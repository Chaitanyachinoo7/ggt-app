import datetime
import time

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

from ggt.lib.adapters.s3_adapter import (
    move_file,
    copy_file_from_s3_to_s3,
    get_file_iterator,
    file_exists,
    read_file
)

import ggt.lib.constants as c

session_id = generate_session_id()

local_backups_path = cfg('vendors.healthtrackrx.inbound.local_backups_path')
local_download_path = cfg('vendors.healthtrackrx.inbound.local_download_path')

lab_inbound_bucket = 'ggt-sftp'
labreport_bucket = 'ggt-labreports'
lab_archive_bucket = 'ggt-sftp-archive'

result_cache = {}


def task_process_inbound_lab_reports():
    start = time.time()
    print_header(
        '\n\n******************Inbound file processing [Start]******************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing Inbound Lab Reports')

    process_pdf_results_for_lab(1)  # AIT
    process_pdf_results_for_lab(2)  # MAWD
    preload_crl_rpt_data()
    process_pdf_results_for_lab(3)  # CRL
    process_pdf_results_for_lab(4)  # LAB3A

    update_test_samples_with_results()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing Inbound Lab Reports')

    print_header(
        '\n\n****************** COMPLETED ******************************\nElapsed Time: {}\n'.format(time.time() - start))


def process_pdf_results_for_lab(lab_id):
    print('process_pdf_results_for_lab #'+str(lab_id))
    key_suffix = '.pdf'

    if lab_id == 1:  # AIT
        key_prefix = 'healthtrackrx/Reports/'
        table_name = 'healthtrackrx_inbound_data'

    elif lab_id == 2:  # MAWD
        key_prefix = 'mawdpath/prod/results/'
        table_name = 'mawdpath_inbound_data'

    elif lab_id == 3:  # CRL
        key_prefix = 'crllabs/prod/results/'
        table_name = 'crl_inbound_data'
        key_suffix = '.idx'

    elif lab_id == 4:  # LAB3A
        key_prefix = 'lab3a/prod/results/'
        table_name = 'lab3a_inbound_data'

    else:
        print_error('Unknown LAB')
        return

    for filename in get_file_iterator(bucket=lab_inbound_bucket, prefix=key_prefix, suffix=key_suffix):
        lab_inbound_key = filename
        lab_archive_key = lab_inbound_key

        try:
            if lab_id == 1:  # AIT
                requisition_id, order_number, test_result, test_status, labreport_filename = extract_report_info_ait(
                    filename)
            elif lab_id == 2:  # MAWD
                requisition_id, order_number, test_result, test_status, labreport_filename = extract_report_info_mawd(
                    filename)
            elif lab_id == 3:  # CRL
                requisition_id, order_number, test_result, test_status, labreport_filename, original_labreport_filename = extract_report_info_crl(
                    filename)
            elif lab_id == 4:  # LAB3A uses samefunction as mawd
                requisition_id, order_number, test_result, test_status, labreport_filename = extract_report_info_mawd(
                    filename)
            else:
                raise ValueError('Unknown Lab')

            labreport_key = labreport_filename

            if requisition_id is None:
                print_warning(
                    'Invalid requisition_id.. skipping {}'.format(filename))
                continue

            add_to_inbound_data_table(
                table_name, requisition_id, order_number, test_result, test_status)

            # is it a Rejected Sample? #is labreport in s3? #did labreport to copy to s3 successfully
            archive = (test_result == 'Rejected') or \
                file_exists(lab_inbound_bucket, labreport_key) or \
                copy_inbound_report_to_public_labreports_folder(
                    lab_inbound_key, labreport_key)

            archive_inbound_file(
                lab_id, archive, lab_inbound_key, lab_archive_key)

            if lab_id == 3:  # CRL
                archive_inbound_file(
                    lab_id, archive, original_labreport_filename, original_labreport_filename)

        except Exception as err:
            log_generic(
                type=c.ERROR,
                function=whoami(),
                error=err
            )


