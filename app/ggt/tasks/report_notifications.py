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

from ggt.lib.email import render_template

import ggt.lib.constants as c

session_id = generate_session_id()


async def task_schedule_result_notifications_and_followups():
    print('\n\n************************************************\n\n')
    print('create_result_notification_campaign')
    await create_result_notification_campaign()
    print('schedule_notifications_using_sms')
    await schedule_notifications_using_sms()
    print('schedule_notifications_using_email')
    await schedule_notifications_using_email()
    print('schedule_positive_followups')
    await schedule_positive_followups()

    print('\n\n************************************************\n\n')


async def create_result_notification_campaign():
    sql = """
    INSERT INTO result_notification_campaigns
        (test_id,
        patient_id,
        token,
        phone_number,
        email,
        first_name,
        last_name,
        dob)

    SELECT 
        test_samples.id AS test_id,
        test_samples.patient_id AS patient_id,
        patients.token AS token,
        patients.phone_number AS phone_number,
        patients.email AS email,
        patients.first_name AS first_name,
        patients.last_name AS last_name,
        patients.dob AS dob
    FROM
        (test_samples
        JOIN patients ON ((patients.id = test_samples.patient_id)))
    WHERE
        test_samples.test_result IS NOT NULL
            AND test_samples.status <> 'final'
        
    ON DUPLICATE KEY UPDATE test_id=test_id

    """
    vals = ()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='BEGIN - Creating result notification campaign')

    await exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Creating result notification campaign')


async def schedule_positive_followups():
    sql = """
    INSERT INTO positive_result_followup_queue
        (test_id,
        patient_id,
        phone_number,
        email,
        first_name,
        last_name,
        dob)

    SELECT 
        test_samples.id AS test_id,
        test_samples.patient_id AS patient_id,
        patients.phone_number AS phone_number,
        patients.email AS email,
        patients.first_name AS first_name,
        patients.last_name AS last_name,
        patients.dob AS dob
    FROM
        (test_samples
        JOIN patients ON ((patients.id = test_samples.patient_id)))
    WHERE
        test_samples.test_result = 'pos'
            AND test_samples.status <> 'final'
        
    ON DUPLICATE KEY UPDATE test_id=test_id

    """
    vals = ()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='BEGIN - Scheduling Positive Report Followup sessions')

    await exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Scheduling Positive Report Followup sessions')


async def schedule_notifications_using_sms():
    sql = """
        SELECT * FROM result_notification_campaigns
        WHERE overall_status = 'scheduled'
    """
    rows = await replica_read_rows(sql)

    # ---
    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        first_name = row['first_name'].strip()
        token = row['token']
        phone_number = row['phone_number']
        data.append(
            (phone_number, formatted_sms_message(first_name, token))
        )
        test_id_list.append(
            test_id
        )

    await batch_enqueue_sms_notifications(data)
    await batch_update_notification_queue_status_to_pending(
        str(test_id_list).strip('[]')
    )


async def schedule_notifications_using_email():
    batch_size = 100
    sql = """
        SELECT count(*) as total
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
    """
    row = await replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)
    
    for _ in range(limit):
        print('*')
        await __batch_schedule_notifications_using_email(batch_size)


async def __batch_schedule_notifications_using_email(batch_size=100):
    sql = """
        SELECT * 
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
        LIMIT {}
    """.format(batch_size)
    rows = await replica_read_rows(sql)

    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        email = await formatted_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
            email['to_email'], email['subject'], email['html_content'])
        )
        test_id_list.append(
            test_id
        )

    if await batch_enqueue_email_notifications(data):
        await batch_update_notification_queue_status_for_email(
            str(test_id_list).strip('[]')
        )

async def formatted_email_message(row):
    base_url = cfg('base_url')
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = cfg('notifications.result_subject')

    template_vars = {
        "first_name": row['first_name'],
        "result_link": "{}/r/{}".format(base_url, row['token'])
    }

    template_name = cfg('notifications.result_template')
    html_content = await render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


async def add_to_healthtrackrx_inbound_data_table():
    rows = await get_all_lab_records_from_cache()
    try:
        sql = """
            INSERT INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        await exec_batch_execute(sql, rows)

    except Exception as err:
        print("err:", err)


def formatted_sms_message(first_name, token):
    base_url = cfg('base_url')
    return "Hi {}, your COVID-19 test results are ready. " \
           "Follow this link to view {}/r/{} reply STOP to cancel msgs".format(
               first_name, base_url, token)


# TODO: Bulk insert into Table instead of 1 query at a time
async def add_to_sms_queue(phone_number, message):
    sql = """
        INSERT INTO sms_notification_queue
        (to_number,message)
        VALUES
        (%s, %s);
    """
    vals = (phone_number, message)
    await exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        phone_number=phone_number,
        message=message,
        info='SMS Queued for delivery')

    return True


# TODO: complete this
async def batch_update_notification_queue_status_for_email(test_id_list):
    try:
        sql = """
            UPDATE result_notification_campaigns
            SET
                email_sent = 1,
                email_dt = NOW(),
                update_dt = NOW()
            WHERE 
                test_id IN ({})
                AND test_id <> 0
            """.format(test_id_list)
        await exec_update(sql)

    except Exception as err:
        print("err:", err)


async def update_notification_queue_status_to_pending(test_id):
    try:
        sql = """
            UPDATE result_notification_campaigns
            SET
            overall_status = 'pending',
            update_dt = NOW()
            WHERE test_id = %s
            """
        vals = (test_id,)
        await exec_update(sql, vals)

    except Exception as err:
        print("err:", err)


async def batch_enqueue_sms_notifications(data):
    try:
        sql = """
            INSERT INTO sms_notification_queue
                (to_number,message)
            VALUES
                (%s, %s);
        """
        await exec_batch_execute(sql, data)

    except Exception as err:
        print("err:", err)


async def batch_enqueue_email_notifications(data):
    try:
        sql = """
            INSERT INTO email_notification_queue
                (from_email, from_name, to_email, subject, html_content)
            VALUES
                (%s, %s, %s, %s, %s);
        """
        await exec_batch_execute(sql, data)
        return True

    except Exception as err:
        print("err:", err)
        return False


async def batch_update_notification_queue_status_to_pending(test_id_list):
    sql = """
        UPDATE result_notification_campaigns
        SET
            overall_status = 'pending',
            sms_sent = 1,
            sms_dt = NOW(),
            update_dt = NOW()
        WHERE 
            test_id IN ({})
            AND test_id <> 0
        """.format(test_id_list)
    await exec_update(sql)
