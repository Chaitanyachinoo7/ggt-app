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
    read_row
)

session_id = generate_session_id()

#TODO: create a processed file list hash file to save time
def task_process_inbound_lab_reports():
    log_generic(
        type="info", 
        function='task_process_inbound_lab_reports', 
        task_session_id=session_id, 
        info='Begin Processing Inbound Lab Reports')
        
    download_ftp_files()
    parse_csv_files()
    update_test_samples_with_results()
    upload_pdf_lab_reports()

    log_generic(
        type="info", 
        function='task_process_inbound_lab_reports', 
        task_session_id=session_id, 
        info='End Processing Inbound Lab Reports')



def download_ftp_files():
    try:
        hostname=get_config_val('vendors.healthtrackrx.hostname')
        username=get_config_val('vendors.healthtrackrx.username')
        password=get_config_val('vendors.healthtrackrx.password')
        port=get_config_val('vendors.healthtrackrx.port')
        remote_folder=get_config_val('vendors.healthtrackrx.remote_folder')

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
        print(paths)  ##

        directory_list = get_remote_directory_list(ftp_client, paths, remote_folder)
        copy_files_to_local(ftp_client, directory_list, remote_folder)

    except Exception as err:
        log_generic(
            type="error", 
            function='download_ftp_files', 
            task_session_id=session_id, 
            error=err
        )
    finally:
        ftp_client.close()


def get_remote_directory_list(ftp_client, paths, remote_folder):
    directories = []
    for path in paths:
        try:
            ftp_client.chdir(path)
            directories.append(path)
            ftp_client.chdir(remote_folder)
        except:
            #print(path+" is not a dir")
            pass
    print(directories)##
    return directories


def copy_files_to_local(ftp_client, directory_list, remote_folder):
    try:
        download_path=get_config_val('vendors.healthtrackrx.download_path')
    
        for dir in directory_list:
            remote_dir_path = "{}/{}".format(remote_folder, dir)
            print("Scanning dir: {}".format(dir)) ##
            try:
                newpath = "{}/{}".format(download_path, dir)
                if not os.path.exists(newpath):
                    os.makedirs(newpath)

                ftp_client.chdir(remote_dir_path)
                filenames = ftp_client.listdir()

                for filename in filenames:
                    try:
                        local_path = "{}/{}".format(newpath, filename)
                        print("copying {} to {}".format(filename, local_path)) ##
                        if not os.path.exists(local_path):
                            ftp_client.get(filename, local_path)
                    except Exception as err:
                        log_generic(
                            type="error", 
                            function='copy_files_to_local --filelist', 
                            task_session_id=session_id, 
                            error=err
                        )


                #ftp_client.chdir(download_path)
            except Exception as err:
                log_generic(
                            type="error", 
                            function='copy_files_to_local --dirlist', 
                            task_session_id=session_id, 
                            error=err
                        )

    except Exception as err:
        log_generic(
            type="error", 
            function='copy_files_to_local --final', 
            task_session_id=session_id, 
            error=err
        )

    

def parse_csv_files():
    download_path=get_config_val('vendors.healthtrackrx.download_path')
    try:
        files = [f for f in glob.glob("{}/**/*.csv".format(download_path), recursive=True)]
        for filename in files:
            parse_csv_file(filename) #TODO: change the flow to batch insert, currently processes 1 file at a time

    except Exception as err:
        print(err)


def upload_pdf_lab_reports():
    from ggt.lib.storage import (upload_lab_report)
    download_path=get_config_val('vendors.healthtrackrx.download_path')
    try:
        files = [f for f in glob.glob("{}/**/*.pdf".format(download_path), recursive=True)]
        for filename in files:
            try:
                __destination_file_name = destination_file_name(filename)
                if __destination_file_name:
                    upload_lab_report(
                        filename, 
                        __destination_file_name
                    )
            except Exception as err:
                print('Error uploading {}'.format(filename))
            

    except Exception as err:
        print(err)


def destination_file_name(file_path):
    arr = file_path.split('/')
    file_name = arr[len(arr)-1]
    requisition_id = file_name.split('-')[3]
    sql = """
            SELECT order_number 
            FROM ggt_prod.healthtrackrx_inbound_data 
            WHERE requisition_id = %s
            """
    vals = (requisition_id, )
    row = read_row(sql, vals)
    if row is None:
        print('no record for: {}'.format(requisition_id))
        return None

    file_name = '{}.pdf'.format(row['order_number'])
    print(file_name)
    return file_name



def parse_csv_file(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                add_to_inbound_record(row)
            except Exception as err:
                print("err:", err)
            

'''
def add_to_processed_file(file_name):
    print("{} added to processed list".format(file_name))
'''

def add_to_inbound_record(rec):
    print("==>", rec['requisition_id'], rec['order_number'], rec['first_name'], rec['last_name'], rec['DOB'], rec['assay_name'], rec['status'], rec['result'])
    sql = """INSERT INTO healthtrackrx_inbound_data
            (requisition_id, order_number, first_name, last_name, DOB, assay_name, status, result)
        VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE requisition_id=requisition_id"""
    vals = (str(rec['requisition_id']), 
            str(rec['order_number']), 
            str(rec['first_name']), 
            str(rec['last_name']), 
            str(rec['DOB']), 
            str(rec['assay_name']), 
            str(rec['status']), 
            str(rec['result']))
    exec_insert(sql, vals)



def update_test_samples_with_results():
    sql = """UPDATE test_samples
                    INNER JOIN
                healthtrackrx_inbound_data ON (test_samples.id = healthtrackrx_inbound_data.order_number) 
            SET 
                test_samples.lab_result_receive_dt = NOW(),
                test_samples.test_result = (CASE
                    WHEN (healthtrackrx_inbound_data.result = 'Negative') THEN 'neg'
                    WHEN (healthtrackrx_inbound_data.result = 'Positive') THEN 'pos'
                    ELSE 'inconclusive'
                END),
                test_samples.status = 'lab_result_received',
                test_samples.update_dt = NOW()
            WHERE
                test_samples.test_result IS NULL
                    AND test_samples.id = healthtrackrx_inbound_data.order_number
        """
    val = ()
    exec_update(sql, val)



'''

def publish_file_to_gcp_bucket():
    pass


def parse_pdf_files():
    pass

'''
'''
def append_to_processed_file_list():
    pass

'''
