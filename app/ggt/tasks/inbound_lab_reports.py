import os
import os.path
from os import path
import glob
import csv
import datetime
import time
import paramiko
import itertools
import shutil
from pathlib import Path


from ggt.lib.utils import (
    get_config_val as cfg,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    exec_batch_execute,
    replica_read_row,
    replica_read_rows
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
    file_exists_in_files_in_remote_storage_cache,
    add_to_csv_pdf_sync_cache,
    add_to_csv_pdf_sync_cache_v2,
    add_to_lab_test_records_cache_v2
)

from ggt.lib.adapters.s3_adapter import (
    archive_ftp_s3_file
)

import ggt.lib.constants as c

session_id = generate_session_id()

local_backups_path = cfg('vendors.healthtrackrx.inbound.local_backups_path')
local_download_path = cfg('vendors.healthtrackrx.inbound.local_download_path')

# ----What this does----
# Delete/move files at the download directory
# get a list of remote files
# iterate over the files
#       if file exists in cache, skip. Else download. Add name to cache
# --
# parse CSV files, add all records into the labrecords table in cache (insert ignore)
# Take all the records in the cache and add to Mysql (results are available for reporting)
# Scan the download folder and upload all the files to inboundfiles folder in GCP
# Copy renamed PDF lab reports to GCP


def task_process_inbound_lab_reports():
    start = time.time()
    print_header(
        '\n\n******************Inbound file processing [Start]******************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing Inbound Lab Reports')

    # init_local_cache()
    # load_data_from_remote_db_to_cache()

    # clean_downloads_folder()
    #download_ftp_files()
    #parse_csv_files()

    #add_to_healthtrackrx_inbound_data_table()
    #update_test_samples_with_results()
    #upload_pdf_lab_reports()
    process_pdf_results_for_lab_ait()
    process_pdf_results_for_lab_mawd()
    #parse_report_comments()
    add_to_healthtrackrx_inbound_data_table()
    add_to_mawdpath_inbound_data_table()
    update_test_samples_with_results()

    #upload_all_inbound_files_to_central_storage() //Not required anymore since files are hosted in S3
    

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing Inbound Lab Reports')

    print_header(
        '\n\n****************** COMPLETED ******************************\nElapsed Time: {}\n'.format(time.time() - start))


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
            type=c.ERROR, 
            function=whoami(), 
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def download_ftp_files():
    print_ok2('Connecting to FTP server...')
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
        ftp_client.close()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def copy_files_to_local(ftp_client, directory_list, remote_folder):
    try:
        for dir in directory_list:
            remote_dir_path = "{}/{}".format(remote_folder, dir)
            total_files = 0
            cache_hits = 0
            cache_misses = 0
            download_errors = 0
            try:
                dir_list, file_list = get_remote_directories_and_files(ftp_client, remote_dir_path)

                file_count = len(file_list)
                i = 0
                p = 0
                PROGRESS_LABEL = 'copying files from FTP to local'
                for filename in file_list:
                    i += 1
                    p = i/file_count*100
                    print_progress_bar_message("{} {} —— {:.1f}%".format(PROGRESS_LABEL, remote_dir_path, p))

                    total_files += 1
                    try:
                        cache_hits, cache_misses, download_errors = download_and_cleanup(
                            ftp_client, filename, remote_dir_path, cache_hits, cache_misses, download_errors)

                    except Exception as err:
                        download_errors += 1
                        log_generic(
                            type=c.ERROR,
                            function=whoami(),
                            task_session_id=session_id,
                            error=err
                        )

                print_ok2("{} {} —— 100%            ".format(
                    PROGRESS_LABEL, remote_dir_path))

            except Exception as err:
                log_generic(
                    type=c.ERROR,
                    function=whoami(),
                    task_session_id=session_id,
                    error=err
                )
            finally:
                print_ok1('total_files: {}'.format(total_files))
                print_ok1('cache_hits: {}'.format(cache_hits))
                print_ok1('cache_misses: {}'.format(cache_misses))
                print_ok1('download_errors: {}'.format(download_errors))

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )


