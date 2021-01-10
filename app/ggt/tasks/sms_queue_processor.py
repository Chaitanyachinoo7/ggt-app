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


def task_process_sms_queue(batch_size=10000, offset=0):
    print('********************task_process_SMS_queue****************************')

    sql = """
        SELECT count(*) as total FROM sms_notification_queue where status IN ('pending','retry')
    """
    row = replica_read_row(sql,)
    total_count = row['total']

    if batch_size < total_count:
        total_count = batch_size

    micro_batch_size = 50
    batch_count = math.ceil(total_count/micro_batch_size)

    for i in range(batch_count):
        micro_offset = offset + (micro_batch_size * i)
        __batch_process_sms_queue(micro_batch_size, micro_offset)

    print('************************ END ************************\n\n')


def __batch_process_sms_queue(micro_offset, micro_batch_size):
    sql = """
    SELECT * 
    FROM sms_notification_queue 
    WHERE status 
        IN ('pending','retry') 
    ORDER BY create_dt DESC
    LIMIT {},{}
    """.format(micro_offset, micro_batch_size)

    rows = replica_read_rows(sql)

    for row in rows:
        _id = row['id']
        status = row['status']
        to_number = row['to_number']
        message = row['message']
        priority = row['priority']
        if status == 'retry':
            if send_sms(to_number, message, priority):
                update_sms_status_to_processed(_id)
            else:
                update_sms_status_to_error(_id)
        else:
            if send_sms(to_number, message, priority):
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
