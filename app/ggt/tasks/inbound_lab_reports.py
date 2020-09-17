import os
import glob
import csv
import datetime
import time
import paramiko
import itertools
import shutil
from pathlib import Path


from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_batch_execute,
    exec_update,
    read_row,
    read_rows
)

from ggt.lib.storage import (
    file_exists_in_all_inbound_files,
    upload_lab_report,
    upload_to_all_inbound_files
)

from ggt.models.data_models.tasks_local_cache import (
    init_local_cache,
    add_to_lab_test_records_cache,
    get_all_lab_records_from_cache,
    add_to_all_inbound_files_cache,
    file_exists_in_all_inbound_files_cache,
    get_order_number_by_requisition_id,
    add_to_files_in_remote_storage_cache,
    file_exists_in_files_in_remote_storage_cache
)


session_id = generate_session_id()

hostname=get_config_val('vendors.healthtrackrx.hostname')
username=get_config_val('vendors.healthtrackrx.username')
password=get_config_val('vendors.healthtrackrx.password')
port=get_config_val('vendors.healthtrackrx.port')
remote_downloads_folder=get_config_val('vendors.healthtrackrx.remote_downloads_folder')

local_backups_path=get_config_val('vendors.healthtrackrx.local_backups_path')
local_download_path=get_config_val('vendors.healthtrackrx.local_download_path')

#----What this does----
#Delete/move files at the download directory
#get a list of remote files
#iterate over the files
#       if file exists in cache, skip. Else download. Add name to cache
#--
#parse CSV files, add all records into the labrecords table in cache (insert ignore)
#Take all the records in the cache and add to Mysql (results are available for reporting)
#Scan the download folder and upload all the files to inboundfiles folder in GCP
#Copy renamed PDF lab reports to GCP
def task_process_inbound_lab_reports():
    start = time.time()
    print('\n\n******************Inbound file processing [Start]******************************\n\n')
    log_generic(
        type="info", 
        function='task_process_inbound_lab_reports', 
        task_session_id=session_id, 
        info='Begin Processing Inbound Lab Reports')

    init_local_cache()  
    load_data_from_remote_db_to_cache() 

    #clean_downloads_folder()
    download_ftp_files()
    parse_csv_files()
        
    add_to_healthtrackrx_inbound_data_table()
    update_test_samples_with_results()
    upload_pdf_lab_reports()
    upload_all_inbound_files_to_central_storage() 

    log_generic(
        type="info", 
        function='task_process_inbound_lab_reports', 
        task_session_id=session_id, 
        info='End Processing Inbound Lab Reports')

    print('\n\n****************** COMPLETED ******************************\nElapsed Time: {}\n'.format(time.time() - start))

    
'''
def init_ftp_connection():
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
        directory_list = get_remote_directory_list(ftp_client, paths, remote_folder)
        return ftp_client, directory_list, remote_folder


    except Exception as err:
        log_generic(
            type="error", 
            function='download_ftp_files', 
            task_session_id=session_id, 
            error=err
        )
    finally:
        ftp_client.close()
'''

def clean_downloads_folder():
    print('cleaning up downloads folder')
    try:
        files = glob.glob("{}/*".format(local_download_path))
        for f in files:
            os.remove(f)

    except Exception as err:
        log_generic(
            type="error", 
            function='clean_downloads_folder',
            error=err
        )


def download_ftp_files():
    print('downloading files from FTP')
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
        ftp_client.chdir(remote_downloads_folder)

        paths = ftp_client.listdir()
        directory_list = get_remote_directory_list(ftp_client, paths, remote_downloads_folder)
        copy_files_to_local(ftp_client, directory_list, remote_downloads_folder)

    except Exception as err:
        log_generic(
            type="error", 
            function='download_ftp_files', 
            task_session_id=session_id, 
            error=err
        )
    finally:
        ftp_client.close()




def copy_files_to_local(ftp_client, directory_list, remote_folder):
    print('copying files from remote to local')
    try:
        for dir in directory_list:
            remote_dir_path = "{}/{}".format(remote_folder, dir)
            print("Scanning dir: {}".format(remote_dir_path)) ##
            total_files = 0
            cache_hits = 0
            cache_misses = 0
            download_errors = 0
            try:
                newpath = "{}/{}".format(local_download_path, remote_dir_path)
                if not os.path.exists(newpath):
                    os.makedirs(newpath)

                dir_list, file_list = get_remote_directories_and_files(ftp_client, remote_dir_path)

                for filename in file_list:
                    total_files+=1
                    try:
                        if file_exists_in_all_inbound_files_cache(filename):
                            #print('{} exists in cache. -- skipping.'.format(filename))
                            cache_hits+=1
                        else:    
                            cache_misses+=1
                            local_path = "{}/{}".format(newpath, filename).replace('//','/')

                            print("copying {} to {}".format(filename, local_path)) ##
                            ftp_client.get(filename, local_path)
                            if add_to_all_inbound_files_cache(filename):
                                old_path = '{}/{}'.format(remote_dir_path, filename)
                                new_path = '{}{}/{}'.format('/backups', remote_dir_path, filename)
                                ftp_client.rename(old_path, new_path)

                    except Exception as err:
                        download_errors+=1
                        log_generic(
                            type="error", 
                            function='copy_files_to_local --filelist', 
                            task_session_id=session_id, 
                            error=err
                        )

            except Exception as err:
                log_generic(
                            type="error", 
                            function='copy_files_to_local --dirlist', 
                            task_session_id=session_id, 
                            error=err
                        )
            finally:
                print('total_files: ', total_files)
                print('cache_hits: ', cache_hits)
                print('cache_misses: ', cache_misses)
                print('download_errors: ', download_errors)

    except Exception as err:
        log_generic(
            type="error", 
            function='copy_files_to_local --final', 
            task_session_id=session_id, 
            error=err
        )