def prep_local_downloads_dir(remote_dir_path):
    newpath = "{}/{}".format(local_download_path, remote_dir_path)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


def cleanup_s3():
    pass



def download_and_cleanup(ftp_client, filename, remote_dir_path, cache_hits, cache_misses, download_errors):
    local_downloads_dir = prep_local_downloads_dir(remote_dir_path)
    if file_exists_in_all_inbound_files_cache(filename):
        cache_hits += 1
        old_path = '{}/{}'.format(remote_dir_path, filename).replace('//', '/')
        new_path = '{}{}/{}'.format('/backups/processed',
                                    remote_dir_path, filename).replace('//', '/')
        print('Archiving FTP file {}'.format(old_path))
        ########ftp_move_file(ftp_client, old_path, new_path)  # Archive file

    else:
        cache_misses += 1
        local_path = "{}/{}".format(local_downloads_dir,
                                    filename).replace('//', '/')
        if path.exists(local_path):
            print("file {} exists".format(local_path))
            if os.stat(local_path).st_size > 0:
                add_to_all_inbound_files_cache(filename)
            else:
                print_error(
                    'Deleting empty downloaded file : {}'.format(local_path))
                download_errors += 1
                os.remove(local_path)
        else:
            print_ok1("copying {} to {}".format(filename, local_path))
            try:
                ftp_client.get(filename, local_path)
            except Exception as err:
                print_error(err)
                raise ValueError(
                    'Error downloading from FTP —— {}'.format(filename))

            if os.stat(local_path).st_size > 0:
                add_to_all_inbound_files_cache(filename)
            else:
                print_error(
                    'Deleting empty downloaded file : {}'.format(local_path))
                download_errors += 1
                os.remove(local_path)
                raise ValueError(
                    'Error downloading from FTP —— {}'.format(filename))

    return cache_hits, cache_misses, download_errors


def ftp_move_file(ftp_client, old_path, new_path):
    dir_path, file_name = os.path.split(new_path.rstrip('/'))

    try:
        ftp_client.chdir(dir_path)
    except IOError:
        ftp_create_dir_path(ftp_client, dir_path)

    try:
        ftp_client.rename(old_path, new_path)
    except Exception as err:
        print_error('ftp move failed: {}'.format(err))


def ftp_create_dir_path(ftp_client, dir_path):
    # Test if sub directories to the remote path exists. If not recursively create them
    dir_chain = dir_path.split('/')
    sub_dir_path = ''
    for directory in dir_chain:
        sub_dir_path = '{}/{}'.format(sub_dir_path,
                                      directory).replace('//', '/')
        try:
            ftp_client.chdir(sub_dir_path)
        except IOError:
            ftp_client.mkdir(sub_dir_path)


def get_remote_directories_and_files(ftp_client, remote_folder):
    file_list = []
    dir_list = []

    try:
        ftp_client.chdir(remote_folder)
        resources = ftp_client.listdir()

        for resource in resources:
            lstatout = str(ftp_client.lstat(resource)).split()[0]
            if 'd' in lstatout:
                dir_list.append(resource)
            else:
                file_list.append(resource)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
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
    print(directories)
    return directories


def parse_csv_files():
    try:
        file_list = glob.iglob(
            '{}/**/*.csv'.format(local_download_path), recursive=True)

        file_count = 0
        for filename in file_list:
            file_count += 1

        file_list = glob.iglob(
            '{}/**/*.csv'.format(local_download_path), recursive=True)
        i = 0
        p = 0
        PROGRESS_LABEL = 'Parsing CSV files'
        for filename in file_list:
            try:
                i += 1
                p = i/file_count*100
                print_progress_bar_message('Parsing CSV files {:.1f}%'.format(p))
                parse_csv_file(filename)
            except Exception as e:
                print(e)
                print_error('Error Parsing {}'.format(filename))

        print_ok2('{} 100%'.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)


