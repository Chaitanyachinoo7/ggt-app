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
    whoami
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    read_row,
    read_rows
)

from ggt.models.data_models.hl7 import (
    Message, MSH, MSG, PID, PV1, DG1, ORC, OBR, OBX, IN1, GT1
)

from ggt.lib.storage import (
    get_file_blob
)

import ggt.lib.constants as c

session_id = generate_session_id()
local_outbound_file_path = cfg(
    'vendors.healthtrackrx_outbound.local_outbound_file_path')
outbound_file_prefix = cfg(
    'vendors.healthtrackrx_outbound.outbound_file_prefix')
local_insurance_card_file_path = cfg(
    'vendors.healthtrackrx_outbound.local_insurance_card_file_path')


def task_process_outbound_lab_orders():
    print('\n\n************************************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing outbound HL7 Lab Orders')

    print('looking up ready to transmit orders')
    orders = get_orders_ready_to_transmit()

    upload_insurance_files_from_gstore(orders)

    if len(orders) > 0:
        print('generating outbound file')
        filename, local_file_path = create_outbound_file(orders)

        print('uploading file to FTP server')
        upload_file_to_ftp(filename, local_file_path)

        print('marking records to "with_lab" status')
        update_to_with_lab_status(orders)
    else:
        print('no orders to process')

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')
    print('\n\n************************************************\n\n')


def upload_insurance_files_from_gstore(orders):
    try:
        print('converting insurance image files to PDF')
        file_buffer = []
        for order in orders:
            if order['bill'] == 'DB':
                try:
                    file_path_png = "{}/{}_001.png".format(
                        local_insurance_card_file_path, order['id'])
                    filename = "{}_001.pdf".format(order['id'])
                    file_path_pdf = "{}/{}".format(
                        local_insurance_card_file_path, filename)
                    appointment_id = order['id']
                    blob = get_file_blob('ggt-insurance-cards-prod', '{}.png'.format(appointment_id))
                    if blob:
                        blob.download_to_filename(file_path_png)
                        Image.open(file_path_png).convert(
                            'RGB').save(file_path_pdf)
                        file_buffer.append((filename, file_path_pdf))

                except Exception as err:
                    print(err)

        print('uploading insurance files to FTP')
        upload_file_list_to_ftp(file_buffer)

    except Exception as err:
        print(err)


def get_insurance_photo_base64(appointment_id):
    sql = """
    SELECT 
        q.insurance_photo
    FROM
        (appointments
        JOIN patient_questionnaires q 
            ON (appointments.patient_id = q.patient_id))
    WHERE
        appointments.id = %s
    LIMIT 1
    """
    vals = (appointment_id,)
    row = read_row(sql, vals)
    return row['insurance_photo']


def __get_msh(order):
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    cid = str(int(time.time()))
    return MSH(
        msh_1_field_separator='^~\&',
        msh_2_encoding_characters='',
        msh_3_sending_application='WELLHEALTH',
        msh_4_sending_facility=order['client_site_code'],
        msh_5_receiving_application='AIT',
        msh_6_receiving_facility='AIT',
        msh_7_datetime_of_message=dt,
        msh_9_message_type='ORM^O01',
        msh_10_message_control_id=int(time.time()*1000),
        msh_11_processing_id='P',
        msh_12_version_id='2.3'
    )


def __get_pid(order):
    return PID(
        pid_1_set_id=1,
        pid_2_patient_id=order['patient_id'],  # External Code
        pid_5_patient_name='{}^{}^^^'.format(
            order['last_name'], order['first_name']),  # Last Name^First Name
        pid_7_date_time_of_birth=order['dob'].replace(
            '-', ''),  # Date of Birth
        pid_8_administrative_sex=order['gender'],  # Gender
        pid_10_race=order['race'],  # Race
        pid_11_patient_address='{}^{}^{}^{}^{}^^^^'.format(
            order['addr1'], order['addr2'], order['city'], order['st'], order['zip']),  # Address^Address2^City^State^Zip Code
        pid_13_phone_number_home=order['phone_number'].replace('+1',''),  # Phone
        pid_18_patient_account_number='{}^^^P'.format(order['patient_id']),
        pid_20_drivers_license_number_patient='',
        pid_22_ethnic_group=order['ethnicity']  # Ethnicity
    )


