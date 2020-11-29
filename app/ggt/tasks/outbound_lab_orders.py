import os
import glob
import csv
import datetime
import paramiko
import base64
from PIL import Image

from ggt.lib.utils import (
    get_config_val,
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

from ggt.lib.storage import (
    get_file_blob
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

session_id = generate_session_id()
local_outbound_file_path = get_config_val('vendors.healthtrackrx.local_outbound_file_path')
outbound_file_prefix = get_config_val('vendors.healthtrackrx.outbound_file_prefix')
local_insurance_card_file_path = get_config_val('vendors.healthtrackrx.local_insurance_card_file_path')

async def task_process_outbound_lab_orders():
    print('\n\n************************************************\n\n')
    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing outbound Lab Reports')

    print('looking up ready to transmit orders')
    orders = get_orders_ready_to_transmit()

    #upload_insurance_files_from_db(orders)
    await upload_insurance_files_from_gstore(orders)

    if len(orders)>0:
        print('generating outbound file')
        filename, local_file_path = create_outbound_file(orders)

        print('uploading file to FTP server')
        upload_file_to_ftp(filename, local_file_path)

        print('marking records to "with_lab" status')
        update_to_with_lab_status(orders)
    else:
        print('no orders to process')


    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')
    print('\n\n************************************************\n\n')


def upload_insurance_files_from_db(orders):
    try:
        print('converting insurance image files to PDF')
        file_buffer = []
        for order in orders:
            if order['bill'] == 'Insurance Attached':
                file_path_png = "{}/{}_001.png".format(local_insurance_card_file_path, order['id'])
                filename = "{}_001.pdf".format(order['id'])
                file_path_pdf = "{}/{}".format(local_insurance_card_file_path, filename)

                insurance_photo_str = get_insurance_photo_base64(order['id'])
                base64string = insurance_photo_str.split(",")[1]

                with open(file_path_png, "wb") as fh:
                    fh.write(base64.b64decode(base64string + "=="))

                Image.open(file_path_png).convert('RGB').save(file_path_pdf)
                file_buffer.append((filename, file_path_pdf))
        
        print('uploading insurance files to FTP')
        upload_file_list_to_ftp(file_buffer)

    except Exception as err:
        print(err)


async def upload_insurance_files_from_gstore(orders):
    try:
        print('converting insurance image files to PDF')
        file_buffer = []
        for order in orders:
            if order['bill'] == 'Insurance Attached':
                try:
                    file_path_png = "{}/{}_001.png".format(local_insurance_card_file_path, order['id'])
                    filename = "{}_001.pdf".format(order['id'])
                    file_path_pdf = "{}/{}".format(local_insurance_card_file_path, filename)
                    appointment_id = order['id']
                    blob = await get_file_blob('ggt-insurance-cards-prod', '{}.png'.format(appointment_id))
                    if blob:
                        blob.download_to_filename(file_path_png)
                        Image.open(file_path_png).convert('RGB').save(file_path_pdf)
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


def create_outbound_file(orders):
    filename = "{}-{}.csv".format(
        outbound_file_prefix,
        datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    )
    local_file_path = "{}/{}".format(local_outbound_file_path, filename)

    with open(local_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(
                __get_header_row()
            )

        for order in orders:
            writer.writerow(
                __get_formatted_row(order)
            )

    return filename, local_file_path


def __get_header_row():
    return [
        'External Code',
        'First Name',
        'Last Name',
        'Date of Birth',
        'Gender',
        'Date of Collection',
        'Race',
        'Ethnicity',
        'Address',
        'Address2',
        'City',
        'State',
        'Zip Code',
        'Phone',
        'Client Site Code',
        'Physician NPI',
        'Bill',
        'Client Order Number',
        'Sample Code',
        'Collected By',
        'Sample Type',
        'Sample Source',
        'Panel Code',
        'Panel Name',
        'First Test?',
        'Employed in healthcare?',
        'Symptomatic as defined by CDC?',
        'Hospitalized?',
        'ICU?',
        'Resident in a congregate care setting?',
        'Pregnant?']


def __get_formatted_row(order):
    formatted_row = []
    try:
        formatted_row = [
        order['patient_id'],
        order['first_name'],
        order['last_name'],
        order['dob'],
        order['gender'],
        order['date_of_collection'],
        order['race'],
        order['ethnicity'],
        order['addr1'],
        order['addr2'],
        order['city'],
        order['st'],
        order['zip'],
        order['phone_number'],
        order['client_site_code'],
        order['physician_npi'],
        order['bill'],
        order['client_order_number'],
        order['sample_code'],
        order['collected_by'],
        order['sample_type'],
        order['sample_source'],
        order['panel_code'],
        order['panel_name'],
        order['is_first_test'],
        order['is_healthcare_employee'],
        order['is_cdc_symptomatic'],
        order['is_hospitalized'],
        order['is_in_icu'],
        order['is_congregate_resident'],
        order['is_pregnant']
    ]
    except Exception as err:
        print(err)

    return formatted_row


def get_orders_ready_to_transmit():
    '''
    call sync_test_completed_status_where_timestamps_exist;	
    call create_test_samples_records_for_completed_appointments;

    sql = """
        UPDATE appointments 
        SET 
            status = 'test_completed'
        WHERE
            status <> 'test_completed'
                AND test_start_dt IS NOT NULL
                AND id <> 0;
        END
    """


    sql = """
        INSERT ignore INTO test_samples
        (
            id,
            appointment_id,
            group_code,
            patient_id,
            patient_questionnaire_id,
            sample_collection_location_id,
            sample_collection_start_dt,
            sample_collection_end_dt,
            status
        )
        SELECT 
            id,
            id,
            group_code,
            patient_id,
            patient_questionnaire_id,
            location_id,
            test_start_dt,
            test_end_dt,
            'ready_to_tx' AS status
        FROM
            appointments
        WHERE
            status = 'test_completed';
    """
    '''
    sql = """
        SELECT 
            t.id AS id,
            t.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob, '%m/%d/%Y') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'Male'
                WHEN (p.gender = 'female') THEN 'Female'
                ELSE 'Unknown'
            END) AS gender,
            (CASE
                WHEN (t.sample_collection_start_dt IS NOT NULL) THEN DATE_FORMAT(t.sample_collection_start_dt, '%m/%d/%y')
                WHEN (t.sample_collection_end_dt IS NOT NULL) THEN DATE_FORMAT(t.sample_collection_end_dt, '%m/%d/%y')
                WHEN (t.pre_ship_label_scan_dt IS NOT NULL) THEN DATE_FORMAT(t.pre_ship_label_scan_dt, '%m/%d/%y')
                ELSE DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '-06:00'),
                        '%m/%d/%y')
            END) AS date_of_collection,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
                WHEN (p.race = 'race_asian') THEN 'Asian'
                WHEN (p.race = 'race_black') THEN 'Black or African American'
                WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
                WHEN (p.race = 'race_other') THEN 'Other'
                WHEN (p.race = 'race_white') THEN 'White'
                ELSE 'Unknown'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
                WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
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
                    'Insurance Attached'
                WHEN
                    ((l.billing_type = 'insurance')
                        AND (q.has_insurance_photo <> 1))
                THEN
                    'Self-Pay'
                ELSE 'Client Bill'
            END) AS bill,
            t.id AS client_order_number,
            '' AS sample_code,
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
            """
    return read_rows(sql,)


def upload_file_list_to_ftp(file_list):
    try:
        hostname = get_config_val('vendors.healthtrackrx.hostname')
        username = get_config_val('vendors.healthtrackrx.username')
        password = get_config_val('vendors.healthtrackrx.password')
        port = get_config_val('vendors.healthtrackrx.port')

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
            type=ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()



def upload_file_to_ftp(filename, local_file_path):
    try:
        hostname = get_config_val('vendors.healthtrackrx.hostname')
        username = get_config_val('vendors.healthtrackrx.username')
        password = get_config_val('vendors.healthtrackrx.password')
        port = get_config_val('vendors.healthtrackrx.port')

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
            type=ERROR,
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
