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
from ggt.models.process_models.bp_schedules import bp_generate_full_schedule

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
    #process_delta_locations_file()
    #update_schedules()

    # upload_insurance_images_to_gcp()
    # sync_appointments_with_schedule_slots()
    # upload_insurance_images_to_gcp_with_small_table()
    #process_email_notifications()
    #upload_insurance_files_from_gstore()
    process_sms_notifications()
    #process_email_notifications()
    #dedupe_tokens()
    #process_raw_list_sms_notifications()
    #process_vax()
    # process_vax_reschedule_sms_notification()
    #process_vax_reminder()
    # process_vax_waitlist()
    # generate_schedules()

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing Misc Task')
    print('\n\n************************************************\n\n')


def generate_schedules():
    for x in range(3420, 3478):
        bp_generate_full_schedule(x)

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
    print(data)
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
    #return """Hi {}, the location where you have registered for your COVID-19 test will be located at the following address for today.  509 E 11th Street Hutchinson KS 67501. Please arrive at this site for your appointment. We apologize for the inconvenience this might have caused.
    #""".format(appointment["first_name"])

    return """Hi {}, due to unforeseen circumstances the location where you have registered for your COVID-19 test will have a delayed start until 12 pm. We apologize for the inconvenience. Please visit GoGetTested.com to register for a new appointment.
    """.format(appointment["first_name"])

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
                78
                )
                AND scheduled_dt > '2021-08-23 00:00:00'
                AND scheduled_dt < '2021-08-23 12:00:00'
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



def process_delta_locations_file():
    import csv
    with open('archived/delta_lowes_locations.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            print(', '.join(row))
            name = row[0]
            addr1= row[1]
            addr2= ''
            city= row[2]
            st= row[3]
            zip= row[4]
            operator= 'WellHealth Management LLC'
            phone_number= ''
            website= ''
            open_hours= ''
            add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours)