def __get_pv1(order):
    return PV1(
        pv1_1_set_id=1,
        pv1_3_assigned_patient_location='',
        # Physician NPI^Provider Last Name^Provider First name
        pv1_7_attending_doctor='{}^{}^{}'.format(order['physician_npi'], 'Khan', 'Samad'),
        pv1_20_financial_class=order['bill']
    )

'''
def __get_in1(order):
    return IN1(
        in1_1_set_id=1,
        in1_3_insurance_company_id='MMP',
        in1_4_insurance_company_name='MEDICARE MASTER PAYER',
        in1_16_name_of_insured='DOE^JOHN^M',
        in1_17_insureds_relationship_to_patient='01',
        in1_18_insureds_date_of_birth='195208150000',
        in1_19_insureds_address='1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US',
        in1_22_coord_of_ben_priority='1',
        in1_32_billing_status='INSURANCE',
        in1_36_policy_number='8J89UD3HR59',
        in1_43_insureds_administrative_sex='F'
    )
'''

def __get_gt1(order):
    return GT1(
        gt1_1_set_id_gt1='',
        gt1_3_guarantor_name='{}^{}^^^'.format(
            order['last_name'], order['first_name']),  # Last Name^First Name
        gt1_5_guarantor_address='{}^{}^{}^{}^{}^^^^'.format(
            order['addr1'], order['addr2'], order['city'], order['st'], order['zip']),  # Address^Address2^City^State^Zip Code
        gt1_6_guarantor_ph_num_home=order['phone_number'].replace('+1',''),  # Phone
        gt1_7_guarantor_ph_num_business='',
        gt1_8_guarantor_datetime_of_birth=order['dob'].replace(
            '-', ''),  # Date of Birth
        gt1_9_guarantor_administrative_sex=order['gender'],  # Gender
        gt1_11_guarantor_relationship='01'
    )


def __get_orc(order):
    return ORC(
        orc_1_order_control='',
        # Client Order Number^
        orc_2_placer_order_number=order['client_order_number'],
        orc_3_filler_order_number='{}^{}'.format(
            order['sample_code'], 'AIT' if order['sample_code'] else ''),  # Sample Code^Lab Vial Owner
        orc_4_placer_group_number='',
        orc_5_order_status='',
        orc_6_response_flag='',
        orc_7_quantitytiming='',
        orc_8_parent_order='',
        # Date of Collection
        orc_9_datetime_of_transaction=order['date_of_collection'],
        orc_10_entered_by='',
        orc_11_verified_by='',
        # Physician NPI^Provider Last Name^Provider First name
        orc_12_ordering_provider='{}^{}^{}'.format(
            order['physician_npi'], 'Khan', 'Samad'),
    )


def __get_obr(order):
    return OBR(
        obr_1_set_id='1',
        # Client Order Number
        obr_2_placer_order_number=order['client_order_number'],
        obr_3_filler_order_number='{}^{}'.format(
            order['sample_code'], 'AIT' if order['sample_code'] else ''),  # Sample Code^Lab Vial Owner
        obr_4_universal_service_identifier='RESPI507^COVID-19 Test',  # Panel Code^Panel Name
        obr_6_requested_datetime='',  # Date of Collection
        obr_7_observation_datetime=order['date_of_collection'],  # Date of Collection
        obr_15_specimen_source='^^^NASOPHARYNGEAL SWAB',  # Sample Source
        # Physician NPI^Provider Last Name
        obr_16_ordering_provider='{}^{}^{}'.format(order['physician_npi'], 'Khan', 'Samad'),
        obr_17_order_callback_phone_number='4697892595', #WH Phopne number
        obr_21_filler_field_2='^^^^^^'
    )


def __get_dg1(order):
    return DG1(
        dg1_1_set_id_dg1=1,
        # ICD Code
        dg1_3_diagnosis_code_dg1='Z20.828^Contact with and (suspected) exposure to other viral communicable diseases'
    )

