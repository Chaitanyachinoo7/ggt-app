import os
import glob
import csv
import datetime
import paramiko
import base64
import random
from datetime import datetime

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

    #process_bcg_locations_file()
    #process_mx_locations_file()
    #update_schedules()

    # upload_insurance_images_to_gcp()
    # sync_appointments_with_schedule_slots()
    # upload_insurance_images_to_gcp_with_small_table()
    #process_email_notifications()
    #upload_insurance_files_from_gstore()
    #process_sms_notifications()
    #process_email_notifications()
    #dedupe_tokens()
    #process_raw_list_sms_notifications()
    #process_vax()
    process_vax_reschedule_sms_notification()

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
    subject = "IMPORTANT: {}, Important information regarding Covid-19 Testing".format(row['first_name'])
    #subject = "IMPORTANT: {}, Your Covid-19 Testing location has closed due to inclement weather".format(row['first_name'])

    template_vars = {
        "first_name": row['first_name']
    }

    template_name = 'GGT-14-APPOINTMENT-WEATHER-CLOSING-EMAIL.html'
    #template_name = 'GGT-9-APPOINTMENT-DELAYED-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


def prepare_sms_text(appointment):
    return """Hi {}, the location where you have registered for your COVID-19 test will be located at the following address for today.  509 E 11th Street Hutchinson KS 67501. Please arrive at this site for your appointment. We apologize for the inconvenience this might have caused.
    """.format(appointment["first_name"])

    #return """Hi {}, the location where you have registered for your COVID-19 test will be CLOSED 02/19/2021 due to inclement weather. We apologize for the inconvenience this might have caused. Please visit GoGetTested.com to register for a new appointment.
    #""".format(appointment["first_name"])

    #return """Hi {}, due to inclement weather, we’ve had to delay opening the testing location where you have registered to 12 pm. This may change depending on the weather. We apologize for the inconvenience this may cause. Please visit GoGetTested.com to register for a new appointment.
    #""".format(appointment["first_name"])



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

        sql14 = """
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

        sql = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
        WHERE
            location_id IN (
                2497
                )
                AND scheduled_dt > '2021-02-19 00:00:00'
                AND scheduled_dt < '2021-02-20 00:00:00'
                AND status = 'scheduled'
        """

        return read_rows(sql)

    except Exception as err:
        print(err)




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


    



