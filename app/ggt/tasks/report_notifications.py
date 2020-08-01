from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_batch_execute,
    exec_update,
    read_rows
)


session_id = generate_session_id()


def task_schedule_result_notifications_and_followups():
    print('\n\n************************************************\n\n')
    create_result_notification_campaign()
    schedule_notifications_using_sms()
    schedule_positive_followups()
    
    print('\n\n************************************************\n\n')


def create_result_notification_campaign():
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
        type="info",
        function='create_result_notification_campaign',
        task_session_id=session_id,
        info='BEGIN - Creating result notification campaign')

    exec_insert(sql, vals)

    log_generic(
        type="info",
        function='create_result_notification_campaign',
        task_session_id=session_id,
        info='COMPLETED - Creating result notification campaign')


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



def schedule_notifications_using_sms():
    sql = """
        SELECT * FROM result_notification_campaigns
        WHERE overall_status = 'scheduled'
    """
    rows = read_rows(sql)

    ##---
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

    batch_enqueue_sms_notifications(data)
    batch_update_notification_queue_status_to_pending(
        str(test_id_list).strip('[]')
    )



def add_to_healthtrackrx_inbound_data_table():
    rows = get_all_lab_records_from_cache()
    try:
        sql = """
            INSERT INTO healthtrackrx_inbound_data
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result)
            VALUES (%s,%s,%s,%s, %s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE requisition_id=requisition_id
        """
        exec_batch_execute(sql, rows)

    except Exception as err:
        print("err:", err)




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
    try:
        sql = """
            UPDATE result_notification_campaigns
            SET
            overall_status = 'pending',
            update_dt = NOW()
            WHERE test_id = %s
            """
        val = (test_id,)
        exec_update(sql, val)

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


def batch_update_notification_queue_status_to_pending(test_id_list):
    sql = """
        UPDATE result_notification_campaigns
        SET
            overall_status = 'pending',
            update_dt = NOW()
        WHERE 
            test_id IN ({})
            AND test_id <> 0
        """.format(test_id_list)
    exec_update(sql)
