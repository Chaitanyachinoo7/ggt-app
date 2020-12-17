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

from ggt.lib.email import send_email, render_template

import ggt.lib.constants as c


async def task_process_email_queue():
    print('\n\n********************task_process_email_queue****************************\n\n')

    batch_size = 100
    sql = """
        SELECT count(*) as total FROM email_notification_queue where status IN ('pending','retry')
    """
    row = replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)

    for _ in range(limit):
        await __batch_process_email_queue(batch_size)

    print('\n\n************************************************\n\n')


async def __batch_process_email_queue(batch_size=100):
    sql = """
    SELECT * FROM email_notification_queue 
    WHERE status 
        IN ('pending','retry') 
    ORDER BY ID
    LIMIT {}
    """.format(batch_size)
    rows = read_rows(sql)
    for row in rows:
        _id = row['id']
        status = row['status']
        from_email = row['from_email']
        from_name = row['from_name']
        to_email = row['to_email']
        subject = row['subject']
        html_content = row['html_content']

        if status == 'retry':
            if send_email(from_email, from_name, to_email, subject, html_content):
                await update_email_status_to_processed(_id)
            else:
                await update_email_status_to_error(_id)
        else:
            if await send_email(from_email, from_name, to_email, subject, html_content):
                await update_email_status_to_processed(_id)
            else:
                await update_email_status_to_retry(_id)


async def update_email_status_to_processed(id):
    sql = """
        UPDATE email_notification_queue
        SET
        status = 'processed',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)


async def update_email_status_to_retry(id):
    sql = """
        UPDATE email_notification_queue
        SET
        status = 'retry',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)


async def update_email_status_to_error(id):
    sql = """
        UPDATE email_notification_queue
        SET
        status = 'error',
        update_dt = NOW()
        WHERE `id` = %s
    """
    vals = (id,)
    exec_update(sql, vals)


'''
def test_email():
    template_vars = {
        "first_name": "Suresh",
        "test_number": "f4gv34-001",
        "test_location_line1": "Gregory Swanson",
        "test_location_line2": "26 Caesar Canyon Suite 723,",
        "test_location_line3": "West Newell, 62418",
        "test_date": "August 01, 2020",
        "test_time": "11:15AM to 11:30AM",
        "appointment_link": "https://start.gogettested.com/appointment/400800"
    }

    # generate HTML from template
    template_name = 'GGT-1-APPOINTMENT-CONFIRMATION-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    from_email = "support@gogettested.com"
    from_name = "Go Get Tested"
    to_email = "suresh@wellpay.com"
    subject = "COVID-19 Testing Appointment Confirmation"

    send_email(from_email, from_name, to_email, subject, html_content)


def test_email2():
    try:
        template_vars = {
            "first_name": "Suresh",
            "result_link": "https://start.gogettested.com/r/xxxxxxxxxxxxxxxxxxxxxxx"
        }

        # generate HTML from template
        template_name = 'GGT-5-RESULT-AVAILABLE-EMAIL.html'
        html_content = render_template(template_name, **template_vars)

        from_email = "support@gogettested.com"
        from_name = "Go Get Tested"
        to_email = "sureshd@gmail.com"
        subject = "COVID-19 Testing Result Available"

        send_email(from_email, from_name, to_email, subject, html_content)

    except Exception as err:
        print(err)
'''