def process_bcg_locations_file():
    import csv
    with open('archived/bcg_location_list_v3.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            print(', '.join(row))
            name = row[0]
            addr1= row[1]
            addr2= row[2]
            city= row[3]
            st= row[4] 
            zip= row[5]
            operator= row[7]
            phone_number= row[8]
            website= row[8]
            open_hours = row[11]
            add_to_locations(name+' | '+open_hours, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours)


def process_mx_locations_file():
    import csv
    with open('archived/mx_locations.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            print(', '.join(row))
            name = row[0]
            addr1= row[1]
            addr2= ''
            city= ''
            st= ''
            zip= ''
            operator= 'Laboratorio medico Del Chopo'
            phone_number= ''
            website= ''
            open_hours= ''
            add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours)



def add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
    payload = {
        "site_code": "GGT",
        "group_code": "_default_mx_",
        "name": name,
        "addr1": addr1,
        "addr2": addr2,
        "addr3": "",
        "city": city,
        "st": st,
        "zip": zip,
        "lat": 0,
        "lng": 0,
        "time_zone": "CST",
        "time_zone_offset": "-06:00",
        "test_type_offered": "oral",
        "status": "enabled",
        "type": "drive_thru",
        "billing_type": "client_bill",
        "collect_insurance_info": 0,
        "allow_insurance_skip": 1,
        "collect_upfront_payment": 0,
        "image_thumbnail": "",
        "accepts_bookings": True,
        "accepts_walkins": True,
        "operator": operator,
        "phone_number": phone_number,
        "website": website,
        "open_hours": open_hours,
        "is_external": False,
        "group_ids": [1],
        "service_ids": [1],
        "country": 'MX'
    }

    try:
        import requests
        import ujson
        print(ujson.dumps(payload))
        url = 'http://localhost:5010/api/portal/site-admin/create_location'
        r = requests.post(url, json=payload)
        res = r.json()

        location_id = res['results'][0]['location_id']
        add_sched_rule(location_id)
        update_location_org(location_id)

    except Exception as err:
        print(err)


def add_sched_rule(location_id):
    payload = {
        "rule_type": "regular",
        "time_zone": "string",
        "time_zone_offset": "string",
        "status": "enabled",
        "location_id": location_id,
        "category": "test",
        "slot_increment": 10,
        "slot_multiplier": 10,
        "local_start_time": "08:00:00",
        "local_end_time": "12:00:00",
        "active_local_start_dt": "2021-03-08 08:00:00",
        "active_local_end_dt": "2021--31 12:00:00",
        "sun": False,
        "mon": True,
        "tue": True,
        "wed": True,
        "thu": True,
        "fri": True,
        "sat": True
    }
    try:
        import ujson
        import requests

        print(ujson.dumps(payload))
        url = 'http://localhost:5010/api/portal/site-admin/add_schedule_generation_rule'
        r = requests.post(url, json=payload)
        res = r.json()

        location_id = res['results'][0]['location_id']

    except Exception as err:
        print(err)


def update_location_org(location_id):
    sql = """
        UPDATE
            locations l
        SET
            l.org_id = 4
        WHERE
            id = %s
        """

    vals = (location_id, )
    return exec_update(sql, vals)


def update_schedules():
    locations = ['2631','2630','2629','2628','2627','2626','2625','2624','2623','2622','2621','2620','2619','2618','2617','2616','2615','2614','2613','2612','2611','2610','2609','2608','2607','2606','2605','2604','2603','2602','2601','2600','2599','2598','2597','2596','2595','2594','2593','2592','2591','2590','2589']
    for location_id in locations:
        add_sched_rule(location_id)

def dedupe_tokens():
    from ggt.tasks.handle_duplicate_tokens import (
        handle_duplicate_tokens
    )
    handle_duplicate_tokens()





def process_raw_list_sms_notifications():
    rows = [
                ['+19999999999','Jo','https://start.gogetvax.com/vax/schedule/startwt/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjMyZDI2ZWI2LTk3MGItNGU4YS05YmFmLWZjZmU5NzY0YmViZCIsImV4cCI6MTYxNzEzNDEwN30.gaoE6Q7KcVgEN3t1NMZJKDOkkYl2yh9WNHy3RqSznTA/_ROCKWALL_'],
                ['+19999999999','Kristi','https://start.gogetvax.com/vax/schedule/startwt/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6ImQ0MzViNzY1LThiY2EtNGE5Ny1iZGYxLTU3YTBiNGE2NjZkYyIsImV4cCI6MTYxNzEzNDEwN30.x-VlYzDhIDCT8M2ZwExtv2mpJgUKvaFILbWPqyLxtfo/_ROCKWALL_']                
            ]
    data = []
    for row in rows:
        phone_number = row[0]
        first_name = row[1]
        link = row[2]
        message = """Hi {}, it's time get vaccinated! The vaccine clinic will be held Saturday March 13, 2021 at 1215 T L Townsend Dr, Rockwall, TX 75087. There are only 900 slots available. Please click this unique link to register for your vaccine. {}""".format(first_name, link)

        data.append(
            (phone_number, message)
        )

    batch_enqueue_sms_notifications(data)



def process_vax_reschedule_sms_notification():
    rows = [
                ['+12142123115','Diane','1963-11-01','1315258','2021-03-13 12:00:00','sleepy732@icloud.com'],
                ['+12143153910','Melissa','1975-04-16','1315260','2021-03-13 11:00:00','garcia1036@gmail.com'],
                ['+12144350186','Christina','1982-08-27','1315263','2021-03-13 12:00:00','christinacarias@gmail.com'],
                ['+19183279863','maria','1983-02-18','1315266','2021-03-13 12:00:00','mariaelisa_h@yahoo.com'],
                ['+12142329380','Jaclyn','1977-12-02','1315270','2021-03-13 12:00:00','jaclyn.almon@rockwallisd.org'],
                ['+14693803137','Christopher','1983-12-07','1315274','2021-03-13 12:00:00','cdkingsley@gmail.com'],
                ['+12145386059','Lucas','1990-04-14','1315276','2021-03-13 12:00:00','lucas.beville@gmail.com'],
                ['+14027095435','Natalie','1981-10-27','1315280','2021-03-13 12:00:00','Natalie.vaughn@rockwallisd.org'],
                ['+12146904106','Elizabeth','1996-11-07','1315282','2021-03-13 12:10:00','lizv1107@gmail.com'],
                ['+17273894635','Michael','1983-03-29','1315283','2021-03-13 12:10:00','coachtschmitz@gmail.com'],
                ['+12147736291','Kayli','1985-02-15','1315284','2021-03-13 12:10:00','kayli.harding@rockwallisd.org'],
                ['+12148720342','Lisa','1959-06-03','1315285','2021-03-13 12:10:00','Lisapacific5@gmail.com'],
                ['+12145495273','Kathy','1966-02-07','1315290','2021-03-13 12:10:00','Kathy.arnold@rockwallisd.org'],
                ['+12108729570','Laural','1970-07-19','1315292','2021-03-13 12:10:00','laural.onstott@rockwallisd.org'],
                ['+19724677240','Jennifer','1976-06-29','1315293','2021-03-13 11:10:00','Jennifer.elizondo@att.net'],
                ['+18064540396','Kelsie','1995-10-30','1315299','2021-03-13 11:10:00','kbminor2000@gmail.com'],
                ['+12146639894','Travis','1992-05-05','1315304','2021-03-13 12:10:00','tueckert005@gmail.com'],
                ['+19727467554','Marchelle','1969-07-12','1315307','2021-03-13 12:10:00','marchelle.morgan@rockwallisd.org'],
                ['+14694007749','Julie','1963-07-21','1315308','2021-03-13 12:10:00','julie.villarreal@rcisd.org'],
                ['+16307476120','Leanne','1993-08-06','1315312','2021-03-13 12:10:00','Leanne.wilson@rockwallisd.org'],
                ['+12148014841','Avery','1991-09-26','1315315','2021-03-13 12:10:00','avery.due@gmail.com'],
                ['+19729220776','Michael','1979-06-23','1315318','2021-03-13 12:10:00','saxman79@yahoo.com'],
                ['+14692076967','Laura','1979-07-09','1315319','2021-03-13 12:10:00','laura.mejia@rockwallisd.org'],
                ['+19723451084','Kelley','1980-08-16','1315323','2021-03-13 11:40:00','kelley.cavin@rockwallisd.org'],
                ['+12144036408','Julie','1977-03-31','1315337','2021-03-13 11:40:00','Julie.locke@rockwallisd.org'],
                ['+12145589177','Janelle','1979-01-21','1315338','2021-03-13 11:10:00','valindy@aol.com'],
                ['+12142158343','Tandra','1975-08-07','1315339','2021-03-13 11:40:00','Tandra.calhoun@rockwallisd.org'],
                ['+12148686296','KASIE','1972-12-27','1315346','2021-03-13 11:40:00','kasie.williamson@rockwallisd.org'],
                ['+12146128340','Hope','1991-10-11','1315347','2021-03-13 11:10:00','hreyes1010@yahoo.com'],
                ['+14693144276','Kelsie','1992-07-10','1315348','2021-03-13 11:40:00','Klynnev@gmail.com'],
                ['+19728248222','Carrie','1981-11-02','1315352','2021-03-13 11:40:00','Carrie.batson@rockwallisd.org'],
                ['+19729895602','Barbara','1970-12-29','1315357','2021-03-13 11:50:00','barbara.duran@rockwallisd.org'],
                ['+19032681934','Julie','1978-05-03','1315358','2021-03-13 11:50:00','julie.sidman@rockwallisd.org'],
                ['+18168356799','Samantha','1978-06-28','1315361','2021-03-13 11:50:00','Samantha.coalter@rockwallisd.org'],
                ['+12143560280','Detra','1956-10-02','1315363','2021-03-13 11:50:00','detraggarrett@gmail.com'],
                ['+19729779246','Melodi','1962-07-30','1315365','2021-03-13 11:50:00','Melodi.nix@rockwallisd.org'],
                ['+14693861564','Michelene','1967-12-13','1315371','2021-03-13 11:50:00','Michelene.watson@rockwallisd.org'],
                ['+18608785106','Tori','1983-04-19','1315372','2021-03-13 11:50:00','tori.mcdaid@gmail.com'],
                ['+12144176961','Renee','1956-12-07','1315378','2021-03-13 11:50:00','renee.aube@rockwallisd.org'],
                ['+12145468323','Andrea','1985-05-29','1315381','2021-03-13 11:50:00','andrea.stewart@rockwallisd.org'],
                ['+12142360343','Julie','1970-11-22','1315386','2021-03-13 11:50:00','Julie.byrnes@rockwallisd.org'],
                ['+19725231553','Cameron','1972-07-07','1315387','2021-03-13 11:10:00','cameron.gipson@rockwallisd.org'],
                ['+19724155971','Donald','1966-07-26','1315388','2021-03-13 11:50:00','don.williams@rockwallisd.org'],
                ['+19726070525','Abigail','1971-12-13','1315397','2021-03-13 11:50:00','abigail.morales@rockwallisd.org'],
                ['+19729777974','Lydia','1959-08-13','1315416','2021-03-13 11:10:00','Jimandlydiawatkins@sbcglobal.net'],
                ['+12144508186','Chad','1978-04-10','1315423','2021-03-13 11:50:00','Cdashby27@aol.com'],
                ['+12148305087','Shauna','1982-02-12','1315425','2021-03-13 11:50:00','shaunahawkins@gmail.com'],
                ['+12147666134','Lana','1966-10-23','1315428','2021-03-13 11:50:00','lana.edwards@rockwallisd.org'],
                ['+19032682683','Shelley','1980-10-12','1315433','2021-03-13 12:00:00','Shelley.willson@rockwallisd.org'],
                ['+12144181207','Amber','1983-10-30','1315436','2021-03-13 12:00:00','amber.tyree@rockwallisd.org'],
                ['+14693389434','Lindsey','2001-02-21','1315437','2021-03-13 12:00:00','Lindsey.Baumgartner@rockwallisd.org'],
                ['+14697449573','Wesley','1983-01-14','1315443','2021-03-13 12:00:00','westeaches@gmail.com'],
                ['+14698338486','Mericyl','1983-02-26','1315464','2021-03-13 12:00:00','Mdcaceres83@yahoo.com'],
                ['+14696010086','Lisa','1970-01-19','1315465','2021-03-13 12:00:00','noellec0119@gmail.com'],
                ['+14696010086','Lisa','1970-01-19','1315466','2021-03-13 12:00:00','noellec0119@gmail.com'],
                ['+12147387003','Teresa','1966-08-17','1315468','2021-03-13 12:00:00','tjames817@yahoo.com'],
                ['+12147661261','Mary','1968-04-22','1315471','2021-03-13 12:00:00','Mary.Hartzell@Rockwallisd.org'],
                ['+18703652806','Michael','1947-10-19','1315473','2021-03-13 12:00:00','lilesmj@yahoo.com'],
                ['+12148018616','Jennifer','1978-09-16','1315484','2021-03-13 12:00:00','Jennscamp@gmail.com'],
                ['+12149268241','Mary','1965-11-20','1315488','2021-03-13 11:20:00','mary@beaureview.com'],
                ['+12144973989','cynthia','1962-06-19','1315499','2021-03-13 10:50:00','Cynthia.lemmons@rockwallisd.org'],
                ['+12142401187','Jennifer','1983-01-22','1315504','2021-03-13 10:50:00','Jholden6212@att.net'],
                ['+12145578078','Christina','1975-07-20','1315509','2021-03-13 11:00:00','Christinabradford1@yahoo.com'],
                ['+12142054988','Laurie','1957-12-30','1315519','2021-03-13 11:00:00','Lpasson@charter.ney'],
                ['+12149919975','Elizabeth','1982-04-05','1315525','2021-03-13 11:00:00','Lizzierodriguez30@yahoo.com'],
                ['+18479753242','Mirna','1986-03-27','1315526','2021-03-13 11:00:00','yadi_garcia21@yahoo.com'],
                ['+14692236376','Allison','1975-12-30','1315530','2021-03-13 11:00:00','allison.lane.1230@gmail.com'],
                ['+12102898200','Melissa','1979-05-14','1315538','2021-03-13 11:20:00','melissa.chase@rockwallisd.org'],
                ['+12147705906','Stefani','1977-11-14','1315539','2021-03-13 11:00:00','Riker.family.tx@gmail.com'],
                ['+12145024775','Connie','1966-05-01','1315540','2021-03-13 11:00:00','connie.westerman@rockwallisd.org'],
                ['+14697749181','Wendy','1973-05-16','1315541','2021-03-13 11:00:00','baridonfam@gmail.com'],
                ['+18155280438','Amanda','1991-11-27','1315543','2021-03-13 11:00:00','ambradlo@yahoo.com'],
                ['+12146632574','Shelby','1995-07-19','1315549','2021-03-13 11:00:00','Shelby.gage@rockwallisd.org'],
                ['+19729894235','Lindsey','1979-11-16','1315551','2021-03-13 11:20:00','lindseysavage@hotmail.com'],
                ['+16613504522','Nilafe','1970-01-31','1315552','2021-03-13 11:00:00','nilafepursell@gmail.com'],
                ['+12147701919','Stacey','1971-06-30','1315553','2021-03-13 11:00:00','Staceyhouser@yahoo.com'],
                ['+12142328277','Travis','1974-10-25','1315556','2021-03-13 11:00:00','tbferg451@gmail.com'],
                ['+12144035117','Alma','1977-10-02','1315558','2021-03-13 11:00:00','alma.chalambaga@rockwallisd.org'],
                ['+19728397553','Carolyn','1965-03-16','1315559','2021-03-13 11:00:00','carolyn.tuttle@rockwallisd.org'],
                ['+14698349155','Tracy','1980-05-22','1315561','2021-03-13 11:00:00','tracy@tracyenoch.com'],
                ['+19727574693','Lauren','1988-02-23','1315562','2021-03-13 11:00:00','lhart0706@gmail.com'],
                ['+12149015118','Robert','1987-09-18','1315564','2021-03-13 11:00:00','Robhack87@icloud.com'],
                ['+12149015118','Robert','1987-09-18','1315565','2021-03-13 11:00:00','Robhack87@icloud.com'],
                ['+16306616334','Amanda','1983-06-29','1315567','2021-03-13 11:00:00','amanda.nelson@live.com'],
                ['+18175387192','Monica','1970-01-16','1315569','2021-03-13 11:20:00','Mprado70@live.com'],
                ['+19729559849','Loretta','1967-09-29','1315572','2021-03-13 11:00:00','loretta.latus@rockwallisd.org'],
                ['+12147930583','Priscilla','1976-04-24','1315576','2021-03-13 11:00:00','Priscilla.swanson@rockwallisd.org'],
                ['+12147287401','James','1991-08-05','1315577','2021-03-13 11:00:00','al3xhart@yahoo.com'],
                ['+12145974394','melody','1973-08-13','1315579','2021-03-13 11:00:00','melody.carrillo@rockwallisd.org'],
                ['+19034682364','Stephanie','1972-09-09','1315585','2021-03-13 11:20:00','sgeer1128@yahoo.com'],
                ['+12144970884','Adrienne','1968-11-13','1315586','2021-03-13 11:00:00','ry01andmad05@yahoo.com'],
                ['+12147259747','Nancy','1956-12-10','1315590','2021-03-13 11:00:00','farrellbe45@cs.com'],
                ['+12144998392','Cory','1973-10-14','1315591','2021-03-13 11:10:00','cwshort1973@outlook.com'],
                ['+14698554743','Francisca','1974-10-10','1315595','2021-03-13 11:10:00','Chavezfrancisca74@yahoo.com'],
                ['+12148831747','Jacqueline','1975-12-04','1315600','2021-03-13 11:10:00','Jacqueline.oxford@rockwallisd.org'],
                ['+12142128820','Jay','1965-07-31','1315601','2021-03-13 11:10:00','liveoak41@gmail.com'],
                ['+12149143571','Cecil','1982-09-18','1315604','2021-03-13 11:10:00','Trey.brooks@rockwallisd.org'],
                ['+12143542660','Sharon','1968-05-14','1315615','2021-03-13 11:10:00','Scbowman1@yahoo.com'],
                ['+14699941198','Gabriela','1994-01-22','1315616','2021-03-13 11:10:00','Orumgabriela@gmail.com'],
                ['+14692742816','Tommy','1961-03-31','1315617','2021-03-13 11:10:00','tommy.green@rockwallisd.org'],
                ['+12147668390','Carman','1962-08-23','1315619','2021-03-13 11:10:00','carman.dennard@rockwallisd.org'],
                ['+14692799084','Jodie','1967-06-23','1315622','2021-03-13 11:10:00','jodie.scivetti@rockwallisd.org'],
                ['+12145338737','Virginia','1971-12-15','1315624','2021-03-13 11:20:00','kay.russo@rockwallisd.org'],
                ['+19728497188','Jennifer','1973-08-02','1315625','2021-03-13 11:20:00','Jennifer.little@rockwallisd.org'],
                ['+19728163454','Jessica','1978-11-13','1315638','2021-03-13 11:20:00','Jesslefere@yahoo.com'],
                ['+19723337553','Nancy09','1960-09-02','1315639','2021-03-13 11:20:00','nancy.cook@rockwallisd.org'],
                ['+13253206722','Gerry','1976-08-11','1315640','2021-03-13 11:20:00','ebtrek@gmail.com'],
                ['+19033661525','Jennifer','1981-05-29','1315642','2021-03-13 11:20:00','Jennifer.holt@rcisd.org'],
                ['+12142408973','Billy','1973-12-19','1315644','2021-03-13 11:20:00','Dane.Steinberger@gmail.com'],
                ['+12142288194','Laurie','1961-05-13','1315647','2021-03-13 11:20:00','Lnh001@hotmail.com'],
                ['+12142133430','Laurie','1960-08-18','1315648','2021-03-13 11:20:00','laurie.mckimmey@rockwallisd.org'],
                ['+14692475340','Kara','1983-03-04','1315657','2021-03-13 11:20:00','kara.burkart@rockwallisd.org'],
                ['+19154490591','Santiago (Jimmy)','1942-07-11','1315663','2021-03-13 11:20:00','glorytg3@sbcglobal.net'],
                ['+12145438761','Melissa','1979-09-08','1315667','2021-03-13 11:30:00','m_starr8@yahoo.com'],
                ['+19032771064','Heather','1980-03-24','1315671','2021-03-13 11:20:00','Hnweaver0306@sbcglobal.net'],
                ['+19032459977','Linda','1970-04-13','1315677','2021-03-13 11:20:00','Linda.schmille@rockwallisd.org'],
                ['+19033865373','Colleen','1969-10-14','1315684','2021-03-13 11:20:00','Colleen.willman@region10.org'],
                ['+12145438455','Kim','1977-03-29','1315693','2021-03-13 11:30:00','Kimschwerdt@yahoo.com'],
                ['+14693389076','David','1968-01-06','1315695','2021-03-13 11:30:00','dgasewicz@aol.com'],
                ['+16303463489','Wendy','1979-12-28','1315705','2021-03-13 11:30:00','Wendy.stambaugh@yahoo.com'],
                ['+12145026599','Beverly','1965-02-23','1315707','2021-03-13 11:30:00','meachamone@sbcglobal.net'],
                ['+18167260081','Cody','1992-06-29','1315711','2021-03-13 11:30:00','Rhsjacketwrestling@gmail.com'],
                ['+14176696110','Nicholas','1996-06-03','1315713','2021-03-13 10:00:00','chase.brennan@rockwallisd.org'],
                ['+12143561996','Ashley','1984-01-29','1315726','2021-03-13 11:30:00','a.mcdougald@me.com'],
                ['+14698473055','Jennifer','1973-09-12','1315732','2021-03-13 10:00:00','jmrinker31@yahoo.com'],
                ['+14692458599','Devonta','1995-06-15','1315736','2021-03-13 10:00:00','danielsd38@gmail.com'],
                ['+12142236864','Melinda','1968-10-06','1315747','2021-03-13 10:00:00','Melinda.lewis@rockwallisd.org'],
                ['+17632328779','Nieshea','1979-10-11','1315766','2021-03-13 10:00:00','nieshea.smith@gmail.com'],
                ['+14693383267','Ryan','1968-04-25','1315767','2021-03-13 10:00:00','ryanhin2523@gmail.com'],
                ['+16159356191','Debbie','1960-06-04','1317317','2021-03-13 10:10:00','debbiekayzink@yahoo.com'],
                ['+12145344090','Yvonne','1956-09-05','1317352','2021-03-13 10:10:00','yharcourt2014@gmail.com'],
                ['+19727228621','Corinna','1968-09-22','1317359','2021-03-13 10:10:00','corinna.calabrese@rockeallisd.org'],
                ['+14692645015','Joshua','1980-11-15','1317398','2021-03-13 10:10:00','josh.goellner@rockwallisd.org'],
                ['+19728346833','Jennifer','1974-08-22','1317498','2021-03-13 10:20:00','Jennifer.Johnson@rockwallisd.org'],
                ['+14698779226','Cecilia','1981-12-17','1317572','2021-03-13 10:20:00','Cecilia.Cervantes@rockwallisd.org'],
                ['+19037156169','Taylor','1993-08-03','1317653','2021-03-13 10:20:00','travisandtayloru@gmail.com'],
                ['+19034561793','Patrick','1968-05-04','1317784','2021-03-13 10:20:00','Pjust3136@gmail.com'],
                ['+12144048352','Nancy','1976-07-21','1317884','2021-03-13 10:20:00','monyta19@gmail.com'],
                ['+19723428812','Bryan','1984-06-18','1317885','2021-03-13 10:20:00','Bryan.moss@rockwalliad.orf'],
                ['+18064384692','Amy','1979-05-06','1317886','2021-03-13 10:20:00','amy.becknell@rcisd.org'],
                ['+15124842640','Julia','1981-04-02','1317888','2021-03-13 10:20:00','jimandjulia2009@gmail.com'],
                ['+16104285312','Philip','1967-07-27','1317898','2021-03-13 10:20:00','pguarin@rcn.com'],
                ['+19726798711','Bobby','1956-12-31','1317899','2021-03-13 10:20:00','djt212121@gmail.com'],
                ['+14697660077','Giselle','1977-11-23','1317902','2021-03-13 10:20:00','Giselle.Snowden@rockwallisd.org'],
                ['+12146629005','Melanie','1980-01-18','1317903','2021-03-13 10:20:00','Melanie.brannon@rockwallisd.org'],
                ['+12144762935','Suzanne','1966-02-01','1317915','2021-03-13 10:20:00','katellio@yahoo.com'],
                ['+18179017392','Jeremy','1975-01-06','1317922','2021-03-13 10:20:00','Meltoncrew5@gmail.com'],
                ['+12146866464','Dorothy','1957-12-04','1317923','2021-03-13 10:20:00','pauldorothypinholt@hotmail.com'],
                ['+12142891718','Maria','1969-05-08','1317924','2021-03-13 10:20:00','lulu.bueno@rockwallisd.org'],
                ['+14692360817','Nicholas','2000-10-09','1317936','2021-03-13 10:20:00','kay.russo@rockwallisd.org'],
                ['+14699646552','Cade','2001-11-06','1317939','2021-03-13 10:20:00','edwarcad01@gmail.com'],
                ['+12144703795','Stephanie','1972-07-04','1317940','2021-03-13 10:20:00','stephbaughn.rd@gmail.com'],
                ['+12142504048','Ricky','1966-04-09','1317943','2021-03-13 10:20:00','rickyb1966@suddenlink.net'],
                ['+19727429291','Amber','1982-03-05','1317946','2021-03-13 10:20:00','amcampos82@hotmail.com'],
                ['+12142821827','Kenneth','1952-06-30','1317948','2021-03-13 10:20:00','Kmenard@showbizcinemas.com'],
                ['+14694741508','Leslie','1964-02-21','1317951','2021-03-13 10:20:00','Leslie.reese@rockwallisd.org'],
                ['+12147934918','Cameron','1950-04-18','1317963','2021-03-13 10:30:00','c_menard@live.com'],
                ['+12142329380','Jillian','2008-08-28','1317964','2021-03-13 10:30:00','jaclynkay@hotmail.com'],
                ['+12145578283','Sheron','1962-03-05','1317974','2021-03-13 10:30:00','Sheron.baldwin@mkcorp.com'],
                ['+19725524546','Sylvia','1982-02-19','1317975','2021-03-13 10:30:00','sagallardo219@yahoo.com'],
                ['+12147934918','Gene','1923-12-01','1317976','2021-03-13 10:30:00','c_menard@live.com'],
                ['+19034568903','Julia','1992-06-17','1317986','2021-03-13 10:30:00','juliehernandez92@hotmail.com'],
                ['+19729656654','Kerasten','1974-11-07','1317992','2021-03-13 10:30:00','Kerastennelson@gmail.com'],
                ['+19728241832','Britt','1979-01-12','1318004','2021-03-13 10:30:00','Bsatttu@hotmail.com'],
                ['+19407044924','Austin','1994-01-26','1318021','2021-03-13 10:30:00','Steven.murphy@rockwallisd.org'],
                ['+19729778546','Abigail','2000-02-02','1318022','2021-03-13 10:30:00','Kntexas@swbell.net'],
                ['+14692866284','Kyra','1972-05-01','1318033','2021-03-13 10:30:00','kyra.mccaw@gmail.com'],
                ['+18062394614','Sunni','1981-04-30','1318051','2021-03-13 10:30:00','sunni.miegel@rockwallisd.org'],
                ['+19032682683','Jarrett','1979-12-08','1318053','2021-03-13 10:30:00','Shelley.willson@rockwallisd.org'],
                ['+19723333030','Debra','1973-01-24','1318058','2021-03-13 10:30:00','Theartprofessor@tx.rr.com'],
                ['+12148686296','Kirby','1968-05-04','1318085','2021-03-13 10:30:00','k_williamson@sbcglobal.net'],
                ['+19723425536','Mattie','1998-10-30','1318090','2021-03-13 10:30:00','mattie.barentine@gmail.com']                
            ]
    data = []
    for row in rows:
        phone_number = row[0]
        first_name = row[1]
        dob = row[2].replace('-','')
        appointment_id = row[3]
        scheduled_dt = row[4]
        sched_time = datetime.strptime(scheduled_dt, "%Y-%m-%d %H:%M:%S").strftime("%a, %-d %b %Y @ %-I:%M %p")
        link = 'https://start.gogetvax.com/appointment/{}/{}'.format(appointment_id, dob)
        message = """Hi {}, Your appointment time for today's vaccine clinic has changed. Please note the new appointment time, {} at 1215 T L Townsend Dr, Rockwall, TX 75087. {}""".format(first_name, sched_time, link)

        data.append(
            (phone_number, message)
        )

    batch_enqueue_sms_notifications(data)


def process_vax():
    from ggt.tasks.vax_tx_outbound_hl7 import (
         process_vax_hl7         
    )
    process_vax_hl7()
    