def preload_crl_rpt_data():
    print('preload_crl_rpt_data')
    key_prefix = 'crllabs/prod/results/'
    key_suffix = '.rpt'

    for file_path in get_file_iterator(bucket=lab_inbound_bucket, prefix=key_prefix, suffix=key_suffix):
        _order_number = None
        _test_result = None
        _requisition_id = None

        try:
            arr = file_path.split('/')
            filename = arr[len(arr)-1]

            # is a folder name
            if filename == '':
                continue

            # parse index file
            for line in read_file(lab_inbound_bucket, file_path).splitlines():
                line = line.decode("utf-8")

                try:
                    if line.startswith('PID'):
                        _requisition_id = line.split('|')[3]
                    elif line.startswith('OBR'):
                        _order_number = line.split('|')[2]
                    elif line.startswith('OBX'):
                        r = line.split('|')[5]
                        if r == 'NDD':
                            _test_result = 'Negative'
                        elif r == 'DET':
                            _test_result = 'Positive'
                        elif r == 'NSA':
                            _test_result = 'Rejected'
                        elif r == 'TNP':
                            _test_result = 'Rejected'
                        else:
                            raise ValueError(
                                'Uknown result: {} / appointment_id {}'.format(r, _order_number))

                except Exception as err:
                    print_error(
                        'Error processing — {} — {}'.format(err, filename))

            result_cache[_order_number] = [_order_number,
                                           _requisition_id, _test_result, file_path]
            print(_order_number, _requisition_id, _test_result, file_path)

        except Exception as err:
            print_error(err)


def add_to_inbound_data_table(table_name, requisition_id, order_number, test_result, test_status):
    if order_number:
        sql = """
        INSERT IGNORE INTO {}
        (
            requisition_id,
            order_number,
            status,
            result
        )
        VALUES(%s, %s, %s, %s)

        ON DUPLICATE KEY UPDATE
            status = VALUES(status), result = VALUES(result)
        """.format(table_name)

        vals = (requisition_id, order_number, test_status, test_result)

        operation = 'requisition_id: {} order_number: {} test_status:{} test_result:{}'.format(
            requisition_id, order_number, test_status, test_result)
        res = exec_insert(sql, vals)
        if res > 0:
            print_ok2('Insert SUCCESS for ' + operation)
        elif res == 0:
            print_ok2('Updated existing ' + operation)
        else:
            print_error('Insert FAILED for ' + operation)

    else:
        print_warning('Invalid Order ID (assuming rejected sample)')


def copy_inbound_report_to_public_labreports_folder(lab_inbound_key, labreport_key):
    # copy labreport to s3
    if file_exists(labreport_bucket, labreport_key):
        print_ok2('Report already exists, s3 copy SKIPPED for {}/{} ==> {}/{}'.format(
            lab_inbound_bucket, lab_inbound_key, labreport_bucket, labreport_key))
        return True

    if copy_file_from_s3_to_s3(lab_inbound_bucket, lab_inbound_key, labreport_bucket, labreport_key):
        print_ok2('s3 copy success for {}/{} ==> {}/{}'.format(lab_inbound_bucket,
                                                               lab_inbound_key, labreport_bucket, labreport_key))
        return True
    else:
        print_error('s3 copy failed for {}/{} ==> {}/{}'.format(lab_inbound_bucket,
                                                                lab_inbound_key, labreport_bucket, labreport_key))
        return False


