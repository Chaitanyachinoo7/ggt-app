import base64
import ujson

from ggt.lib.storage import (
    upload_archived_notification_from_base64_string
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
    INFO
)
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

session_id = generate_session_id()
bucket_name = get_config_val('gcp.notification_archive_bucket_name')
limit = 100


def archive_processed_email_notifications():
    print('\n\n************************************************\n\n')
    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Archiving processed email notifications')

    print('Archiving processed email notifications')
    keep_processing = True

    while keep_processing:
        rows = get_available_email_notifications(limit)
        if len(rows) == 0:
            break
        if insert_email_archive_table(rows):
            if archive_email_notifications(rows):
                delete_archived_email_record()

    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End of archiving processed email notifications')
    print('\n\n************************************************\n\n')


def archive_processed_sms_notifications():
    print('\n\n************************************************\n\n')
    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Archiving processed sms notifications')

    print('Archiving processed sms notifications')
    keep_processing = True

    while keep_processing:
        rows = get_available_sms_notifications(limit)
        if len(rows) == 0:
            break
        insert_sms_archive_table(rows)
        archive_sms_notifications(rows)
        delete_archived_sms_record()

    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End of archiving processed sms notifications')
    print('\n\n************************************************\n\n')


def get_available_email_notifications(limit):
    sql = """SELECT 
                    *
                FROM
                    email_notification_queue
                WHERE
                    status = 'processed'
                ORDER BY id
                LIMIT {};""".format(limit)
    return read_rows(sql)


def get_available_sms_notifications(limit):
    sql = """SELECT 
                    *
                FROM
                    sms_notification_queue
                WHERE
                    status = 'processed'
                ORDER BY id
                LIMIT {};""".format(limit)
    return read_rows(sql)


def insert_email_archive_table(records):
    print('Archiving  {} email notifications'.format(len(records)))
    sql = """INSERT IGNORE INTO archived_email_notification
            (id,
            from_email,
            from_name,
            to_email,
            subject,
            create_dt,
            update_dt)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s);"""

    vals = []
    for record in records:
        val = (
            record['id'],
            record['from_email'],
            record['from_name'],
            record['to_email'],
            record['subject'],
            record['create_dt'],
            record['update_dt']
        )
        vals.append(val)
    return exec_batch_execute(sql, tuple(vals))


def insert_sms_archive_table(records):
    print('Archiving  {} sms notifications'.format(len(records)))
    sql = """INSERT INTO archived_sms_notification
            (id,
            to_number,
            create_dt,
            update_dt)
            VALUES
            (%s, %s, %s, %s);"""

    vals = []
    for record in records:
        val = (
            record['id'],
            record['to_number'],
            record['create_dt'],
            record['update_dt']
        )
        vals.append(val)
    return exec_batch_execute(sql, tuple(vals))


def delete_archived_email_record():
    print("Deleting archived records from email_notification_queue.")
    sql = """DELETE FROM email_notification_queue 
                WHERE
                    id IN (SELECT 
                            temp.id
                            FROM
                            (SELECT 
                                en.id AS id
                            FROM
                                email_notification_queue AS en
                            INNER JOIN archived_email_notification AS an 
                                ON en.id = an.id) as 
                            temp);"""
    return exec_delete(sql)


def delete_archived_sms_record():
    print("Deleting archived records from sms_notification_queue.")
    sql = """DELETE FROM sms_notification_queue 
                WHERE
                    id IN (SELECT 
                            temp.id
                            FROM
                            (SELECT 
                                en.id AS id
                            FROM
                                sms_notification_queue AS en
                            INNER JOIN archived_sms_notification AS an 
                                ON en.id = an.id) as 
                            temp);"""
    return exec_delete(sql)


def archive_sms_notifications(records):
    print("Uploading sms archives to the bucket")
    for rec in records:
        note = rec['message']
        note = str(note)
        destination_blob_name = "{}_sms_{}_{}.json".format(
            rec['id'], rec['to_number'],  rec['update_dt'])
        upload_archived_notification(note, destination_blob_name)


def archive_email_notifications(records):
    print("Uploading email archives to the bucket")
    for rec in records:
        note = rec['html_content']
        note = str(note)
        destination_blob_name = "{}_email_{}_{}.json".format(
            rec['id'], rec['to_email'],  rec['update_dt'])
        upload_archived_notification(note, destination_blob_name)


def upload_archived_notification(notification, destination_blob_name):
    content_type = 'application/json'
    notification = {"notification": notification}
    notification = ujson.dumps(notification)
    notification = base64.b64encode(notification.encode('utf-8'))
    return upload_archived_notification_from_base64_string(
        bucket_name, 
        notification,
        content_type, 
        destination_blob_name
    )


def archive_processed_notifications():
    archive_processed_email_notifications()
    archive_processed_sms_notifications()
