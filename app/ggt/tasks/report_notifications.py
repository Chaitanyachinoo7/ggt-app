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


session_id = generate_session_id()


def task_schedule_result_notifications_and_followups():
    schedule_negative_notifications()
    schedule_positive_notifications()
    schedule_negative_notification_using_sms()


def schedule_negative_notifications():
    sql = """
    INSERT INTO negative_result_notification_queue
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
        test_samples.test_result = 'neg'
            AND test_samples.status <> 'final'
        
    ON DUPLICATE KEY UPDATE test_id=test_id

    """
    vals = ()

    log_generic(
        type="info",
        function='task_process_negative_notifications',
        task_session_id=session_id,
        info='BEGIN - Scheduling Negative Report Notifications for delivery')

    exec_insert(sql, vals)

    log_generic(
        type="info",
        function='task_process_negative_notifications',
        task_session_id=session_id,
        info='COMPLETED - Scheduling Negative Report Notifications for delivery')


def schedule_positive_notifications():
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
        type="info",
        function='task_process_positive_notifications',
        task_session_id=session_id,
        info='BEGIN - Scheduling Positive Report Followup sessions')

    exec_insert(sql, vals)

    log_generic(
        type="info",
        function='task_process_positive_notifications',
        task_session_id=session_id,
        info='COMPLETED - Scheduling Positive Report Followup sessions')


def schedule_negative_notification_using_sms():
    sql = """
        SELECT * FROM negative_result_notification_queue
        WHERE overall_status = 'scheduled'
    """
    rows = read_rows(sql)
    for row in rows:
        test_id = row['test_id']
        first_name = row['first_name'].strip()
        token = row['token']
        phone_number = row['phone_number']

        if add_to_sms_queue(
                phone_number,
                formatted_sms_message(first_name, token)):
            # TODO: update to pending until patient acknowledges the message. If not, try other means of communication
            update_notification_queue_status_to_pending(test_id)


def formatted_sms_message(first_name, token):
    base_url = get_config_val('base_url')
    return "Hi {}, your GoGetTested.com COVID-19 test results are available. Please follow this link to view your results {}/r/{}".format(first_name, base_url, token)


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
        type="info",
        function='add_to_sms_queue',
        task_session_id=session_id,
        phone_number=phone_number,
        message=message,
        info='SMS Queued for delivery')

    return True


def update_notification_queue_status_to_pending(test_id):
    sql = """
        UPDATE negative_result_notification_queue
        SET
        overall_status = 'pending',
        update_dt = NOW()
        WHERE test_id = %s
        """
    val = (test_id,)
    exec_update(sql, val)
