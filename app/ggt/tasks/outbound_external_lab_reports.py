import csv
import datetime

import paramiko

import ggt.lib.constants as c
from ggt.lib.db import (
    exec_update,
    read_rows
)
from ggt.lib.utils import (
    get_config_val as cfg,
    log_generic,
    generate_session_id,
    whoami
)

session_id = generate_session_id()
local_outbound_file_path = '/tmp'

def task_process_outbound_lab_reports():
    print('\n\n************************************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing outbound External Lab Reports')

    print('looking up ready to transmit reports')
    reports = await get_reports_ready_to_transmit()

    if len(reports) > 0:
        print('generating outbound file')
        filename, local_file_path = await create_outbound_file(reports)

        print('uploading file to FTP server')
        if await upload_file_to_ftp(filename, local_file_path):
            print('marking records to "with_lab" status')
            if await update_to_with_lab_status(reports):
                print('publishing report to KDHE completed')
        else:
            print('Error publishing report to KDHE')
    else:
        print('no orders to process')

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')
    print('\n\n************************************************\n\n')


def create_outbound_file(reports):
    filename = "ggt-outbound-{}.csv".format(
        datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    )
    local_file_path = "{}/{}".format(local_outbound_file_path, filename)

    with open(local_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(
            __get_header_row()
        )

        for order in reports:
            writer.writerow(
                __get_formatted_row(order)
            )

    return filename, local_file_path


def __get_header_row():
    return [
        'Lab',
        'Patient_Last_Name',
        'Patient_First_Name',
        'Patient_DOB',
        'Patient_Gender',
        'Patient_Address_1',
        'Patient_Address_2',
        'Patient_City',
        'Patient_State',
        'Patient_Zip',
        'Patient_Area_Code',
        'Patient_Phone',
        'Ordering_Facility',
        'Ordering_Facility_Address_1',
        'Ordering_Facility_Address_2',
        'Ordering_Facility_City',
        'Ordering_Facility_State',
        'Ordering_Facility_Zip',
        'Ordering_Facility_Area_Code',
        'Ordering_Facility_Phone',
        'Ordering_Provider_LName',
        'Ordering_Provider_Fname',
        'Accession_Number',
        'Specimen_Collection_Date',
        'Specimen_Source',
        'Test_Date',
        'Test_Performed',
        'Result',
        'Race']


def __get_formatted_row(report):
    formatted_row = []
    try:
        formatted_row = [
            report['Lab'],
            report['Patient_Last_Name'],
            report['Patient_First_Name'],
            report['Patient_DOB'],
            report['Patient_Gender'],
            report['Patient_Address_1'],
            report['Patient_Address_2'],
            report['Patient_City'],
            report['Patient_State'],
            report['Patient_Zip'],
            report['Patient_Area_Code'],
            report['Patient_Phone'],
            report['Ordering_Facility'],
            report['Ordering_Facility_Address_1'],
            report['Ordering_Facility_Address_2'],
            report['Ordering_Facility_City'],
            report['Ordering_Facility_State'],
            report['Ordering_Facility_Zip'],
            report['Ordering_Facility_Area_Code'],
            report['Ordering_Facility_Phone'],
            report['Ordering_Provider_LName'],
            report['Ordering_Provider_Fname'],
            report['Accession_Number'],
            report['Specimen_Collection_Date'],
            report['Specimen_Source'],
            report['Test_Date'],
            report['Test_Performed'],
            report['Result'],
            report['Race']
        ]

    except Exception as err:
        print(err)

    return formatted_row


def get_reports_ready_to_transmit():
    sql = """SELECT 
    k.Lab,
    k.Patient_Last_Name,
    k.Patient_First_Name,
    k.Patient_DOB,
    k.Patient_Gender,
    k.Patient_Address_1,
    k.Patient_Address_2,
    k.Patient_City,
    k.Patient_State,
    k.Patient_Zip,
    k.Patient_Area_Code,
    k.Patient_Phone,
    k.Ordering_Facility,
    k.Ordering_Facility_Address_1,
    k.Ordering_Facility_Address_2,
    k.Ordering_Facility_City,
    k.Ordering_Facility_State,
    k.Ordering_Facility_Zip,
    k.Ordering_Facility_Area_Code,
    k.Ordering_Facility_Phone,
    k.Ordering_Provider_LName,
    k.Ordering_Provider_Fname,
    k.Accession_Number,
    k.Specimen_Collection_Date,
    k.Specimen_Source,
    k.Test_Date,
    k.Test_Performed,
    k.Result,
    k.Race,
    k.Ethnicity,
    k.status
FROM
    outbound_kdhe_epitrax k
WHERE
    k.status = 'pending'"""
    return read_rows(sql, )


def upload_file_to_ftp(filename, local_file_path):
    status = False
    try:
        hostname = cfg('vendors.kdhe.hostname')
        username = cfg('vendors.kdhe.username')
        password = cfg('vendors.kdhe.password')
        port = cfg('vendors.kdhe.port')
        path = cfg('vendors.kdhe.path')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()

        remotepath = "{}/{}".format(path, filename)
        ftp_client.put(local_file_path, remotepath)
        status = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()
    
    return status


def list_ftp_files():
    hostname = cfg('vendors.kdhe.hostname')
    username = cfg('vendors.kdhe.username')
    password = cfg('vendors.kdhe.password')
    port = cfg('vendors.kdhe.port')
    remote_folder = cfg('vendors.kdhe.path')
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()
        ftp_client.chdir(remote_folder)

        paths = ftp_client.listdir()
        print('\n\n*********************10***************************\n\n')
        print(paths)
        return paths
        print('\n\n*********************11***************************\n\n')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def delete_ftp_files():
    hostname = cfg('vendors.kdhe.hostname')
    username = cfg('vendors.kdhe.username')
    password = cfg('vendors.kdhe.password')
    port = cfg('vendors.kdhe.port')
    remote_folder = cfg('vendors.kdhe.path')
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()
        ftp_client.chdir(remote_folder)

        paths = ftp_client.listdir()
        print('\n\n*********************100***************************\n\n')
        for file in paths:
            print(file)
            remotepath = "{}/{}".format(remote_folder, file)
            print(remotepath)
            ftp_client.remove(remotepath)
        print('\n\n*********************110***************************\n\n')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def update_to_with_lab_status(reports):
    list_of_ids = []
    for report in reports:
        list_of_ids.append(report['Accession_Number'])

    format_strings = ','.join(['%s'] * len(list_of_ids))
    sql = """
        UPDATE outbound_kdhe_epitrax 
        SET 
            status = 'sent',
            update_dt = NOW()
        WHERE
            Accession_Number IN (%s)
        """ % format_strings

    return exec_update(sql, tuple(list_of_ids))
