import os
import os.path
from os import path
import glob
import csv
from datetime import datetime
import time
import paramiko
import itertools
import shutil
from pathlib import Path


from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_batch_execute,
    exec_update,
    read_row,
    read_rows
)

from ggt.lib.storage import (
    file_exists_in_all_inbound_files,
    upload_lab_report,
    upload_to_all_inbound_files
)

from ggt.models.data_models.tasks_local_cache import (
    init_local_cache,
    add_to_lab_test_records_cache,
    get_all_lab_records_from_cache,
    add_to_all_inbound_files_cache,
    file_exists_in_all_inbound_files_cache,
    get_order_number_by_requisition_id,
    add_to_files_in_remote_storage_cache,
    file_exists_in_files_in_remote_storage_cache,
    add_to_csv_pdf_sync_cache
)

session_id = generate_session_id()


def task_process_sms_reminders():
    try:
        start = time.time()
        print_header(
            '\n\n******************SMS Reminder Task started at [Start]******************************\n\n')
        log_generic(
            type="info",
            function='task_process_sms_reminders',
            task_session_id=session_id,
            info='SMS Reminders started')
        rows = get_appointments_for_today()
        print(rows)
        data = []
        # for row in rows:
        # phone_number = row['phone_number']
        # data.append(
        #     (phone_number, prepare_sms_text(row))
        # )
        data.append(
            ("+14372309014", prepare_sms_text(rows[0])[0])
        )
        data.append(
            ("+14372309014", prepare_appointment_details(rows[0]))
        )
        batch_enqueue_sms_notifications(data)
        log_generic(
            type="info",
            function='task_process_inbound_lab_reports',
            task_session_id=session_id,
            info='End SMS Reminders')

        print_header(
            '\n\n****************** COMPLETED ******************************\nElapsed Time: {}\n'.format(time.time() - start))
    except Exception as err:
        print(err)


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


def get_appointments_for_today():
    try:
        sql = """
        SELECT a.id, a.scheduled_dt, b.first_name, b.phone_number, b.dob, c.addr1, IFNULL(c.addr2,"") as addr2, c.city, c.st, c.zip 
        FROM appointments a 
        JOIN patients b ON a.patient_id = b.id
        JOIN locations c ON a.location_id = c.id
        where scheduled_dt LIKE %s
        """
        vals = (datetime.today().strftime('%Y-%m-%d')+'%',)
        return read_rows(sql, vals)
    except Exception as err:
        print(err)


def prepare_sms_text(appointment):
    base_url = get_config_val('base_url')
    return "Hi {}, this is a reminder for your COVID-19 testing appointment scheduled today at {} at {}. Click the link for appointment details: {}/appointment/{}/{}".format(
        appointment["first_name"], str(appointment["scheduled_dt"].strftime('%I:%M%p')), str(appointment["addr1"]) + " " + appointment["addr2"] + ", " + str(appointment["city"]) + ", " + str(appointment["st"]) + " " + str(appointment["zip"]), base_url, appointment["id"], str(appointment["dob"]).replace('-', '')),


def prepare_appointment_details(appointment):
    print(appointment["scheduled_dt"].strftime('%I:%M%p'))
    return "Please make sure to bring and show this QR code {}/appointment/{}/{}, and Acceptable ID when you arrive at the test. We will scan the QR code to check you in for testing. Please no eating or drinking at least 15 minutes prior to testing as this may impact your test results.".format(
        get_config_val('base_url'), str(appointment["id"]).rjust(6, '0'), str(appointment["dob"]).replace('-', ''))


def print_header(message):
    print('{.HEADER}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok1(message):
    print('{.OKGREEN}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok2(message):
    print('{.OKBLUE}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_warning(message):
    print('{.WARNING}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_error(message):
    print('{.FAIL}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_progress_bar_message(message):
    print('{.OKBLUE}{}{.ENDC}\r'.format(bcolors, message, bcolors), end="")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
