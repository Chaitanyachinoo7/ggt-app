import math
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

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.sms import send_sms

'''
def _task_process_sms_queue():
    to_number = '+14159873454'
    message = """Hi Mo, your GoGetTested.com COVID-19 test results are available. 
    Please follow this link to view your results https://start.GoGetTested.com/r/c304407c-0624-4012-b10d-437b734adb7d"""
    send_sms(to_number, message)
'''


def task_process_sms_queue():
    print('\n\n********************task_process_SMS_queue****************************\n\n')

    batch_size = 100
    sql = """
        SELECT count(*) as total FROM sms_notification_queue where status IN ('pending','retry')
    """
    row = replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)

    for _ in range(limit):
        __batch_process_sms_queue(batch_size)

    print('\n\n************************************************\n\n')


def __batch_process_sms_queue(batch_size=100):
    sql = """
    SELECT * 
    FROM sms_notification_queue 
    WHERE status 
        IN ('pending','retry') 
    ORDER BY ID DESC
    LIMIT {}
    """.format(batch_size)
    rows = replica_read_rows(sql)

    for row in rows:
        _id = row['id']
        status = row['status']
        to_number = row['to_number']
        message = row['message']

        if status == 'retry':
            if send_sms(to_number, message):
                update_sms_status_to_processed(_id)
            else:
                update_sms_status_to_error(_id)
        else:
            if send_sms(to_number, message):
                update_sms_status_to_processed(_id)
            else:
                update_sms_status_to_retry(_id)


def update_sms_status_to_processed(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'processed',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)


def update_sms_status_to_retry(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'retry',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)


def update_sms_status_to_error(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'error',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)
