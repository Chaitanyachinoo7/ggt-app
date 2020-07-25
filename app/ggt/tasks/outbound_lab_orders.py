import os
import glob
import csv
import datetime
import paramiko

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_row,
    read_rows
)

session_id = generate_session_id()
local_outbound_file_path = get_config_val('vendors.healthtrackrx.local_outbound_file_path')
outbound_file_prefix = get_config_val('vendors.healthtrackrx.outbound_file_prefix')


def task_process_outbound_lab_orders():
    log_generic(
        type="info",
        function='task_process_outbound_lab_orders',
        task_session_id=session_id,
        info='Begin Processing outbound Lab Reports')

    print('************* looking up ready to transmit orders')
    orders = get_orders_ready_to_transmit()

    if len(orders)>0:
        print('************* generating outbound file')
        file_name, local_file_path = create_outbound_file(orders)

        print('************* uploading file to FTP server')
        upload_files_to_ftp(file_name, local_file_path)

        print('************* marking records to "with_lab" status')
        update_to_with_lab_status(orders)
    else:
        print('no orders to process')
        
    print('************* completed')

    log_generic(
        type="info",
        function='task_process_outbound_lab_orders',
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')


def create_outbound_file(orders):
    file_name = "{}-{}.csv".format(
        outbound_file_prefix,
        datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    )
    local_file_path = "{}/{}".format(local_outbound_file_path, file_name)

    with open(local_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(
                __get_header_row()
            )

        for order in orders:
            writer.writerow(
                __get_formatted_row(order)
            )

    return file_name, local_file_path


def __get_header_row():
    return [
        'External Code',
        'First Name',
        'Last Name',
        'Date of Birth',
        'Gender',
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
        'Sample Type',
        'Sample Source',
        'Date of Collection',
        'Panel Code',
        'Panel Name']


def __get_formatted_row(order):
    return [
        order['patient_id'],
        order['first_name'],
        order['last_name'],
        order['dob'],
        order['gender'],
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
        order['sample_type'],
        order['sample_source'],
        order['date_of_collection'],
        order['panel_code'],
        order['panel_name']
    ]


def get_orders_ready_to_transmit():
    sql = """
        SELECT 
            t.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob,'%m/%d/%Y') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'Male'
                WHEN (p.gender = 'female') THEN 'Female'
                ELSE 'Unknown'
            END) AS gender,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
                WHEN (p.race = 'race_asian') THEN 'Asian'
                WHEN (p.race = 'race_black') THEN 'Black or African American'
                WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
                WHEN (p.race = 'race_other') THEN 'Other'
                WHEN (p.race = 'race_white') THEN 'Caucasian'
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
            'WELLHLTX' AS client_site_code,
            '22244887999' AS physician_npi,
            'Client Bill' AS bill,
            t.id AS client_order_number,
            'Respiratory' AS sample_type,
            'Nasopharynx' AS sample_source,
            DATE_FORMAT(t.sample_collection_start_dt,
                    '%m/%d/%y') AS date_of_collection,
            'RESPI507' AS panel_code,
            'COVID-19 Coronavirus (SARS-CoV-2)' AS panel_name
        FROM
            (test_samples t
            JOIN patients p ON ((t.patient_id = p.id)))
        WHERE
            (t.status = 'ready_to_tx')
            """
    return read_rows(sql,)


def upload_files_to_ftp(file_name, local_file_path):
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

        remotepath = "{}/{}".format('', file_name)
        ftp_client.put(local_file_path, remotepath)

    except Exception as err:
        log_generic(
            type="error",
            function='upload_files_to_ftp',
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
        UPDATE ggt_prod.test_samples 
        SET 
            status = 'with_lab',
            update_dt = NOW(),
            lab_electronic_submission_dt = NOW()
        WHERE
            id IN (%s)
        """ % format_strings
        
    exec_update(sql, tuple(list_of_ids))