def add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
    payload = {
        "site_code": "GGT",
        "group_code": "_DEFAULT_",
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
        "time_zone_offset": "-05:00",
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
        "country": 'US'
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
        #update_location_org(location_id)

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
        "slot_multiplier": 1,
        "local_start_time": "08:00:00",
        "local_end_time": "12:00:00",
        "active_local_start_dt": "2021-03-04 08:00:00",
        "active_local_end_dt": "2021-03-07 16:00:00",
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


def get_locations():
    sql = """select id from locations where country='MX'"""
    rows = read_rows(sql)
    locations = []
    for row in rows:
        locations.append(row['id'])
    return locations


def update_schedules():
    locations = get_locations()  # ['2631','2630','2629','2628','2627','2626','2625','2624','2623','2622','2621','2620','2619','2618','2617','2616','2615','2614','2613','2612','2611','2610','2609','2608','2607','2606','2605','2604','2603','2602','2601','2600','2599','2598','2597','2596','2595','2594','2593','2592','2591','2590','2589']
    for location_id in locations:
        add_sched_rule(location_id)


def dedupe_tokens():
    from ggt.tasks.handle_duplicate_tokens import (
        handle_duplicate_tokens
    )
    handle_duplicate_tokens()





def process_raw_list_sms_notifications():
    rows = [
                ['+19999999999','Jo','https://start.gogetdoc.com/vax/schedule/startwt/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjMyZDI2ZWI2LTk3MGItNGU4YS05YmFmLWZjZmU5NzY0YmViZCIsImV4cCI6MTYxNzEzNDEwN30.gaoE6Q7KcVgEN3t1NMZJKDOkkYl2yh9WNHy3RqSznTA/_ROCKWALL_'],
                ['+19999999999','Kristi','https://start.gogetdoc.com/vax/schedule/startwt/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6ImQ0MzViNzY1LThiY2EtNGE5Ny1iZGYxLTU3YTBiNGE2NjZkYyIsImV4cCI6MTYxNzEzNDEwN30.x-VlYzDhIDCT8M2ZwExtv2mpJgUKvaFILbWPqyLxtfo/_ROCKWALL_']                
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
                ['+18018602474','Suresh','1980-10-31','1275935','2021-03-27 12:30:00','suresh@wellpay.com'],
                ['+19725333139','Robert','1962-09-10','1277114','2021-03-27 12:30:00','Chapr99@yahoo.com']
            ]
    data = []
    for row in rows:
        phone_number = row[0]
        first_name = row[1]
        dob = row[2].replace('-','')
        appointment_id = row[3]
        scheduled_dt = row[4]
        sched_time = datetime.strptime(scheduled_dt, "%Y-%m-%d %H:%M:%S").strftime("%a, %-d %b %Y @ %-I:%M %p")
        link = 'https://start.gogetdoc.com/appointment/{}/{}'.format(appointment_id, dob)
        message = """Hi {}, Your appointment time for today's vaccine clinic has changed. {} at 1215 T L Townsend Dr, Rockwall, TX 75087. For your convenience, you may arrive anytime before before 4:00 PM {}""".format(first_name, sched_time, link)

        data.append(
            (phone_number, message)
        )

    batch_enqueue_sms_notifications(data)


def process_vax_reminder():
    rows = [
                ['+18173127782','Mouyyad','1986-06-26','1274058','2021-03-27 13:00:00'],
                ['+18173087657','Ahmad','1987-09-04','1274080','2021-03-27 08:00:00']
            ]
    data = []
    for row in rows:
        phone_number = row[0]
        first_name = row[1]
        dob = row[2].replace('-','')
        appointment_id = row[3]
        scheduled_dt = row[4]
        sched_time = datetime.strptime(scheduled_dt, "%Y-%m-%d %H:%M:%S").strftime("%a, %-d %b %Y @ %-I:%M %p")
        link = 'https://start.gogetdoc.com/appointment/{}/{}'.format(appointment_id, dob)
        message = """Hi {}, this is a reminder that your 2nd dose vaccine appointment is on {}. Please note the address change to 1215 T L Townsend Dr, Rockwall TX 75087. You can acccess your QR code for your 2nd appointment here: {}""".format(first_name, sched_time, link)

        data.append(
            (phone_number, message)
        )

    batch_enqueue_sms_notifications(data)

    
def process_vax_waitlist():
    rows = [
                ['+19725231418','Maria'],
                ['+19032859761','Kara'],
                ['+12143550631','Luz'],
                ['+14695696799','Sarah'],
                ['+14694082969','Kimberlea'],
                ['+19404659879','Stacey'],
                ['+19728399414','Joshua'],
                ['+14699959397','Josh'],
                ['+12145513167','Jacob'],
                ['+14693472321','quanda'],
                ['+16086092101','Oskar'],
                ['+19035636767','Jacob'],
                ['+18179294419','James'],
                ['+17135820231','Armando'],
                ['+19727431535','Theresa'],
                ['+18589478372','Karen'],
                ['+12146632607','Reagan'],
                ['+12147105144','tamara'],
                ['+12148869158','Abbie'],
                ['+19034406023','Tracy'],
                ['+14692199717','Manila'],
                ['+14693287404','Michael'],
                ['+12148644338','Ashley'],
                ['+15058036172','Kevin'],
                ['+12147094574','Stephan'],
                ['+12147698372','Ashley'],
                ['+19033883426','Kathy'],
                ['+12149068057','Vanessa'],
                ['+12142881769','Safir'],
                ['+19037800379','Lea'],
                ['+12143045289','April'],
                ['+14698101383','Dorothy'],
                ['+16034913902','Cameron'],
                ['+12142322534','Janene'],
                ['+14693602442','Maria Jasmin'],
                ['+14699395330','Juliana'],
                ['+12147976560','Tetsuya'],
                ['+14694267094','Glenda'],
                ['+18177736588','Shannon'],
                ['+19723654584','Kimberly'],
                ['+19723753818','Ethan'],
                ['+16619175025','Colleen'],
                ['+12147898283','Robbie'],
                ['+19728167299','Joleen'],
                ['+17135820231','Kari'],
                ['+19723426086','casey'],
                ['+12142293209','dixie'],
                ['+19728148429','Brandon'],
                ['+14699518144','Rebecca'],
                ['+14695833687','Steve'],
                ['+12145072822','Melissa'],
                ['+12143262933','Ana'],
                ['+18605972059','Anupama'],
                ['+12146687570','Jaimie'],
                ['+14692225690','Steve'],
                ['+19728002309','Krystle'],
                ['+12146218198','Christine'],
                ['+12015662205','Denise'],
                ['+14697747778','Kimberly'],
                ['+12104285650','Lynette'],
                ['+19728399414','Ronnie'],
                ['+14697671880','Lori'],
                ['+18087996004','Haley'],
                ['+13096420031','John'],
                ['+12145059423','Hoan'],
                ['+14694039374','Shiv'],
                ['+12144158234','Rose'],
                ['+12146738733','Zachary'],
                ['+19723335204','Tracey'],
                ['+14692601280','Madellaine'],
                ['+19726797090','Helen'],
                ['+14693388411','Toni'],
                ['+14693388411','Toni'],
                ['+19035203706','Jeramy'],
                ['+13399701526','Lukas'],
                ['+12146295806','Yolanda'],
                ['+12147242557','Genia'],
                ['+12147242557','Genia'],
                ['+16197152424','Victoria'],
                ['+14693878919','Baily'],
                ['+12142289962','Matthew'],
                ['+12147716390','Brennan'],
                ['+12146972298','Bradley'],
                ['+19729987231','Debra'],
                ['+12143956368','Patrick'],
                ['+19723229613','Alex'],
                ['+14693588622','Servando'],
                ['+14699395330','Lucas'],
                ['+15129226550','Jules'],
                ['+12147976730','Cathy'],
                ['+17073300715','Deborah'],
                ['+14693607337','Jennifer'],
                ['+19723584796','Julie'],
                ['+12142184386','Alexandria'],
                ['+12146620767','Benson'],
                ['+14052497963','Kennedy'],
                ['+12147320150','Roberto'],
                ['+12142938385','Alicia'],
                ['+14697740908','Ivan'],
                ['+19726895033','Ashley'],
                ['+19729652972','Pamela'],
                ['+12146972298','Dana'],
                ['+12548551710','Susan'],
                ['+12146329773','Lacy'],
                ['+12147089739','Stacie'],
                ['+12145524540','Norman'],
                ['+19723335204','Matthew'],
                ['+19726211584','Anastasia'],
                ['+12148377608','Mark'],
                ['+19723587797','Kevin'],
                ['+19405976296','James'],
                ['+18587404335','Michael'],
                ['+12142124370','Kayla'],
                ['+19794180529','Annie'],
                ['+19722777089','Tristan'],
                ['+19728397253','Jery'],
                ['+14693236063','Patrice'],
                ['+18034796705','Kinnon'],
                ['+12144974015','Loren'],
                ['+18176635645','Tamika'],
                ['+16192518437','Cathy'],
                ['+19729535020','Shirley'],
                ['+14403822497','Jacqueline'],
                ['+19729793624','Kevin'],
                ['+14695695623','Paul'],
                ['+12148422067','Marianne'],
                ['+19403058266','Hayden'],
                ['+13367076663','Michael'],
                ['+12146086468','Erika'],
                ['+12147105264','Jimmie'],
                ['+12146360169','Catherine'],
                ['+12149302028','Alexis'],
                ['+18323498631','Bryan'],
                ['+12104285650','Ross'],
                ['+12169736944','Armando'],
                ['+19722078283','Deborah'],
                ['+14698479894','Lisa'],
                ['+12147387477','Darla'],
                ['+18322769106','Alyssa'],
                ['+19725890803','Audrey'],
                ['+12316313367','Alexander'],
                ['+19729783889','Bailey'],
                ['+12146939165','Brandon'],
                ['+17046410155','William'],
                ['+14693347133','Teresa'],
                ['+12146854643','Rocio'],
                ['+19729551285','Ann'],
                ['+16786501267','Ethan'],
                ['+12144022122','Laura'],
                ['+19729987231','Jacqueline'],
                ['+14697329978','Marcela'],
                ['+14693383701','Dawn'],
                ['+19727414998','Malcolm'],
                ['+12142124399','Eric'],
                ['+14694718991','Mary'],
                ['+14694326505','Richard'],
                ['+12816358918','Michael'],
                ['+19728352384','Joe'],
                ['+12147711288','Charli'],
                ['+16098201405','Joseph'],
                ['+14693158338','Rosa'],
                ['+15126981792','Barbara'],
                ['+18062529072','Anusha'],
                ['+19728412999','Darrell'],
                ['+19407831118','Erin'],
                ['+12143567873','Toni'],
                ['+14696678750','Erica'],
                ['+12147976730','Hal'],
                ['+19035743235','Linda'],
                ['+14693234797','McKinleigh'],
                ['+12546403368','Guillermo'],
                ['+14693584203','Anne'],
                ['+12149919184','James'],
                ['+14693714627','Christopher'],
                ['+12144768876','Michael'],
                ['+12147960257','Roxann'],
                ['+14697355828','Linda'],
                ['+12146972299','Rodney'],
                ['+12145296915','Katherin'],
                ['+19032852034','Justin'],
                ['+12145158535','Tommy'],
                ['+19727548871','Bryan'],
                ['+19729770721','Amy'],
                ['+12146976139','Lauren'],
                ['+13868717888','MiLLiE'],
                ['+15402226676','Cody'],
                ['+14693234797','Blaize'],
                ['+12149311647','Jazze’'],
                ['+19728008224','Tammy'],
                ['+19728354055','Tracy'],
                ['+12512722068','Tara'],
                ['+19703969791','Kristin'],
                ['+14692339612','Kevin'],
                ['+12145573833','Ryan'],
                ['+14403822497','Stefanie'],
                ['+14693584203','Korey'],
                ['+19728413741','Linda'],
                ['+12145055336','Leslie'],
                ['+12149572300','Rene'],
                ['+19794504878','Cassandra'],
                ['+19152569078','Adrian'],
                ['+19288975428','Colter'],
                ['+19723107597','Matthew'],
                ['+18479158668','Heidi'],
                ['+19729659687','Kenneth'],
                ['+14693078335','Samuel'],
                ['+12147344086','Mike'],
                ['+19727417207','Gerardo'],
                ['+19047037608','Cassandra'],
                ['+19729488497','Reginald'],
                ['+12512722068','David'],
                ['+12148094923','Hector'],
                ['+12147993972','Nickole'],
                ['+19729896911','Patricia'],
                ['+12147159881','Cecilia'],
                ['+19724673955','Bret'],
                ['+16263886286','Mary'],
                ['+14698563796','Walter'],
                ['+14697698813','Hayli'],
                ['+18603047866','Clayton'],
                ['+12143167733','Robert'],
                ['+12147331504','Karim'],
                ['+14696883095','Willie'],
                ['+14696445680','Duante'],
                ['+12147089842','Tiffany'],
                ['+12148421902','Joseph'],
                ['+13173634990','Edward'],
                ['+19727506982','Stephen'],
                ['+19035139390','Tammy'],
                ['+19729790986','Ernest'],
                ['+12149232707','Oscar'],
                ['+19728399469','Tommy'],
                ['+15868762526','Shilpa'],
                ['+18177260795','Diana'],
                ['+12816353420','Norman'],
                ['+12146809099','Stephen'],
                ['+12145787889','Avery'],
                ['+19727506982','Colton'],
                ['+19725678082','Ashley'],
                ['+14692030948','Debora'],
                ['+19175091233','Eva'],
                ['+12145573833','Richard'],
                ['+19725107289','Marlana']
    ]
    data = []
    for row in rows:
        phone_number = row[0]
        first_name = row[1]
        message = """Hi {}, We apologize but will not have the supplies to give you the J&J vaccine today. Please reschedule your appointment for this Friday, April 2nd and Saturday, April 3rd. The appointments on the 2nd and 3rd will be for the Pfizer vaccine. That is the only option at this time. Reschedule your appointment here: https://rockwall.gogetvax.com. If you don't see a location to register, please try in about 15 mins. Sorry for any inconvenience. """.format(first_name)

        data.append(
            (phone_number, message)
        )

    batch_enqueue_sms_notifications(data)

def process_vax():
    from ggt.tasks.vax_tx_outbound_hl7 import (
         process_vax_hl7         
    )
    process_vax_hl7()
    