def get_remote_directories_and_files(ftp_client, remote_folder):
    file_list = []
    dir_list = []

    try:
        ftp_client.chdir(remote_folder)
        resources = ftp_client.listdir()

        for resource in resources:
            lstatout=str(ftp_client.lstat(resource)).split()[0]
            if 'd' in lstatout:
                dir_list.append(resource)
            else:
                file_list.append(resource)
    except Exception as err:
        log_generic(
            type="error", 
            function='get_remote_directories_and_files --final', 
            remote_folder=remote_folder, 
            error=err
        )
    
    return dir_list, file_list


def get_remote_directory_list(ftp_client, paths, remote_folder):
    directories = ['']
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

def parse_csv_files():
    print('parsing CSV files')
    try:
        files = [f for f in glob.glob("{}/**/**/*.csv".format(local_download_path), recursive=True)]
        for filename in files:
            parse_csv_file(filename)

    except Exception as err:
        print(err)


def parse_csv_file(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(lower_first(csvfile))
        for row in reader:
            try:
                add_to_lab_test_records_cache(row)
            except Exception as err:
                print("err:", err)


def load_data_from_remote_db_to_cache():
    print('loading data from remote db to local cache')
    sql = """
        SELECT * 
        FROM healthtrackrx_inbound_data 
        """
    rows = read_rows(sql)
    
    for row in rows:
        add_to_lab_test_records_cache(row)
    
    print('sync completed')


def upload_pdf_lab_reports():
    print('uploading PDF lab reports')
    try:
        files = [f for f in glob.glob("{}/**/**/*.pdf".format(local_download_path), recursive=True)]
        for filename in files:
            try:
                __destination_filename = generate_destination_filename(filename)
                shutil.copyfile(filename,'{}/{}'.format(local_backups_path, __destination_filename))
                if __destination_filename:
                    if file_exists_in_files_in_remote_storage_cache(__destination_filename):
                        #print('cache hit: ', __destination_filename)
                        pass
                    else:
                        upload_status = upload_lab_report(
                            filename, 
                            __destination_filename
                        )
                        if upload_status is None:
                            print('pdf_lab_report - Error Uploading.... {} ==> {}'.format(filename, __destination_filename))
                        elif upload_status:
                            print('pdf_lab_report - upload success {} ==> {}'.format(filename, __destination_filename))
                        else:
                            print('pdf_lab_report exists at destination... adding to local cache: {} ==> {}'.format(filename, __destination_filename))
                            add_to_files_in_remote_storage_cache(__destination_filename)
            except Exception as err:
                print('Error uploading {}'.format(filename))
            

    except Exception as err:
        print(err)


def upload_all_inbound_files_to_central_storage():
    print('uploading all inbound raw files to remote storage')
    try:
        files = [f for f in glob.glob("{}/**/*".format(local_download_path), recursive=True)]
        for file_path in files:
            filename = extract_filename(file_path)
            try:
                if file_exists_in_files_in_remote_storage_cache(filename):
                    #print('cache hit: ', filename)
                    pass
                else:
                    upload_status = upload_to_all_inbound_files(file_path, filename)
                    if upload_status is None:
                        print('Error Uploading.... {}'.format(filename))
                    elif upload_status:
                        print('upload success {}'.format(filename))
                    else:
                        print('file exsits... adding to local cache: {}'.format(filename))
                        add_to_files_in_remote_storage_cache(filename)
            except Exception as err:
                print('Error uploading {}'.format(filename))
            

    except Exception as err:
        print(err)



def generate_destination_filename(file_path):
    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]
        requisition_id = filename.split('-')[3]
        
        order_number = get_order_number_by_requisition_id(requisition_id)
        if order_number:
            filename = '{}.pdf'.format(order_number)
            return filename

    except Exception as err:
        print("err:", err)

    print('Requisition Not found - ID: {}'.format(requisition_id))
    append_to_processing_summary('{} - no record found'.format(requisition_id))
    return None
    


def append_to_processing_summary(txt):
    f = open("/tmp/ggt-tasks/process_summary/ggt-inbound-processing-summary.txt", "a")  # append mode 
    f.write(txt + "\n") 
    f.close() 


def add_to_healthtrackrx_inbound_data_table():
    print('syncing inbound cached records to remote DB')
    rows = get_all_lab_records_from_cache()
    try:
        sql = """
            INSERT INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        exec_batch_execute(sql, rows)

    except Exception as err:
        print("err:", err)


def update_test_samples_with_results():
    print('updating test results in remote DB')
    sql = """
        UPDATE test_samples
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
    vals = ()
    exec_update(sql, vals)




def extract_filename(file_path):
    arr = file_path.split('/')
    filename = arr[len(arr)-1]
    return filename

def lower_first(iterator):
    return itertools.chain([next(iterator).lower()], iterator)

'''
TODO: replace file scanning with this new method

from pathlib import Path

for path in Path('src').rglob('*.c'):
    print(path.name)
'''