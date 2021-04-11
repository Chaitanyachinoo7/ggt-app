from ggt.tasks.lab_integration import utils

from ggt.lib.utils import (
    get_config_val as cfg,
    print_header,
    print_ok1,
    print_warning,
    print_error
)

from ggt.lib.adapters.s3_adapter import (
    move_file,
    copy_file_from_s3_to_s3,
    get_file_iterator,
    file_exists,
    read_file
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

import datetime
import os


lab_inbound_bucket = cfg('lab_integrations.s3_bucket')
labreport_bucket = cfg('lab_integrations.labreport_bucket')
lab_archive_bucket = cfg('lab_integrations.archive_bucket')


def process_inbound_results():
    total_processed_results = 0

    for lab_id in utils.lab_map.keys():
        lab_total = process_pdf_results(lab_id=lab_id)
        total_processed_results += lab_total

    return total_processed_results


def process_pdf_results(lab_id):
    """
    1. Go over each PDF file in the s3 bucket for the specied lab
    2. Extract GGT Order ID, Lab (Requisition) ID and Test Result from each file's name
    3. Add extracted data into the inbound_data table for the lab
    4. Update test_samples table with the extracted data
    5. Copy report PDF to labreports s3 bucket
    6. Move PDF files to archive folder
    """

    processed_files = 0

    print_ok1("Processing results for {0}".format(
        utils.lab_map[lab_id]["lab_code"]))

    key_suffix = '.pdf'
    inbound_file_path = utils.lab_map[lab_id]["inbound_path"]

    for filename in get_file_iterator(bucket=lab_inbound_bucket,
                                      prefix=inbound_file_path,
                                      suffix=key_suffix):

        result_details = extract_details_from_filename(filename, lab_id=lab_id)

        if not result_details["requisition_id"] or not result_details["order_id"]:
            msg = 'Invalid requisition_id/order_id.. skipping file {0} with GGT-ORDER: {1}'.format(
                filename, result_details.get("order_id", "None"))
            print_warning(msg)

            if not result_details["order_id"]:
                _oid = -1
            else:
                _oid = result_details["order_id"]

            utils.log_error(order_id=_oid,
                            lab_id=lab_id, metadata=filename, msg=msg, direction="inbound")
            continue

        result, *metadata = add_to_inbound_data_table(result_details, lab_id)

        if not result:
            msg = 'Unable to save extracted data to inbound table for GGT-ORDER: {0}'.format(
                result_details["order_id"])
            print_warning(msg)
            utils.log_error(order_id=result_details["order_id"],
                            lab_id=lab_id, metadata=str(metadata), msg=msg, direction="inbound")
            continue

        result, *metadata = update_test_samples_with_results(lab_id)

        if not result:
            msg = 'Unable to save result data into test_samples for GGT-ORDER: {0}'.format(
                result_details["order_id"])
            print_warning(msg)
            utils.log_error(order_id=result_details["order_id"],
                            lab_id=lab_id, metadata=str(metadata), msg=msg, direction="inbound")
            continue

        # copy pdf result to labreports folder
        if not result_details["test_result"] == 'Rejected':

            result, *metadata = utils.copy_s3_file(source_bucket=lab_inbound_bucket,
                                                   source_path=filename,
                                                   dest_bucket=labreport_bucket,
                                                   dest_path=result_details["labreport_filename"])

            if not result:
                msg = 'Unable to move file {0} to labreports folder. GGT-ORDER: {1}'.format(filename,
                                                                                            result_details["order_id"])
                print_warning(msg)
                utils.log_error(order_id=result_details["order_id"],
                                lab_id=lab_id, metadata=str(metadata), msg=msg, direction="inbound")
                continue
        else:
            print_warning(
                "GGT-ORDER: {0} is marked 'Rejected' by lab".format(result_details["order_id"]))

        if lab_id == 3:

            # archive the idx file in case of CRL labs
            idx_file = filename.replace(".pdf", ".idx")
            result, *metadata = archive_inbound_file(lab_id=lab_id,
                                                     source_bucket=lab_inbound_bucket,
                                                     source_path=idx_file,
                                                     dest_bucket=lab_archive_bucket,
                                                     dest_path=idx_file)
            # archive all rpt files
            force_archive_files(3, key_suffix='.rpt')

        # archive the pdf result files

        result, *metadata = archive_inbound_file(lab_id=lab_id,
                                                 source_bucket=lab_inbound_bucket,
                                                 source_path=filename,
                                                 dest_bucket=lab_archive_bucket,
                                                 dest_path=filename)

        if not result:
            msg = 'Unable to move file {0} to archive folder. GGT-ORDER: {1}'.format(filename,
                                                                                     result_details["order_id"])
            print_warning(msg)
            utils.log_error(order_id=result_details["order_id"],
                            lab_id=lab_id, metadata=str(metadata), msg=msg, direction="inbound")
            continue

        processed_files += 1

    print_ok1(utils.lab_map[lab_id]["lab_code"] +
              " ==> {} processed files".format(processed_files))
    return processed_files


def extract_details_from_filename(inbound_filename, lab_id):
    labreport_filename = None
    requisition_id = None
    order_number = None
    test_result = None
    test_status = None

    try:
        inbound_filename = os.path.basename(inbound_filename)

        # ignore old format reports
        if inbound_filename.startswith(('Final-Report', 'requisitionReport', 'Preliminary-Report')):
            return {
                "requisition_id": requisition_id,
                "order_id": order_number,
                "test_result": test_result,
                "test_status": test_status,
                "labreport_filename": labreport_filename
            }

        # is a folder name
        if inbound_filename == '':
            return {
                "requisition_id": requisition_id,
                "order_id": order_number,
                "test_result": test_result,
                "test_status": test_status,
                "labreport_filename": labreport_filename
            }

        filename_vars = inbound_filename.replace('.pdf', '').split('_')

        if lab_id == 3:
            requisition_id = filename_vars[1]
            order_number = filename_vars[0]
            test_result = filename_vars[2]
        else:
            requisition_id = filename_vars[0]
            order_number = filename_vars[1]
            test_result = filename_vars[2]

        """
        PDF file name formats:
        1. AIT: reqID_ggtOrderId_Positive.pdf, reqID_ggtOrderId_Negative.pdf
        2. MAWD/LAB3A: reqID_ggtOrderId_DETECTED_F.pdf, reqID_ggtOrderId_NOTDETECTED_F.pdf
        3. CRL: ggtOrderId_reqID_IPOS.pdf, ggtOrderId_reqID_INEG.pdf
        """

        if test_result in ['NOTDETECTED', 'INEG']:
            test_result = 'Negative'

        if test_result in ['DETECTED', 'IPOS']:
            test_result = 'Positive'

        if test_result in ['Negative', 'Positive']:
            test_status = 'Approved'
            labreport_filename = '{}.pdf'.format(order_number)

        elif test_result in ['Rejected', 'INON'] or 'SPECIMEN_UNACCEPTABLE' in inbound_filename or 'SpecimenUnacceptable' in inbound_filename:
            test_status = 'Rejected'
            test_result = 'Rejected'

        else:
            test_status = None

    except Exception as err:
        print_warning(
            "Unable to extract details from {}: {}".format(inbound_filename, str(err)))

    return {
        "requisition_id": requisition_id,
        "order_id": order_number,
        "test_result": test_result,
        "test_status": test_status,
        "labreport_filename": labreport_filename
    }


def add_to_inbound_data_table(data, lab_id):
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
    """.format(utils.lab_map[lab_id]["inbound_data_table_name"])

    vals = (data["requisition_id"], data["order_id"],
            data["test_status"], data["test_result"])

    res = exec_insert(sql, vals)

    if res >= 0:
        return True, None

    else:
        msg = 'Insert FAILED for ' + str(data)
        print_error(msg)
        return False, msg


def update_test_samples_with_results(lab_id):
    try:
        data_table = utils.lab_map[lab_id]["inbound_data_table_name"]
        sql = """
            UPDATE test_samples
                    INNER JOIN
                {} h ON (test_samples.id = h.order_number)
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
            """.format(data_table)

        vals = ()
        exec_update(sql, vals)

        return True, None

    except Exception as err:
        msg = 'Critical ERROR - Database Update Failed: {}'.format(str(err))
        print_error(msg)
        return False, msg


def archive_inbound_file(lab_id, source_bucket, source_path, dest_bucket, dest_path):
    sql = """
        INSERT INTO processed_inbound_files
        (
            filename,
            lab_id
        )
        VALUES(%s, %s)
    """
    vals = (source_path, lab_id)
    if exec_insert(sql, vals):

        # prevent override of previous file, add dt suffix
        if file_exists(dest_bucket, dest_path):
            dest_path = dest_path.replace(
                '.', '-{}.'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")))

        try:
            return move_file(source_bucket, source_path, dest_bucket, dest_path), None
        except Exception as e:
            return False, str(e)
    else:
        msg = 'Skipping Archiving, Insert FAILED while adding to Processed Files: ' + source_path
        print_error(msg)
        return False, msg


def force_archive_files(lab_id, key_suffix):
    inbound_file_path = utils.lab_map[lab_id]["inbound_path"]

    for file_path in get_file_iterator(bucket=lab_inbound_bucket, prefix=inbound_file_path, suffix=key_suffix):
        print_warning("Force Archive: {}".format(file_path))
        archive_inbound_file(lab_id, lab_inbound_bucket,
                             file_path, lab_archive_bucket, file_path)