'''

OBX-2.1: 'ED' for electronic document
OBX-3.1: something like 'INSURANCE' or 'INSATTACH' to indicate it's the insurance scan
OBX-3.2: name of the file
OBX-5.3: extension (JPEG, PNG, etc.)
OBX-5.4: 'Base64'
OBX-5.5: The base64 encoded string for the image (with no line breaks)
'''
def __get_obx(order):
    obx2 = OBX(
        obx_1_set_id=2,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-1^Is this the patient\'s first COVID-19 test?',
        obx_5_observation_value='{}^{}'.format(
            order['is_first_test'][0:1], order['is_first_test'])
    )

    obx3 = OBX(
        obx_1_set_id=3,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-2^Is the patient employed in healthcare with direct patient contact?',
        obx_5_observation_value='{}^{}'.format(
            order['is_first_test'][0:1], order['is_first_test'])
    )

    obx4 = OBX(
        obx_1_set_id=4,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?',
        obx_5_observation_value='{}^{}'.format(
            order['is_first_test'][0:1], order['is_first_test'])
    )

    obx5 = OBX(
        obx_1_set_id=5,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)',
        obx_5_observation_value=''
    )

    obx6 = OBX(
        obx_1_set_id=6,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-4^Has the patient been hospalized?',
        obx_5_observation_value='{}^{}'.format(
            order['is_hospitalized'][0:1], order['is_hospitalized'])
    )

    obx7 = OBX(
        obx_1_set_id=7,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-5^Has the patient been hospalized in the ICU?',
        obx_5_observation_value='{}^{}'.format(
            order['is_in_icu'][0:1], order['is_in_icu'])
    )
    obx8 = OBX(
        obx_1_set_id=8,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?',
        obx_5_observation_value='{}^{}'.format(
            order['is_congregate_resident'][0:1], order['is_congregate_resident'])
    )

    obx9 = OBX(
        obx_1_set_id=9,
        obx_2_value_type='ST',
        obx_3_observation_identifier='COVID-PT-7^Is the patient pregnant?',
        obx_5_observation_value='{}^{}'.format(
            order['is_pregnant'][0:1], order['is_pregnant'])
    )

    obx10 = None
    if order['bill'] == 'DB':
        try:
            blob = get_file_blob('ggt-insurance-cards-prod', '{}.png'.format(order['id']))
            if blob:
                content = blob.download_as_string()
                b64content = base64.b64encode(content)

                obx10 = OBX(
                    obx_1_set_id=10,
                    obx_2_value_type='ED',
                    obx_3_observation_identifier='INSURANCE^{}.png'.format(order['client_order_number']),
                    obx_5_observation_value='^^PNG^Base64^{}'.format(b64content)
                )
        except Exception as err:
            print(err)

    arr = [obx2, obx3, obx4, obx5, obx6, obx7, obx8, obx9, obx10]

    return arr


def create_outbound_files(orders):
    for order in orders:
        
        hl7_message = Message()
        hl7_message.msh = __get_msh(order)
        hl7_message.pid = __get_pid(order)
        hl7_message.pv1 = __get_pv1(order)
        hl7_message.orc = __get_orc(order)
        hl7_message.obr = __get_obr(order)
        hl7_message.dg1 = __get_dg1(order)
        hl7_message.obx_list = __get_obx(order)

        if order['bill'] == 'DB':
            hl7_message.gt1 = __get_gt1(order)
        
        filename = "{}-{}.hl7".format(
            outbound_file_prefix,
            order['id']
        )
        local_file_path = "{}/{}".format(local_outbound_file_path, filename)
        
        with open(local_file_path, 'w', newline='') as hl7file:
            _str = str(hl7_message).encode("utf-8").decode('utf-8','ignore')
            hl7file.write(_str)