def parse_csv_file(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(lower_first(csvfile))
        for row in reader:
            try:
                add_to_lab_test_records_cache(row)
                add_to_csv_pdf_sync_cache(row)                    

            except Exception as err:
                print("err:", err)


def load_data_from_remote_db_to_cache():
    sql = """
        SELECT * 
        FROM healthtrackrx_inbound_data 
        """
    rows = read_rows(sql)

    row_count = len(rows)
    i = 0
    p = 0
    PROGRESS_LABEL = 'copying data from remote db to local cache'
    for row in rows:
        i += 1
        p = i/row_count*100
        print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))
        add_to_lab_test_records_cache(row)

    print_ok2('{} 100%            '.format(PROGRESS_LABEL))


def process_pdf_results_for_lab_ait():
    print('process_pdf_results_for_lab_ait')
    try:
        file_count = 0
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            file_count += 1

        i = 0
        p = 0
        PROGRESS_LABEL = 'Processing and uploading PDF lab reports'
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            i += 1
            p = i/file_count*100
            print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))

            try:
                if os.stat(local_file_path).st_size == 0:
                    raise ValueError('Empty File')

                __requisition_id, __order_number, __test_result, __test_status, __destination_filename = extract_report_info(local_file_path)

                #skip old format file
                if not __requisition_id:
                    continue

                #proceed to process new format file
                add_to_csv_pdf_sync_cache_v2(__requisition_id, __order_number, __test_result, __test_status, 'AIT')
                add_to_lab_test_records_cache_v2(__requisition_id, __order_number, __test_result, __test_status, 'AIT')

                if __destination_filename:
                    shutil.copyfile(local_file_path, '{}/{}'.format(local_backups_path, __destination_filename))

                    if file_exists_in_files_in_remote_storage_cache(__destination_filename):
                        #print_ok2('cache hit: {}'.format(__destination_filename))
                        pass
                    else:
                        if __order_number and __destination_filename:
                            upload_status = upload_lab_report(
                                local_file_path,
                                __destination_filename
                            )
                            if upload_status is None:
                                print('pdf_lab_report - Error Uploading.... {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            elif upload_status:
                                print('pdf_lab_report - upload success {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            else:
                                print('pdf_lab_report exists at destination... adding to local cache: {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                                add_to_files_in_remote_storage_cache(
                                    __destination_filename)
                        else:
                            #print_ok2('Lab report upload skipped for rejected lab test')
                            handle_reject_report(local_file_path)
                            
            except Exception as err:
                print('Error uploading — {} — {}'.format(err, local_file_path))

        print_ok2('{} 100%            '.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)




def process_pdf_results_for_lab_mawd():
    print('process_pdf_results_for_lab_mawd')
    #local_download_path = cfg('vendors.mawdpath.remote_downloads_folder.local_download_path')
    local_download_path = '/Users/suresh/ggt-tasks/downloads/mawdpath/prod/results'
    try:
        file_count = 0
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            file_count += 1

        i = 0
        p = 0
        PROGRESS_LABEL = 'Processing and uploading PDF lab reports'
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            i += 1
            p = i/file_count*100
            print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))

            try:
                if os.stat(local_file_path).st_size == 0:
                    raise ValueError('Empty File')

                #__requisition_id, __order_number, __test_result, __test_status, __destination_filename = extract_report_info(local_file_path)
                __vial_id, __order_number, __test_result, __test_status, __destination_filename = extract_report_info_mawd(local_file_path)

                add_to_csv_pdf_sync_cache_v2(__vial_id, __order_number, __test_result, __test_status, 'MAWD')
                add_to_lab_test_records_cache_v2(__vial_id, __order_number, __test_result, __test_status, 'MAWD')

                if __destination_filename:
                    ######shutil.copyfile(local_file_path, '{}/{}'.format(local_backups_path, __destination_filename))

                    if file_exists_in_files_in_remote_storage_cache(__destination_filename):
                        #print_ok2('cache hit: {}'.format(__destination_filename))
                        pass
                    else:
                        if __order_number and __destination_filename:
                            upload_status = upload_lab_report(
                                local_file_path,
                                __destination_filename
                            )
                            if upload_status is None:
                                print('pdf_lab_report - Error Uploading.... {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            elif upload_status:
                                print('pdf_lab_report - upload success {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            else:
                                print('pdf_lab_report exists at destination... adding to local cache: {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                                add_to_files_in_remote_storage_cache(
                                    __destination_filename)
                        else:
                            #print_ok2('Lab report upload skipped for rejected lab test')
                            handle_reject_report(local_file_path)
                            
            except Exception as err:
                print('Error uploading — {} — {}'.format(err, local_file_path))

        print_ok2('{} 100%            '.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)


def upload_pdf_lab_reports():
    print('uploading PDF lab reports')
    try:
        file_count = 0
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            file_count += 1

        i = 0
        p = 0
        PROGRESS_LABEL = 'uploading PDF lab reports'
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            i += 1
            p = i/file_count*100
            print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))

            try:
                if os.stat(local_file_path).st_size == 0:
                    raise ValueError('Empty File')

                __requisition_id, __order_number, __destination_filename = generate_destination_filename(local_file_path)
                add_to_csv_pdf_sync_cache(
                    {'requisition_id': __requisition_id}, 
                    'pdf'
                )

                shutil.copyfile(
                    local_file_path, '{}/{}'.format(local_backups_path, __destination_filename))
                if __destination_filename:
                    if file_exists_in_files_in_remote_storage_cache(__destination_filename):
                        #print_ok2('cache hit: {}'.format(__destination_filename))
                        pass
                    else:
                        if __order_number:
                            upload_status = upload_lab_report(
                                local_file_path,
                                __destination_filename
                            )
                            if upload_status is None:
                                print('pdf_lab_report - Error Uploading.... {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            elif upload_status:
                                print('pdf_lab_report - upload success {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                            else:
                                print('pdf_lab_report exists at destination... adding to local cache: {} ==> {}'.format(
                                    local_file_path, __destination_filename))
                                add_to_files_in_remote_storage_cache(
                                    __destination_filename)
                        else:
                            #print_ok2('Lab report upload skipped for rejected lab test')
                            handle_reject_report(local_file_path)
                            
            except Exception as err:
                print('Error uploading — {} — {}'.format(err, local_file_path))

        print_ok2('{} 100%            '.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)


def parse_report_comments():
    print('Parsing PDF lab reports')
    try:
        file_count = 0
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            file_count += 1

        i = 0
        p = 0
        PROGRESS_LABEL = 'Parsing PDF lab reports'
        for local_file_path in glob.iglob('{}/**/*.pdf'.format(local_download_path), recursive=True):
            i += 1
            p = i/file_count*100
            print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))

            try:
                if os.stat(local_file_path).st_size == 0:
                    raise ValueError('Empty File')

                __requisition_id, __order_number, __destination_filename = generate_destination_filename(local_file_path)

                import pdfplumber
                with pdfplumber.open(local_file_path) as pdf:
                    first_page = pdf.pages[0]
                    print(first_page.extract_text(x_tolerance=3, y_tolerance=3).splitlines())
                    for line in first_page.extract_text(x_tolerance=3, y_tolerance=3).splitlines():
                        if line.startswith('Rejection Report'):
                            is_reject_report=True
                        if line.startswith('Comments:'):
                            reject_reason = line.replace('Comments:','').strip()
                
                            
            except Exception as err:
                print('Error uploading — {} — {}'.format(err, local_file_path))

        print_ok2('{} 100%            '.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)


