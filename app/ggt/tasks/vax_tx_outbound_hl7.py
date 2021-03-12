import os
import glob
import csv
import datetime
import time
import paramiko
import base64
from PIL import Image

from ggt.lib.utils import (
    get_config_val as cfg,
    log_generic,
    generate_session_id,
    whoami,
    print_header,
    print_ok1,
    print_ok2,
    print_warning,
    print_error,
    print_progress_bar_message
)

from ggt.lib.adapters.s3_adapter import (
    write_text_file
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    read_row,
    read_rows
)

from ggt.models.data_models.hl7 import (
    VaxMessage, MSH, PID, ORC, OBX, RXA, RXR, PD1
)

import ggt.lib.constants as c

session_id = generate_session_id()
local_outbound_file_path = '/Users/suresh/ggt-tasks/outbound'
outbound_file_prefix = 'ggv-tx-test-'


def __get_msh(order):
    return MSH(
        msh_1_field_separator='^~\&',
        msh_2_encoding_characters='',
        msh_3_sending_application='GOGETVAX',
        msh_4_sending_facility='1117823000',
        msh_5_receiving_application='TXImmTrac',
        msh_6_receiving_facility='TxDSHS',
        msh_7_datetime_of_message='{}+0000'.format(format_date(order['today_dt'])),  # dt,
        msh_9_message_type='VXU^V04^VXU_V04',
        msh_10_message_control_id=int(time.time()*1000),
        msh_11_processing_id='P',
        msh_12_version_id='2.5.1'
    )


def __get_pid(order):
    return PID(
        pid_1_set_id=1,
        pid_2_patient_id=order['patient_id'],  # External Code
        pid_3_patient_identifier_list='PI',
        pid_5_patient_name='{}^{}^^^'.format(order['last_name'], order['first_name']),  # Last Name^First Name
        pid_7_date_time_of_birth=order['dob'].replace('-', ''),  # Date of Birth
        pid_8_administrative_sex=order['gender'],  # Gender
        pid_10_race=order['race'],  # Race
        pid_11_patient_address='{}^{}^{}^{}^{}^^^^'.format(order['addr1'], order['addr2'], order['city'], order['st'], order['zip']),  # Address^Address2^City^State^Zip Code
        pid_13_phone_number_home=order['phone_number'].replace('+1', ''),  # Phone
        pid_18_patient_account_number='{}^^^P'.format(order['patient_id']),
        pid_22_ethnic_group=order['ethnicity']  # Ethnicity
    )


def __get_rxa(order):
    return RXA(
        rxa_1_give_sub_id_counter = '0',
        rxa_2_administration_sub_id_counter = '1',
        rxa_3_date_time_start_of_administration = '{}+0000'.format(format_date(order['vax_end_dt'])),
        rxa_4_date_time_end_of_administration = '{}+0000'.format(format_date(order['vax_end_dt'])),
        rxa_5_administered_code = '207^COVID-19^CVX',
        rxa_6_administered_amount = '.5',
        rxa_7_administered_units = 'mL^MilliLiters^UCUM',
        rxa_9_administration_notes = '00^NEW IMMUNIZATIONRECORD^NIP001',
        rxa_11_administered_at_location = '1117823000',
        rxa_15_substance_lot_number = '014M20A', #vaccine LOT number
        rxa_16_substance_expiration_date = '20691231',
        rxa_17_substance_manufacturer_name = 'MOD^MODERNA^MVX',
        rxa_20_completion_status = 'CP',
        rxa_21_action_code_rxa = 'A'
    )

def __get_rxr(order):
    return RXR(
        rxr_1_route = 'C28161^Intramuscular^NCIT',
        rxr_2_administration_site = '{}^HL70163'.format(order['injection_site'])
    )

def __get_pd1(order):
    return PD1(
        pd1_12='TXD',
        pd1_13=order['consent_date']
    )

def __get_orc(order):
    return ORC(
        orc_1_order_control='RE',
        orc_2_placer_order_number=order['client_order_number'],
        orc_3_filler_order_number='{}^{}'.format(order['client_order_number'], 'ROCKWALL'), 
        # Date of Collection
        orc_9_datetime_of_transaction='{}+0000'.format(format_date(order['vax_end_dt'])),
        orc_10_entered_by='GGV',
        orc_17_entering_organization='GGV'
    )


