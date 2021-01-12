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


def task_schedule_result_notifications_and_followups():
    print('\n\n************************************************\n\n')
    print('create_result_notification_campaign')
    create_result_notification_campaign()
    print('schedule_result_notifications_using_sms')
    schedule_result_notifications_using_sms()
    print('schedule_result_notifications_using_email')
    schedule_result_notifications_using_email()

    #create_rejects_notification_campaign()
    print('schedule_rejects_notifications_using_sms')
    #schedule_rejects_notifications_using_sms()
    print('schedule_rejects_notifications_using_email')
    #schedule_rejects_notifications_using_email()

    
    print('create_96_hour_delayed_result_notification_campaign')
    #create_96_hour_delayed_result_notification_campaign()
    print('schedule_96_hour_delayed_result_notifications_using_sms')
    #schedule_96_hour_delayed_result_notifications_using_sms()
    print('schedule_96_hour_delayed_result_notifications_using_email')
    #schedule_96_hour_delayed_result_notifications_using_email()
    

    print('schedule_positive_followups')
    schedule_positive_followups()

    print('\n\n************************************************\n\n')


def create_result_notification_campaign():
    sql = """
    INSERT IGNORE INTO result_notification_campaigns
        (test_id,
        patient_id,
        token,
        phone_number,
        email,
        first_name,
        last_name,
        dob,
        message_type)

    SELECT 
        test_samples.id AS test_id,
        test_samples.patient_id AS patient_id,
        patients.token AS token,
        patients.phone_number AS phone_number,
        patients.email AS email,
        patients.first_name AS first_name,
        patients.last_name AS last_name,
        patients.dob AS dob,
        'result'
    FROM
        (test_samples
        JOIN patients ON ((patients.id = test_samples.patient_id)))
    WHERE
        test_samples.test_result IS NOT NULL
            AND test_samples.status = 'lab_result_received'
    """
    vals = ()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='BEGIN - Creating result notification campaign')

    exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Creating result notification campaign')

###
# BEGIN REJECTS BLOCK
###


def create_rejects_notification_campaign():
    sql = """
    INSERT IGNORE INTO result_notification_campaigns
        (test_id,
        patient_id,
        token,
        phone_number,
        email,
        first_name,
        last_name,
        dob,
        message_type)

    SELECT 
        test_samples.id AS test_id,
        test_samples.patient_id AS patient_id,
        patients.token AS token,
        patients.phone_number AS phone_number,
        patients.email AS email,
        patients.first_name AS first_name,
        patients.last_name AS last_name,
        patients.dob AS dob,
        'reject'
    FROM
        (test_samples
        JOIN patients ON ((patients.id = test_samples.patient_id)))
    WHERE
        test_samples.status = 'rejected'
    """
    vals = ()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='BEGIN - Creating REJECTED result notification campaign')

    exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Creating REJECTED result notification campaign')


def schedule_rejects_notifications_using_sms():
    sql = """
        SELECT 
            *
        FROM
            result_notification_campaigns
        WHERE
            overall_status <> 'final_notified' 
            AND (sms_sent is NULL OR sms_sent = 0)
            AND message_type = 'reject'
    """
    rows = replica_read_rows(sql)

    # ---
    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        first_name = row['first_name'].strip()
        phone_number = row['phone_number']
        data.append(
            (phone_number, formatted_rejects_sms_message(first_name))
        )
        test_id_list.append(
            test_id
        )

    batch_enqueue_sms_notifications(data)
    batch_update_notification_queue_status_to_pending(
        str(test_id_list).strip('[]')
    )


def formatted_rejects_sms_message(first_name):
    return "Hi {}, we regret to inform you that our lab partner was not able to return a COVID-19 test result from the sample provided. " \
        "Though rare, these instances can happen for multiple reasons including an insufficient saliva sample provided, " \
        "a loose vial leaking in transport, or an inconclusive lab result. We encourage you to visit GoGetTested.com and register " \
        "for another test as soon as possible.".format(first_name)


def schedule_rejects_notifications_using_email():
    batch_size = 100
    sql = """
        SELECT count(*) as total
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = 'reject'
    """
    row = replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)

    for _ in range(limit):
        __batch_schedule_rejects_notifications_using_email(batch_size)


def __batch_schedule_rejects_notifications_using_email(batch_size=100):
    sql = """
        SELECT * 
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = 'reject'
        LIMIT {}
    """.format(batch_size)
    rows = replica_read_rows(sql)

    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        email = formatted_rejects_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
             email['to_email'], email['subject'], email['html_content'])
        )
        test_id_list.append(
            test_id
        )

    if batch_enqueue_email_notifications(data):
        batch_update_notification_queue_status_for_email(
            str(test_id_list).strip('[]')
        )