def handle_reject_report(pdf_report_path):
    import pdfplumber

    with pdfplumber.open(pdf_report_path) as pdf:
        is_reject_report = False
        reject_reason = ''
        first_page = pdf.pages[0]
        print(first_page.extract_text(x_tolerance=3, y_tolerance=3).splitlines())
        for line in first_page.extract_text(x_tolerance=3, y_tolerance=3).splitlines():
            if line.startswith('Rejection Report'):
                is_reject_report=True
            if line.startswith('Comments:'):
                reject_reason = line.replace('Comments:','').strip()
        
        print(is_reject_report, reject_reason)


def upload_all_inbound_files_to_central_storage():
    try:
        file_count = 0
        for local_file_path in glob.iglob('{}/**/*'.format(local_download_path), recursive=True):
            file_count += 1

        i = 0
        p = 0
        PROGRESS_LABEL = 'uploading all original inbound files to remote storage'
        for local_file_path in glob.iglob('{}/**/*'.format(local_download_path), recursive=True):
            i += 1
            p = i/file_count*100
            print_progress_bar_message('{} {:.1f}%'.format(PROGRESS_LABEL, p))

            filename = extract_filename(local_file_path)
            try:
                if os.stat(local_file_path).st_size == 0:
                    raise ValueError('Empty File')

                if file_exists_in_files_in_remote_storage_cache(filename):
                    #print('cache hit: ', filename)
                    pass
                else:
                    if path.isdir(local_file_path):
                        #print('Skipping uploading Directory {}'.format(local_file_path))
                        pass
                    else:
                        upload_status = upload_to_all_inbound_files(local_file_path, filename)
                        if upload_status is None:
                            print_error(
                                'Error Uploading.... {}'.format(filename))
                        elif upload_status:
                            print('upload success {}'.format(filename))
                            pass
                        else:
                            #print('file exists... adding to local cache: {}'.format(filename))
                            add_to_files_in_remote_storage_cache(filename)
            except Exception as err:
                print('Error uploading {}'.format(filename))

        print_ok2('{} 100%            '.format(PROGRESS_LABEL))

    except Exception as err:
        print(err)