def __get_obx(order):
    if(order['relationship'] is None):
        ins_value = 'V03^No Insurance^HL70064'
    else:
        ins_value = 'V01^Private Pay/Insurance^HL70064'

    obx1 = OBX(
        obx_1_set_id=1,
        obx_2_value_type='CE',
        obx_3_observation_identifier='64994-7^Vaccine Funding Program Eligibility^LN',
        obx_4_observation_sub_id='1',
        obx_5_observation_value=ins_value,
        obx_11_observation_result_status='F',
        obx_17_observation_method='VXC40^Eligibility captured at the immunization level^CDCPHINVS' 
    )

    obx2 = OBX(
        obx_1_set_id=2,
        obx_2_value_type='NM',
        obx_3_observation_identifier='30973-2^Dose Number in Series^LN',
        obx_4_observation_sub_id='1', #This set should be 2, if a CE record exists
        obx_5_observation_value='1',
        obx_6_units='NA^^HL70353',
        obx_11_observation_result_status='F',
        obx_14_datetime_of_the_observation='{}+0000'.format(format_date(order['vax_end_dt']))
    )

    arr = [obx1, obx2]

    return arr

def format_date(dt):
    return str(dt).replace('-','').replace(':','').replace(' ','')

def get_orders_ready_to_transmit(limit=5000):
    sql = """
        SELECT 
            a.id AS id,
            a.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob, '%Y%m%d') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'M'
                WHEN (p.gender = 'female') THEN 'F'
                ELSE 'U'
            END) AS gender,
            a.vax_start_dt,
            a.vax_end_dt,
            a.vax_notes_dt,
            (CASE
                WHEN (a.injection_site = 'right_arm') THEN 'RD^Right Deltoid'
                WHEN (p.race = 'left_arm') THEN 'LD^Left Deltoid'
                ELSE 'RD^Right Deltoid'
            END) AS injection_site,
            a.no_adverse_reactions,
            a.lot_no,
            a.expiration_date,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN '1002-5'
                WHEN (p.race = 'race_asian') THEN '2028-9'
                WHEN (p.race = 'race_black') THEN '2054-5'
                WHEN (p.race = 'race_hawaiian') THEN '2076-8'
                WHEN (p.race = 'race_other') THEN '2131-1'
                WHEN (p.race = 'race_white') THEN '2106-3'
                ELSE 'U'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN '2135-2'
                WHEN (p.ethnicity = 'false') THEN '2186-5'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN '2135-2'
                ELSE 'U'
            END) AS ethnicity,
            REPLACE(p.addr1, ',', '') AS addr1,
            (CASE
                WHEN ISNULL(p.addr2) THEN ''
                ELSE REPLACE(p.addr2, ',', '')
            END) AS addr2,
            REPLACE(p.city, ',', '') AS city,
            REPLACE(p.st, ',', '') AS st,
            REPLACE(p.zip, ',', '') AS zip,
            p.phone_number AS phone_number,
            a.id AS client_order_number,
            l.st AS test_location_st,
            a.sample_collection_location_id,
            DATE_FORMAT(CONVERT_TZ(a.create_dt, '+00:00', '-06:00'),
                    '%Y%m%d') AS consent_date,
            DATE_FORMAT(NOW(), '%Y%m%d%H%m%s') AS today_dt,
            i.relationship
        FROM
            (((appointments a
            JOIN patients p ON (p.id = a.patient_id))
            JOIN locations l ON (a.sample_collection_location_id = l.id))
            JOIN patient_questionnaires q ON (q.id = a.patient_questionnaire_id)
            JOIN patient_insurance_details i ON (i.patient_id = a.patient_id))
        WHERE
            a.group_code LIKE '%ROCKWALL%'
            AND DATE(a.scheduled_dt) = '2021-02-27'
            AND (a.status = 'end_vax'
            OR a.status = 'test_completed')
        LIMIT {}
            """.format(limit)
    return read_rows(sql,)


def create_outbound_files(orders):
    processed_orders = []

    filename = "immitrack.hl7"
    local_file_path = "{}/{}".format(local_outbound_file_path, filename)

    with open(local_file_path, 'w', newline='') as hl7file:

        for order in orders:
            try:
                hl7_message = VaxMessage()
                hl7_message.msh = __get_msh(order)
                hl7_message.pid = __get_pid(order)
                hl7_message.pd1 = __get_pd1(order)
                hl7_message.orc = __get_orc(order)
                hl7_message.rxr = __get_rxr(order)
                hl7_message.rxa = __get_rxa(order)
                hl7_message.obx_list = __get_obx(order)
                
                _str = str(hl7_message).encode("utf-8").decode('utf-8','ignore')
                hl7file.write(_str)

            except Exception as err:
                # print_error(err)
                print_error(
                    'Error generating HL7 for Order ID: {}'.format(order['id']))

    return processed_orders



def process_vax_hl7():
    print('starting...')
    orders = get_orders_ready_to_transmit()
    create_outbound_files(orders)
    print('done')

