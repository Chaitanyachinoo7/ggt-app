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

from ggt.lib.email import send_email, render_template


def task_process_email_queue():
    print('\n\n********************task_process_email_queue****************************\n\n')

    sql = """
    SELECT * FROM email_notification_queue where status = 'pending'
    """
    rows = read_rows(sql)
    for row in rows:
        email_id = row['id']
        from_email = row['from_email']
        from_name = row['from_name']
        to_email = row['to_email']
        subject = row['subject']
        html_content = row['html_content']
        if send_email(from_email, from_name, to_email, subject, html_content):
            update_email_status_to_processed(email_id)

    print('\n\n************************************************\n\n')


def update_email_status_to_processed(id):
    sql = """
        UPDATE email_notification_queue
        SET
        status = 'processed',
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