def formatted_rejects_email_message(row):
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = 'An important update regarding your COVID-19 Test' #cfg('notifications.result_subject')

    template_vars = {
        "first_name": row['first_name']
    }
    
    template_name = 'GGT-16-RESULT-REJECTED.html' # cfg('notifications.result_template')
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


###
# END REJECTS BLOCK
###


def schedule_positive_followups():
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

    exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Scheduling Positive Report Followup sessions')

###
# BEGIN RESULTING BLOCK
###


def schedule_result_notifications_using_sms():
    sql = """
        SELECT 
            *
        FROM
            result_notification_campaigns
        WHERE
            overall_status = 'scheduled'
                AND message_type = 'result'
    """
    rows = replica_read_rows(sql)

    # ---
    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        first_name = row['first_name'].strip()
        token = row['token']
        phone_number = row['phone_number']
        data.append(
            (phone_number, formatted_result_sms_message(first_name, token))
        )
        test_id_list.append(
            test_id
        )

    batch_enqueue_sms_notifications(data)
    batch_update_notification_queue_status_to_pending(
        str(test_id_list).strip('[]')
    )


def schedule_result_notifications_using_email():
    batch_size = 100
    sql = """
        SELECT count(*) as total
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = 'result'
    """
    row = replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)

    for _ in range(limit):
        __batch_schedule_result_notifications_using_email(batch_size)


def __batch_schedule_result_notifications_using_email(batch_size=100):
    sql = """
        SELECT * 
        FROM result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = 'result'
        LIMIT {}
    """.format(batch_size)
    rows = replica_read_rows(sql)

    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        email = formatted_result_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
             email['to_email'], email['subject'], email['html_content'])
        )
        test_id_list.append(
            test_id
        )

    if batch_enqueue_email_notifications(data):
        batch_update_notification_queue_status_for_email(
            str(test_id_list).strip('[]')
        )


def formatted_result_email_message(row):
    base_url = cfg('base_url')
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = cfg('notifications.result_subject')

    template_vars = {
        "first_name": row['first_name'],
        "result_link": "{}/r/{}".format(base_url, row['token'])
    }

    template_name = cfg('notifications.result_template')
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message

###
# /// END RESULTING BLOCK
###


###
# /// BEGIN 96 Hour Delayed RESULTING BLOCK
###
def create_96_hour_delayed_result_notification_campaign():
    sql = """
    INSERT IGNORE INTO delayed_result_notification_campaigns
        (test_id,
        message_type,
        patient_id,
        phone_number,
        email,
        first_name,
        last_name
        )

    SELECT 
        test_samples.id AS test_id,
        '96_hour_delay' AS message_type,
        test_samples.patient_id AS patient_id,
        patients.phone_number AS phone_number,
        patients.email AS email,
        patients.first_name AS first_name,
        patients.last_name AS last_name
    FROM
        (test_samples
        JOIN patients ON ((patients.id = test_samples.patient_id)))
            JOIN
        locations ON (locations.id = test_samples.sample_collection_location_id)
    WHERE
        test_samples.test_result IS NULL
            AND locations.st <> 'KS'
            AND test_samples.status = 'with_lab'
            AND HOUR(TIMEDIFF(NOW(),
                    test_samples.lab_electronic_submission_dt)) > 96
            AND HOUR(TIMEDIFF(NOW(),
                    test_samples.lab_electronic_submission_dt)) < 170
    """
    vals = ()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='BEGIN - Creating 96 Hour Delayed result notification campaign')

    exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='COMPLETED - Creating 96 Hour Delayed result notification campaign')


def schedule_96_hour_delayed_result_notifications_using_sms():
    sql = """
        SELECT 
            *
        FROM
            delayed_result_notification_campaigns
        WHERE
            overall_status <> 'final_notified' 
                AND (sms_sent is NULL OR sms_sent = 0)
                AND message_type = '96_hour_delay'
    """
    rows = replica_read_rows(sql)

    # ---
    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        first_name = row['first_name'].strip()
        phone_number = row['phone_number']
        data.append(
            (phone_number, formatted_96_hour_delayed_result_sms_message(first_name))
        )
        test_id_list.append(
            test_id
        )

    batch_enqueue_sms_notifications(data)
    batch_update_delayed_result_notifications_sms_status_to_pending(
        str(test_id_list).strip('[]')
    )


def batch_update_delayed_result_notifications_sms_status_to_pending(test_id_list):
    sql = """
        UPDATE delayed_result_notification_campaigns
        SET
            overall_status = 'pending',
            sms_sent = 1,
            sms_dt = NOW(),
            update_dt = NOW()
        WHERE 
            test_id IN ({})
            AND test_id <> 0
        """.format(test_id_list)
    exec_update(sql)


