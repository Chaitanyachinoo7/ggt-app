import os
import glob
import csv
import datetime
import paramiko
import base64
import random
from PIL import Image

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

from ggt.lib.storage import (
    file_exists_in_insurance_cards,
    upload_insurance_card_from_base64_string
)

from ggt.lib.email import render_template

import ggt.lib.constants as c


from ggt.lib.storage import (
    get_file_blob
)

import ggt.lib.constants as c

session_id = generate_session_id()
local_outbound_file_path = cfg('vendors.healthtrackrx.outbound.local_outbound_file_path')
outbound_file_prefix = cfg('vendors.healthtrackrx.outbound.outbound_file_prefix')
local_insurance_card_file_path = cfg('vendors.healthtrackrx.outbound.local_insurance_card_file_path')

def task_process_misc():
    print('\n\n************************************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing Misc Task')

    # upload_insurance_images_to_gcp()
    # sync_appointments_with_schedule_slots()
    # upload_insurance_images_to_gcp_with_small_table()
    #process_email_notifications()
    #upload_insurance_files_from_gstore()
    process_sms_notifications()
    process_email_notifications()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing Misc Task')
    print('\n\n************************************************\n\n')



def upload_insurance_files_from_gstore():
    try:
        print('converting insurance image files to PDF')
        file_buffer = []
        orders = []


        for appointment_id in orders:
            try:
                file_path_png = "{}/{}_001.png".format(local_insurance_card_file_path, appointment_id)
                filename = "{}_001.pdf".format(appointment_id)
                file_path_pdf = "{}/{}".format(local_insurance_card_file_path, filename)
                blob = get_file_blob('ggt-insurance-cards-prod', '{}.png'.format(appointment_id))
                if blob:
                    blob.download_to_filename(file_path_png)
                    Image.open(file_path_png).convert('RGB').save(file_path_pdf)
                    file_buffer.append((filename, file_path_pdf))

            except Exception as err:
                print(err)    
        
        print('uploading insurance files to FTP')
        upload_file_list_to_ftp(file_buffer)

    except Exception as err:
        print(err)

'''
def upload_file_list_to_ftp(file_list):
    try:
        hostname = cfg('vendors.healthtrackrx_outbound.hostname')
        username = cfg('vendors.healthtrackrx_outbound.username')
        password = cfg('vendors.healthtrackrx_outbound.password')
        port = cfg('vendors.healthtrackrx_outbound.port')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()

        for f in file_list:
            filename = f[0]
            local_file_path = f[1]
            remotepath = "{}/{}".format('', filename)
            ftp_client.put(local_file_path, remotepath)


    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()
'''

def process_sms_notifications():
    rows = get_appointments()
    data = []
    for row in rows:
        phone_number = row['phone_number']
        data.append(
            (phone_number, prepare_sms_text(row))
        )

    batch_enqueue_sms_notifications(data)


def process_email_notifications():
    rows = get_appointments()
    data = []

    for row in rows:
        email = formatted_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
             email['to_email'], email['subject'], email['html_content'])
        )

    batch_enqueue_email_notifications(data)


def formatted_email_message(row):
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    #subject = "IMPORTANT: {}, Your Covid-19 Testing location has closed due to inclement weather".format(row['first_name'])
    subject = "IMPORTANT: {}, Your Covid-19 Testing hours have changed".format(row['first_name'])

    template_vars = {
        "first_name": row['first_name']
    }

    #template_name = 'GGT-14-APPOINTMENT-WEATHER-CLOSING-EMAIL.html'
    template_name = 'GGT-9-APPOINTMENT-DELAYED-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


def batch_enqueue_email_notifications(data):
    try:
        sql = """
            INSERT INTO email_notification_queue
                (from_email, from_name, to_email, subject, html_content)
            VALUES
                (%s, %s, %s, %s, %s);
        """
        exec_batch_execute(sql, data)
        return True

    except Exception as err:
        print("err:", err)
        return False


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


