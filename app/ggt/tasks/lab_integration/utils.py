from ggt.lib.utils import get_config_val as cfg
from ggt.lib.db import read_rows, exec_insert
import datetime

from ggt.lib.adapters.s3_adapter import (
    move_file,
    copy_file_from_s3_to_s3,
    get_file_iterator,
    file_exists,
    read_file
)

from ggt.lib.utils import (
    get_config_val as cfg,
    print_header,
    print_ok1,
    print_warning,
    print_error
)


lab_map = {}


def log_error(order_id, lab_id, metadata=None, msg=None, direction="outbound"):
    """
    Function to log errors while processing inbound/outbound files into the database
    """

    today = datetime.datetime.now()

    sql = """
    INSERT INTO {}_processing_errors
        (
            order_id,
            lab_id,
            description,
            metadata,
            error_dt
        )
        VALUES(%s, %s, %s, %s, %s)
    """.format(direction)
    vals = (order_id, lab_id, msg[:255], str(metadata)[:255], today)
    exec_insert(sql, vals)


def set_lab_map():
    """
    Builds a dict which contains lab information
    """

    sql = """SELECT id, lab_code from labs"""
    labs = read_rows(sql,)

    for lab in labs:
        lab_map[lab["id"]] = {}
        lab_map[lab["id"]]["lab_code"] = lab["lab_code"]
        lab_map[lab["id"]]["outbound_path"] = cfg(
            'lab_integrations.{0}.outbound_path'.format(lab["lab_code"]))
        lab_map[lab["id"]]["inbound_path"] = cfg(
            'lab_integrations.{0}.inbound_path'.format(lab["lab_code"]))
        lab_map[lab["id"]]["inbound_data_table_name"] = cfg(
            'lab_integrations.{0}.inbound_data_table_name'.format(lab["lab_code"]))


def copy_s3_file(source_bucket, source_path, dest_bucket, dest_path):
    if file_exists(dest_bucket, dest_path):
        print_warning('Report already exists, s3 copy SKIPPED for {}/{} ==> {}/{}'.format(
            source_bucket, source_path, dest_bucket, dest_path))
        return True, None

    if copy_file_from_s3_to_s3(source_bucket, source_path, dest_bucket, dest_path):
        return True, None
    else:
        msg = 's3 copy failed for {}/{} ==> {}/{}'.format(source_bucket,
                                                          source_path, dest_bucket, dest_path)
        print_error(msg)
        return False, msg