#'ggt-tasks/downloads/healthtrackrx/Reports/3561603_967995_Negative.pdf'
#'ggt-tasks/downloads/healthtrackrx/Reports/3560192_962060_Positive.pdf'
#'ggt-tasks/downloads/healthtrackrx/Reports/3553760__Rejected.pdf'
def extract_report_info(file_path):
    filename = None
    requisition_id = None
    order_number = None
    test_result = None
    test_status = None

    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]

        #ignore old format reports
        if filename.startswith('Final-Report') or filename.startswith('requisitionReport') or filename.startswith('Preliminary-Report'):
            return requisition_id, order_number, test_result, test_status, filename

        filename_vars = filename.replace('.pdf','').split('_')
        requisition_id = filename_vars[0]
        order_number = filename_vars[1]
        test_result = filename_vars[2]

        if test_result == 'Negative' or test_result == 'Positive':
            test_status = 'Approved'
            filename = '{}.pdf'.format(order_number)
        elif test_result == 'Rejected':
            test_result = ''
            filename = ''
            test_status = 'Rejected'
        else:
            test_status =  None

        return requisition_id, order_number, test_result, test_status, filename

    except Exception as err:
        print_error(err)

    
def extract_report_info_mawd(file_path):
    filename = None
    vial_id = None
    order_number = None
    test_result = None
    test_status = None

    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]

        filename_vars = filename.replace('.pdf','').split('_')
        order_number = filename_vars[0]
        vial_id = filename_vars[1]
        test_result = filename_vars[2]

        if test_result == 'NOTDETECTED':
            test_status = 'Approved'
            test_result = 'Negative'
            filename = '{}.pdf'.format(order_number)
        elif test_result == 'DETECTED':
            test_status = 'Approved'
            test_result = 'Positive'
            filename = '{}.pdf'.format(order_number)
        else:
            test_status =  None

        return vial_id, order_number, test_result, test_status, filename

    except Exception as err:
        print_error(err)