def get_orders_ready_to_transmit():
    sql = """
        SELECT 
            t.id AS id,
            t.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob, '%Y%m%d') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'M'
                WHEN (p.gender = 'female') THEN 'F'
                ELSE 'Unknown'
            END) AS gender,
            (CASE
                WHEN (t.sample_collection_start_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_start_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y%m%d')
                WHEN (t.sample_collection_end_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_end_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y%m%d')
                WHEN (t.pre_ship_label_scan_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.pre_ship_label_scan_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y%m%d')
                ELSE DATE_FORMAT(CONVERT_TZ(NOW(),
                            '+00:00',
                            '-06:00'),
                    '%Y%m%d')
            END) AS date_of_collection,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN '1002-5'
                WHEN (p.race = 'race_asian') THEN '2028-9'
                WHEN (p.race = 'race_black') THEN '2054-5'
                WHEN (p.race = 'race_hawaiian') THEN '2076-8'
                WHEN (p.race = 'race_other') THEN '2131-1'
                WHEN (p.race = 'race_white') THEN '2106-3'
                ELSE 'Unknown'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN '2135-2'
                WHEN (p.ethnicity = 'false') THEN '2186-5'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN '2135-2'
                ELSE 'Unknown'
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
            (CASE
                WHEN (l.billing_type = 'insurance') THEN 'WELLHLD'
                ELSE 'WELLHLTX'
            END) AS client_site_code,
            (CASE
                WHEN (l.billing_type = 'insurance') THEN '1780944496'
                ELSE '22244887999'
            END) AS physician_npi,
            (CASE
                WHEN
                    ((l.billing_type = 'insurance')
                        AND (q.has_insurance_photo = 1))
                THEN
                    'DB'
                WHEN
                    ((l.billing_type = 'insurance')
                        AND (q.has_insurance_photo <> 1))
                THEN
                    'SP'
                ELSE 'CB'
            END) AS bill,
            t.id AS client_order_number,
            t.vial_id AS sample_code,
            (CASE
                WHEN (l.st = 'SC') THEN 'Pod 1 South Carolina'
                ELSE ''
            END) AS collected_by,
            'Respiratory' AS sample_type,
            (CASE
                WHEN (l.test_type_offered = 'oral') THEN 'MOUTH'
                ELSE 'Nasopharynx'
            END) AS sample_source,
            'RESPI507' AS panel_code,
            'COVID-19 Coronavirus (SARS-CoV-2)' AS panel_name,
            'Unknown' AS is_first_test,
            'Unknown' AS is_healthcare_employee,
            'Unknown' AS is_cdc_symptomatic,
            'Unknown' AS is_hospitalized,
            'Unknown' AS is_in_icu,
            'Unknown' AS is_congregate_resident,
            'Unknown' AS is_pregnant
        FROM
            (((test_samples t
            JOIN patients p ON ((t.patient_id = p.id)))
            JOIN locations l ON ((t.sample_collection_location_id = l.id)))
            JOIN patient_questionnaires q ON ((p.id = q.patient_id)))
        WHERE
            (t.status = 'ready_to_tx')
        LIMIT 100
            """
    return read_rows(sql,)


def upload_file_list_to_ftp(file_list):
    try:
        hostname = cfg('vendors.healthtrackrx_outbound.hostname')
        username = cfg('vendors.healthtrackrx_outbound.username')
        password = cfg('vendors.healthtrackrx_outbound.password')
        port = cfg('vendors.healthtrackrx_outbound.port')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()

        for f in file_list:
            filename = f[0]
            local_file_path = f[1]
            remotepath = "{}/{}".format('', filename)
            ftp_client.put(local_file_path, remotepath)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def upload_file_to_ftp(filename, local_file_path):
    try:
        hostname = cfg('vendors.healthtrackrx_outbound.hostname')
        username = cfg('vendors.healthtrackrx_outbound.username')
        password = cfg('vendors.healthtrackrx_outbound.password')
        port = cfg('vendors.healthtrackrx_outbound.port')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()

        remotepath = "{}/{}".format('', filename)
        ftp_client.put(local_file_path, remotepath)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def update_to_with_lab_status(orders):
    list_of_ids = []
    for order in orders:
        list_of_ids.append(order['client_order_number'])

    format_strings = ','.join(['%s'] * len(list_of_ids))
    sql = """
        UPDATE test_samples 
        SET 
            status = 'with_lab',
            update_dt = NOW(),
            lab_electronic_submission_dt = NOW()
        WHERE
            id IN (%s)
        """ % format_strings

    exec_update(sql, tuple(list_of_ids))