def get_appointments():
    try:
        sql2 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (380)
            AND status = 'scheduled'
        """
        sql5 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            ggt_prod.appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            status = 'scheduled'
                AND location_id = 2445
                AND scheduled_dt > '2020-12-28'
        """

        sql4 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            ggt_prod.appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            status = 'scheduled'
            AND location_id IN (2414, 2417)
            AND scheduled_dt > '2020-12-23'
            AND scheduled_dt < '2020-12-24'
        """

        sql5 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            test_samples t
            JOIN
                    patients p ON t.patient_id = p.id
        WHERE
            t.status = 'with_lab'
                AND t.create_dt < '2020-12-23'
        LIMIT 22000,4000
        """

        sql6 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (2420 , 2446,
                276,
                2448,
                274,
                344,
                2451,
                370,
                361,
                360,
                372,
                2414,
                2417,
                2421,
                367,
                2397,
                364,
                366,
                2458,
                350,
                369,
                2416,
                2452,
                382)
                AND scheduled_dt > '2020-12-29 00:00:00'
                AND scheduled_dt <  '2020-12-29 11:30:00'
                AND status = 'scheduled'
        """

        sql7 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (2420 , 2446,
                2423,
                344,
                370,
                361,
                360,
                2418,
                2415,
                414,
                417,
                2422,
                367,
                399,
                350,
                369,
                416,
                2421)
                AND scheduled_dt > '2020-12-29 00:00:00'
                AND scheduled_dt < '2020-12-30 00:00:00'
                AND status = 'scheduled'
        """

        sql8 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
                JOIN
            test_samples t ON t.id = a.id
        WHERE
            t.test_result = 'inconclusive'
                AND t.lab_electronic_submission_dt > '2020-12-20'

        """

        sql9 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (222, 266, 272)
            AND status = 'scheduled'
            AND scheduled_dt > '2020-12-31 00:00:00'
            AND scheduled_dt <  '2021-01-01 00:00:00'
        """

        sql10 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
                JOIN
            test_samples t ON t.id = a.id
        WHERE
            a.location_id IN (2421)
                AND t.status <> 'lab_result_received'
                AND a.status = 'test_completed'
                AND a.test_start_dt > '2020-12-28 00:00:00'
                AND a.test_start_dt < '2021-12-29 00:00:00'
        """

        sql = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (144)
                AND scheduled_dt > '2021-01-11 00:00:00'
                AND scheduled_dt <  '2021-01-12 00:00:00'
                AND status = 'scheduled'
        """

        sql12 = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (250, 164)
            AND scheduled_dt > '2021-01-11 00:00:00'
            AND scheduled_dt < '2021-01-12 00:00:00'
            AND status = 'scheduled'
        """

        return read_rows(sql)

    except Exception as err:
        print(err)


def prepare_sms_text(appointment):
    #return """Hi {}, due to inclement weather, the location where you have registered for your COVID-19 test will be CLOSED. We apologize for the inconvenience this may cause. Please visit GoGetTested.com to register for a new appointment.
    #""".format(appointment["first_name"])

    return """Hi {}, due to inclement weather, we’ve had to delay opening the testing location where you have registered to 11am. This may change depending on the weather. We apologize for the inconvenience this may cause. Please visit GoGetTested.com to register for a new appointment.
    """.format(appointment["first_name"])


def sync_appointments_with_schedule_slots():
    sql = """
        SELECT 
            id, scheduled_dt, location_id
        FROM
            appointments
        WHERE
            scheduled_dt > DATE(NOW())
            AND scheduled_dt < '2020-11-20'
                AND id NOT IN (
                    SELECT 
                        appointment_id
                    FROM
                        schedules
                    WHERE
                        appointment_id IS NOT NULL
                )
    """
    rows = read_rows(sql)
    print('Appointments loaded. Count: {}'.format(len(rows)))

    for row in rows:
        try:
            sql = """
                UPDATE schedules 
                SET 
                    status = 'booked',
                    appointment_id = %s
                WHERE
                    start_dt = %s
                    AND status = 'available' 
                    AND location_id = %s
                LIMIT 1
            """
            vals = (row['id'], row['scheduled_dt'], row['location_id'])
            # if exec_update(sql, vals):
            #    print(row['id'], row['scheduled_dt'])

            print("""UPDATE schedules SET status = 'booked', appointment_id = {} WHERE start_dt = '{}' AND location_id = {} AND status = 'available' LIMIT 1""".format(
                row['id'], row['scheduled_dt'], row['location_id']))

        except Exception as err:
            log_generic(
                type=c.c.ERROR,
                function=whoami(),
                error=err
            )


def upload_insurance_images_to_gcp():
    limit = 500000
    increment = 1000
    start = random.randint(0, 100000)
    start = 0
    print('starting at: ', start)
    try:
        for i in range(start, limit, increment):
            sql = """
            SELECT 
                q.id, a.id as appointment_id, q.patient_id, insurance_photo
            FROM
                patient_questionnaires q
                    JOIN
                appointments a ON (a.patient_id = q.patient_id)
            LIMIT {},{}
            """.format(i, increment)
            rows = read_rows(sql)

            for row in rows:
                try:
                    qid = row['id']
                    insurance_photo = row['insurance_photo']
                    appointment_id = row['appointment_id']

                    if insurance_photo is None or len(insurance_photo) < 250:
                        pass
                    else:
                        if "," in insurance_photo:
                            base64string = insurance_photo.split(",")[1]

                        dest_file_name = '{}.png'.format(appointment_id)
                        upload_insurance_card_from_base64_string(
                            base64string, 'image/png', dest_file_name)

                        print('uploaded image: {}'.format(dest_file_name))
                        remove_image_from_questionnnaires_table(qid)

                except Exception as err:
                    print(err)

    except Exception as err:
        print(err)


def upload_insurance_images_to_gcp_with_small_table():
    print('starting...')
    try:
        sql = """
        SELECT 
            q.id, a.id as appointment_id, q.patient_id, insurance_photo
        FROM
            patient_questionnaires q
                JOIN
            appointments a ON (a.patient_id = q.patient_id)
        WHERE length(q.insurance_photo)>10
        LIMIT 100
        """
        rows = read_rows(sql)

        for row in rows:
            try:
                qid = row['id']
                insurance_photo = row['insurance_photo']
                appointment_id = row['appointment_id']

                if insurance_photo is None or len(insurance_photo) < 250:
                    pass
                else:
                    if "," in insurance_photo:
                        base64string = insurance_photo.split(",")[1]

                    dest_file_name = '{}.png'.format(appointment_id)
                    upload_insurance_card_from_base64_string(
                        base64string, 'image/png', dest_file_name)

                    print('uploaded image: {}'.format(dest_file_name))
                    remove_image_from_questionnnaires_table(qid)

            except Exception as err:
                print(err)

    except Exception as err:
        print(err)


def remove_image_from_questionnnaires_table(id):
    try:
        sql = """
        UPDATE patient_questionnaires 
        SET 
            insurance_photo = 1
        WHERE
            id = %s
        """
        val = (id,)
        result = exec_update(sql, val)
        pass

    except Exception as err:
        print(err)


    