def generate_destination_filename(file_path):
    filename = None
    requisition_id = None
    order_number = None

    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]
        requisition_id = filename.split('-')[3]

        if filename.startswith('requisitionReport'):
            #print_warning('Skipping reject file: {}'.format(filename))
            pass
        else:
            order_number = get_order_number_by_requisition_id(requisition_id)
            if order_number:
                filename = '{}.pdf'.format(order_number)
            else:
                print_error('Requisition Not found - ID: {} —/— {}'.format(requisition_id, filename))
                append_to_processing_summary('{} - no record found'.format(requisition_id))

    except Exception as err:
        print("err:", err)

    return requisition_id, order_number, filename


def append_to_processing_summary(txt):
    # append mode
    f = open(
        "/Users/suresh/ggt-tasks/process_summary/ggt-inbound-processing-summary.txt", "a")
    f.write(txt + "\n")
    f.close()


def add_to_healthtrackrx_inbound_data_table():
    print('syncing cached healthtrackrx_inbound_data to remote DB')
    rows = get_all_lab_records_from_cache('AIT')
    try:
        sql = """
            INSERT INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        exec_batch_execute(sql, rows)

    except Exception as err:
        print_error('Critical ERROR: {}'.format(err))


def add_to_mawdpath_inbound_data_table():
    print('syncing cached mawdpath_inbound_data to remote DB')
    rows = get_all_lab_records_from_cache('MAWD')
    try:
        sql = """
            INSERT INTO mawdpath_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        exec_batch_execute(sql, rows)

    except Exception as err:
        print_error('Critical ERROR: {}'.format(err))


def update_test_samples_with_results():
    print('updating test results in remote DB')
    sql = """
        UPDATE test_samples
                INNER JOIN
            healthtrackrx_inbound_data h ON (test_samples.id = h.order_number) 
        SET 
            test_samples.lab_result_receive_dt = NOW(),
            test_samples.test_result = (CASE
                WHEN (h.result = 'Negative') THEN 'neg'
                WHEN (h.result = 'Positive') THEN 'pos'
                WHEN (h.result = 'inconclusive') THEN 'inconclusive'
                ELSE NULL
            END),
            test_samples.status = (CASE
                WHEN (h.status = 'Approved') THEN 'lab_result_received'
                WHEN (h.status = 'Resulted') THEN 'lab_result_received'
                WHEN (h.status = 'Rejected') THEN 'rejected'
                ELSE NULL
            END),
            test_samples.update_dt = NOW()
        WHERE
            test_samples.test_result IS NULL
                AND test_samples.id = h.order_number
        """
    vals = ()
    exec_update(sql, vals)

    sql = """
        UPDATE test_samples
                INNER JOIN
            mawdpath_inbound_data h ON (test_samples.id = h.order_number) 
        SET 
            test_samples.lab_result_receive_dt = NOW(),
            test_samples.test_result = (CASE
                WHEN (h.result = 'Negative') THEN 'neg'
                WHEN (h.result = 'Positive') THEN 'pos'
                WHEN (h.result = 'inconclusive') THEN 'inconclusive'
                ELSE NULL
            END),
            test_samples.status = (CASE
                WHEN (h.status = 'Approved') THEN 'lab_result_received'
                WHEN (h.status = 'Resulted') THEN 'lab_result_received'
                WHEN (h.status = 'Rejected') THEN 'rejected'
                ELSE NULL
            END),
            test_samples.update_dt = NOW()
        WHERE
            test_samples.test_result IS NULL
                AND test_samples.id = h.order_number
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


def organize_backup_files_archive():
    pass


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def print_header(message):
    print('{.HEADER}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok1(message):
    print('{.OKGREEN}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok2(message):
    print('{.OKBLUE}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_warning(message):
    print('{.WARNING}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_error(message):
    print('{.FAIL}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_progress_bar_message(message):
    print('{.OKBLUE}{}{.ENDC}\r'.format(bcolors, message, bcolors), end="")