def schedule_96_hour_delayed_result_notifications_using_email():
    batch_size = 100
    sql = """
        SELECT count(*) as total
        FROM delayed_result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = '96_hour_delay'
    """
    row = replica_read_row(sql,)
    total_count = row['total']
    limit = math.ceil(total_count/batch_size)

    for _ in range(limit):
        __batch_schedule_96_hour_delayed_result_notifications_using_email(
            batch_size)


def __batch_schedule_96_hour_delayed_result_notifications_using_email(batch_size=100):
    sql = """
        SELECT * 
        FROM delayed_result_notification_campaigns 
        WHERE overall_status <> 'final_notified' 
            AND (email_sent is NULL OR email_sent = 0)
            AND message_type = '96_hour_delay'
        LIMIT {}
    """.format(batch_size)
    rows = replica_read_rows(sql)

    data = []
    test_id_list = []

    for row in rows:
        test_id = row['test_id']
        email = formatted_96_hour_delayed_result_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
             email['to_email'], email['subject'], email['html_content'])
        )
        test_id_list.append(
            test_id
        )

    if batch_enqueue_email_notifications(data):
        batch_update_delayed_result_notification_queue_status_for_email(
            str(test_id_list).strip('[]')
        )


def batch_update_delayed_result_notification_queue_status_for_email(test_id_list):
    try:
        sql = """
            UPDATE delayed_result_notification_campaigns
            SET
                email_sent = 1,
                email_dt = NOW(),
                update_dt = NOW()
            WHERE 
                test_id IN ({})
                AND test_id <> 0
            """.format(test_id_list)
        exec_update(sql)

    except Exception as err:
        print("err:", err)


def formatted_96_hour_delayed_result_email_message(row):
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = 'An important update regarding your COVID-19 Test' #cfg('notifications.result_subject')

    template_vars = {
        "first_name": row['first_name']
    }

    # cfg('notifications.result_template')
    template_name = 'GGT-13-RESULT-DELAYED-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


def formatted_96_hour_delayed_result_sms_message(first_name):
    return "Hi {}, we wanted to let you know that there is currently a delay in receiving your COVID-19 test result. " \
        "Our lab partner is working hard to process results as fast as possible. Thank you for your patience with us as we continue to offer testing services." \
        "\nReply STOP to cancel msgs".format(first_name)

###
# /// END 96 Hour Delayed RESULTING BLOCK
###


def add_to_healthtrackrx_inbound_data_table():
    rows = get_all_lab_records_from_cache()
    try:
        sql = """
            INSERT INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        sql = """
            INSERT IGNORE INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
        """
        exec_batch_execute(sql, rows)

    except Exception as err:
        print("err:", err)


def formatted_result_sms_message(first_name, token):
    base_url = cfg('base_url')
    return "Hi {}, your COVID-19 test results are ready. " \
           "Follow this link to view {}/r/{} reply STOP to cancel msgs".format(
               first_name, base_url, token)


# TODO: Bulk insert into Table instead of 1 query at a time
def add_to_sms_queue(phone_number, message):
    sql = """
        INSERT INTO sms_notification_queue
        (to_number,message)
        VALUES
        (%s, %s);
    """
    vals = (phone_number, message)
    exec_insert(sql, vals)

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        phone_number=phone_number,
        message=message,
        info='SMS Queued for delivery')

    return True


# TODO: complete this
def batch_update_notification_queue_status_for_email(test_id_list):
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
        exec_update(sql)

    except Exception as err:
        print("err:", err)


def update_notification_queue_status_to_pending(test_id):
    try:
        sql = """
            UPDATE result_notification_campaigns
            SET
            overall_status = 'pending',
            update_dt = NOW()
            WHERE test_id = %s
            """
        vals = (test_id,)
        exec_update(sql, vals)

    except Exception as err:
        print("err:", err)


def batch_enqueue_sms_notifications(data):
    try:
        sql = """
            INSERT INTO sms_notification_queue
                (to_number,message)
            VALUES
                (%s, %s);
        """
        exec_batch_execute(sql, data)

    except Exception as err:
        print("err:", err)


def batch_enqueue_email_notifications(data):
    try:
        sql = """
            INSERT INTO email_notification_queue
                (from_email, from_name, to_email, subject, html_content, priority)
            VALUES
                (%s, %s, %s, %s, %s, %s);
        """
        exec_batch_execute(sql, data)
        return True

    except Exception as err:
        print("err:", err)
        return False


def batch_update_notification_queue_status_to_pending(test_id_list):
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
    exec_update(sql)