def archive_inbound_file(lab_id, archive, lab_inbound_key, lab_archive_key):
    if archive:
        sql = """
        INSERT INTO processed_inbound_files
        (
            filename,
            lab_id
        )
        VALUES(%s, %s)
        """
        vals = (lab_inbound_key, lab_id)
        if exec_insert(sql, vals):
            # prevent override of previous file, add dt suffix
            if file_exists(lab_archive_bucket, lab_archive_key):
                lab_archive_key = lab_archive_key.replace(
                    '.', '-{}.'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")))

            print_ok1('archiving {}/{} ==> {}/{}'.format(lab_inbound_bucket,
                                                         lab_inbound_key, lab_archive_bucket, lab_archive_key))
            move_file(lab_inbound_bucket, lab_inbound_key,
                      lab_archive_bucket, lab_archive_key)
        else:
            print_error(
                'Skipping Archiving, Insert FAILED while adding to Processed Files >> ' + lab_inbound_key)


# 'ggt-tasks/downloads/healthtrackrx/Reports/3561603_967995_Negative.pdf'
# 'ggt-tasks/downloads/healthtrackrx/Reports/3560192_962060_Positive.pdf'
# 'ggt-tasks/downloads/healthtrackrx/Reports/3553760__Rejected.pdf'
def extract_report_info_ait(file_path):
    filename = None
    requisition_id = None
    order_number = None
    test_result = None
    test_status = None

    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]

        # ignore old format reports
        if filename.startswith('Final-Report') or filename.startswith('requisitionReport') or filename.startswith('Preliminary-Report'):
            return requisition_id, order_number, test_result, test_status, filename

        filename_vars = filename.replace('.pdf', '').split('_')
        requisition_id = filename_vars[0]
        order_number = filename_vars[1]
        test_result = filename_vars[2]

        if test_result == 'Negative' or test_result == 'Positive':
            test_status = 'Approved'
            filename = '{}.pdf'.format(order_number)
        elif test_result == 'Rejected':
            #test_result = ''
            #filename = ''
            test_status = 'Rejected'
        else:
            test_status = None

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

        # is a folder name
        if filename == '':
            return vial_id, order_number, test_result, test_status, filename

        filename_vars = filename.replace('.pdf', '').split('_')

        file_version = 2
        try:
            report_type = filename_vars[3]  # C for Correction, F for Final
        except Exception as err:
            print_warning('using file version 1 (old naming format)')
            file_version = 1

        if file_version == 1:
            order_number = filename_vars[0]
            # This is actually the MAWD accession number
            vial_id = filename_vars[1]
            test_result = filename_vars[2]
        else:
            order_number = filename_vars[1]
            # This is actually the MAWD accession number
            vial_id = filename_vars[0]
            test_result = filename_vars[2]

        # is a Rejected specimen
        if 'SPECIMEN_UNACCEPTABLE' in filename:
            test_status = 'Rejected'
            test_result = 'Rejected'
        elif test_result == 'NOTDETECTED':
            test_status = 'Approved'
            test_result = 'Negative'
            filename = '{}.pdf'.format(order_number)
        elif test_result == 'DETECTED':
            test_status = 'Approved'
            test_result = 'Positive'
            filename = '{}.pdf'.format(order_number)
        else:
            test_status = None

        return vial_id, order_number, test_result, test_status, filename

    except Exception as err:
        print_error(err)


'''
NAME=JONES, JAYE?SON
DOB=2004-11-25
SSN=
COC=6029690306
SID=29690306
DOCTYPE=LABREPORT
FILENAME=29690306_20210205-165927-214.pdf
CLIENT_CODE=ZSK.EMCW
REFERENCE_ID=1212958
SAMPLE_TYPE=S
REPORT_TYPE=INEG
REPORT_CLASS=NONN
CONTACT_ID=ZSKFTP1
REASON_TYPE=NS
'''


def extract_report_info_crl(file_path):
    filename = None
    requisition_id = None
    order_number = None
    test_result = None
    test_status = None

    try:
        arr = file_path.split('/')
        filename = arr[len(arr)-1]

        # is a folder name
        if filename == '':
            return requisition_id, order_number, test_result, test_status, filename

        # parse index file
        for line in read_file(lab_inbound_bucket, file_path).splitlines():
            line = line.decode("utf-8")

            if line.startswith('FILENAME='):
                pdf_filename = line.split('=')[1]
            if line.startswith('REFERENCE_ID='):
                order_number = line.split('=')[1]
            if line.startswith('SID='):
                requisition_id = line.split('=')[1]

        print(pdf_filename, order_number, requisition_id)

        if not (pdf_filename and order_number and requisition_id):
            raise ValueError('Invalid Data')

        pdf_file_path = '{}{}'.format(
            file_path.replace(filename, ''), pdf_filename)
        filename = '{}.pdf'.format(order_number)

        #result_cache[_order_number] = [_order_number, _requisition_id, _test_result, file_path]
        test_result = result_cache[order_number][2]
        if test_result == 'Rejected':
            test_status = 'Rejected'
        else:
            test_status = 'Approved'

        # Archive the RPT file
        lab_inbound_key = result_cache[order_number][3]
        lab_archive_key = lab_inbound_key
        archive_inbound_file(3, True, lab_inbound_key, lab_archive_key)

        return requisition_id, order_number, test_result, test_status, filename, pdf_file_path

    except Exception as err:
        print_error(err)


def update_test_samples_with_results():
    print('updating test results in remote DB')
    try:
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

        sql = """
            UPDATE test_samples
                    INNER JOIN
                crl_inbound_data h ON (test_samples.id = h.order_number)
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
                lab3a_inbound_data h ON (test_samples.id = h.order_number)
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

    except Exception as err:
        print_error('Critical ERROR - Database Update Failed: {}'.format(err))


def extract_filename(file_path):
    arr = file_path.split('/')
    filename = arr[len(arr)-1]
    return filename
