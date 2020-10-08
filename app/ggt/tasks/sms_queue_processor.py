from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_rows
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
    print('\n\n************************************************\n\n')

    sql = """
    SELECT * FROM sms_notification_queue where status = 'pending'
    """
    rows = read_rows(sql)
    for row in rows:
        id = row['id']
        to_number = row['to_number']
        message = row['message']
        if send_sms(to_number, message):
            update_sms_status_to_processed(id)

    print('\n\n************************************************\n\n')


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
