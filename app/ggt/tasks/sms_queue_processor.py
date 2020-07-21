from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_rows
)

from ggt.lib.sms import send_sms

def task_process_sms_queue():
    sql = """
    SELECT * FROM ggt.sms_notification_queue where status = 'pending'
    """
    rows = read_rows(sql)
    for row in rows:
        id = row['id']
        to_number = row['to_number']
        message = row['message']
        if send_sms(to_number, message):
            update_sms_status_to_processed(id)


def update_sms_status_to_processed(id):
    sql = """
        UPDATE sms_notification_queue
        SET
        status = 'processed',
        update_dt = NOW()
        WHERE `id` = %s
    """
    val = (id,)
    exec_update(sql, val)    
