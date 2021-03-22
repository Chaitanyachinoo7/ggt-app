import os
import sys

import nest_asyncio

nest_asyncio.apply()
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from fastapi.testclient import TestClient
from main import app
from tests.resources import token
from ggt.tasks.hl7_outbound_lab_orders import task_process_hl7_lab_orders
from ggt.tasks.inbound_lab_reports import task_process_inbound_lab_reports
from ggt.lib.adapters.s3_adapter import file_exists, delete_file, write_text_file
from ggt.lib.utils import get_config_val as cfg
from ggt.lib.db import read_rows, exec_update
import tests.data as data

client = TestClient(app)


def get_sample_status_and_result(id_):
    sql = """SELECT * FROM test_samples WHERE id = %s"""
    vals = (id_,)
    sample = read_rows(sql, vals)
    return sample[0]['status'], sample[0]['test_result']


def get_orders_by_status(status, lab_id=None):
    sql = """SELECT * FROM test_samples WHERE status = %s"""
    vals = (status,)
    if lab_id:
        sql = """SELECT * FROM test_samples WHERE status = %s AND lab_id = %s"""
        vals = (status, lab_id,)
    return read_rows(sql, vals)


def _check_hl7_files_in_bucket(orders):
    bucket_name = cfg('lab_integrations.s3_bucket')
    result = True
    for order in orders:
        filename = "ggt-outbound-{}.hl7".format(order['id'])
        if order['lab_id'] == 1:
            lab_folder = "healthtrackrx_merth"
        if order['lab_id'] == 2:
            lab_folder = "mawdpath"
        filename = "{0}/prod/orders/{1}".format(lab_folder, filename)
        if not file_exists(bucket_name, filename):
            print("ERROR: Outbound file missing! - {}".format(filename))
            result = False
    return result


def _check_sample_status(orders, exp_status=None, exp_result=None):
    result = True
    for order in orders:
        status, actual_result = get_sample_status_and_result(order['id'])
        if exp_status and status != exp_status:
            result = False
            print(
                "ERROR: Order ID {0} status unchanged - {1}".format(order['id'], status))
        if exp_result and actual_result != exp_result:
            result = False
            print(
                "ERROR: Order ID {0} result unchanged - {1}".format(order['id'], actual_result))
    return result


def _remove_hl7_files(orders):
    bucket_name = cfg('lab_integrations.s3_bucket')
    result = True
    for order in orders:
        filename = "ggt-outbound-{}.hl7".format(order['id'])
        if order['lab_id'] == 1:
            lab_folder = "healthtrackrx_merth"
        if order['lab_id'] == 2:
            lab_folder = "mawdpath"
        filename = "{0}/prod/orders/{1}".format(lab_folder, filename)
        if not delete_file(bucket_name, filename):
            print("ERROR: Error deleting hl7 file! - {}".format(filename))
            result = False
    return True


def _place_report_files_s3(orders):
    bucket_name = cfg('lab_integrations.s3_bucket')
    expected_results = []
    for order in orders:
        if order['lab_id'] == 1:
            lab_folder = "healthtrackrx"
            filename = "{}_{}_{}.pdf".format("1234", order['id'], "Positive")
            filename = "{0}/Reports/{1}".format(lab_folder, filename)
        if order['lab_id'] == 2:
            lab_folder = "mawdpath"
            filename = "{}_{}_{}_F.pdf".format("1234", order['id'], "DETECTED")
            filename = "{0}/prod/results/{1}".format(lab_folder, filename)
        body = "test".encode("utf-8").decode('utf-8', 'ignore')
        expected_results.append({
            "order_id": order['id'],
            "lab_id": order['lab_id'],
            "pdf_file": filename,
            "result": "pos",
            "req_id": 1234
        })
        write_text_file(bucket_name, filename, body)
    return expected_results


def _check_and_delete_archive_files(orders, crl=False):
    result = True
    labreport_bucket = cfg('lab_integrations.labreport_bucket')
    lab_archive_bucket = cfg('lab_integrations.archive_bucket')
    for order in orders:
        filename = order['pdf_file']
        if not file_exists(lab_archive_bucket, filename):
            print("ERROR: archive file missing! - {}".format(filename))
            result = False
        delete_file(lab_archive_bucket, filename)
        filename = str(order["order_id"]) + ".pdf"
        if not file_exists(labreport_bucket, filename):
            print("ERROR: labreport file missing! - {}".format(filename))
            result = False
        delete_file(labreport_bucket, filename)

        if crl:
            filename = order['rpt_file']
            if not file_exists(lab_archive_bucket, filename):
                print("ERROR: archive file missing! - {}".format(filename))
                result = False
            delete_file(lab_archive_bucket, filename)

            filename = order['idx_file']
            if not file_exists(lab_archive_bucket, filename):
                print("ERROR: archive file missing! - {}".format(filename))
                result = False
            delete_file(lab_archive_bucket, filename)

    return result


def _generate_rpt_idx_pdf_pair(orders):
    bucket_name = cfg('lab_integrations.s3_bucket')
    expected_results = []
    for order in orders:
        filename_rpt = "random.rpt"
        filename_rpt = "crllabs/prod/results/{0}".format(filename_rpt)
        rpt_body = data.sample_rpt.format(1234, order['id'], 'DET')
        write_text_file(bucket_name, filename_rpt, rpt_body)

        filename_idx = "random.idx"
        filename_idx = "crllabs/prod/results/{0}".format(filename_idx)
        idx_body = data.sample_idx.format("random.pdf", order['id'], 1234)
        write_text_file(bucket_name, filename_idx, idx_body)

        filename_pdf = "random.pdf"
        filename_pdf = "crllabs/prod/results/{0}".format(filename_pdf)
        pdf_body = "test"
        write_text_file(bucket_name, filename_pdf, pdf_body)

        expected_results.append({
            "order_id": order['id'],
            "lab_id": 3,
            "rpt_file": filename_rpt,
            "idx_file": filename_idx,
            "pdf_file": filename_pdf,
            "result": "pos",
            "req_id": 1234
        })
    return expected_results


def test_outbound_hl7_orders():
    orders = task_process_hl7_lab_orders()
    assert _check_hl7_files_in_bucket(orders), "Outbound file(s) missing!"
    assert _check_sample_status(
        orders, exp_status='with_lab'), "Test Sample status unchanged!"
    assert _remove_hl7_files(orders), "Unable to delete hl7 files!"


def test_inbound_pdf_processing():
    pending_orders = get_orders_by_status('with_lab')
    expected_results = _place_report_files_s3(pending_orders)
    task_process_inbound_lab_reports()

    assert _check_and_delete_archive_files(
        expected_results), "Files not moved to archive!"
    assert _check_sample_status(pending_orders, exp_status='lab_result_received',
                                exp_result='pos'), "Test Sample result unchanged"


def test_inbound_crl_processing():
    sql = """UPDATE test_samples SET status = 'with_lab' WHERE lab_id = 3"""
    exec_update(sql,)
    pending_orders = get_orders_by_status('with_lab', lab_id=3)
    expected_results = _generate_rpt_idx_pdf_pair(pending_orders)

    task_process_inbound_lab_reports()

    assert _check_sample_status(pending_orders, exp_status='lab_result_received',
                                exp_result='pos'), "Test Sample result unchanged"
    assert _check_and_delete_archive_files(
        expected_results, crl=True), "Files not moved to archive!"
