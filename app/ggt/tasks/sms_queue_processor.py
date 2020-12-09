from ggt.lib.utils import (
    get_config_val,
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

async def task_process_sms_queue():
    print('\n\n************************************************\n\n')

    sql = """
    SELECT * FROM sms_notification_queue where status IN ('pending','retry') ORDER BY ID DESC
    """
    rows = await replica_read_rows(sql)
    for row in rows:
        _id = row['id']
        status = row['status']
        to_number = row['to_number']
        message = row['message']

        if status == 'retry':
            if await send_sms(to_number, message):
                await update_sms_status_to_processed(_id)
            else:
                await update_sms_status_to_error(_id)
        else:
            if await send_sms(to_number, message):
                await update_sms_status_to_processed(_id)
            else:
                await update_sms_status_to_retry(_id)

    print('\n\n************************************************\n\n')


async def update_sms_status_to_processed(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'processed',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    await exec_update(sql, vals)    


async def update_sms_status_to_retry(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'retry',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    await exec_update(sql, vals)    


async def update_sms_status_to_error(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'error',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    await exec_update(sql, vals)    
