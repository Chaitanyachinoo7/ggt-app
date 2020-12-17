from datetime import datetime, timedelta

import ggt.lib.constants as c
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
from ggt.lib.utils import (
    log_generic,
    whoami,
    get_config_val)
from ggt.models.data_models.data_types import NotificationEnum
from ggt.tasks.report_notifications import batch_enqueue_email_notifications, batch_enqueue_sms_notifications

base_url = get_config_val('base_url')
from_email = get_config_val('notifications.from_email')
from_name = get_config_val('notifications.from_name')
reschedule_subject = get_config_val('notifications.reschedule_subject')
relocate_subject = get_config_val('notifications.relocate_subject')
relocate_template = get_config_val('notifications.relocate_template')
reschedule_template = get_config_val('notifications.reschedule_template')


async def notify_patients(req):
    location_id = req.location_id
    req_type = req.type
    start_dt = req.start_dt
    end_dt = req.end_dt
    next_location_id = location_id

    if req_type == NotificationEnum.relocate:
        next_location_id = req.next_location_id

    patients = await get_notify_patients(location_id, next_location_id, start_dt, end_dt)
    reschedule_list = []
    email_list = []
    sms_list = []
    try:
        for p in patients:
            email = await get_email_body(p, req_type)
            sms = await get_sms_body(p, req_type)

            if email is not None:
                email_list.append((
                    email['from_email'],
                    email['from_name'],
                    email['to_email'],
                    email['subject'],
                    email['html_content']
                ))

            if sms is not None:
                sms_list.append((
                    sms['to_number'],
                    sms['message']
                ))
            reschedule_list.append(('cancelled', p['appointment_id']))

        batch_enqueue_email_notifications(tuple(email_list))
        batch_enqueue_sms_notifications(tuple(sms_list))
        update_appointments(reschedule_list)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def get_email_body(data, req_type):
    if req_type == NotificationEnum.relocate:
        return get_relocate_email_body(data)
    if req_type == NotificationEnum.reschedule:
        return get_reschedule_email_body(data)
    return None


async def get_sms_body(data, req_type):
    if req_type == NotificationEnum.relocate:
        return get_relocate_sms_body(data)
    if req_type == NotificationEnum.reschedule:
        return get_reschedule_sms_body(data)
    return None


async def get_reschedule_sms_body(data):
    try:

        scheduled_dt = str(data['scheduled_dt'])
        test_date = datetime.strptime(
            scheduled_dt[0:10], "%Y-%m-%d").strftime('%A %d %B %Y')
        test_time = datetime.strptime(
            str(scheduled_dt[11: len(scheduled_dt)]), "%H:%M:%S").strftime("%I:%M %p")
        template_vars = {
            "first_name": data['first_name'],
            "test_number": data['appointment_id'],
            "test_location_line1": data['new_addr1'] if data['new_addr1'] else '',
            "test_location_line2": data['new_addr2'] if data['new_addr2'] else '',
            "test_location_line3": data['new_addr3'] if data['new_addr3'] else '',
            "test_date": test_date,
            "test_time": test_time,
            "test_location_address": "{}, {}, {}".format(data['new_addr1'] if data['new_addr1'] else '',
                                                         data['new_addr2'] if data['new_addr2'] else '',
                                                         data['new_addr3'] if data['new_addr3'] else '')
        }

        message = "Hi {}, \nwe’ve had to close the testing location where you have registered for your " \
                  "COVID-19 test. We apologize for the inconvenience this may cause. Please visit GoGetTested.com and " \
                  "register for another appointment at a convenient location. \nThank you for choosing " \
                  "GoGetTested.".format(template_vars['first_name'])

        formatted = {
            'to_number': data['phone_number'],
            'message': message
        }
        return formatted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def get_relocate_sms_body(data):
    try:

        scheduled_dt = str(data['scheduled_dt'])
        test_date = datetime.strptime(
            scheduled_dt[0:10], "%Y-%m-%d").strftime('%A %d %B %Y')
        test_time = datetime.strptime(
            str(scheduled_dt[11: len(scheduled_dt)]), "%H:%M:%S").strftime("%I:%M %p")
        template_vars = {
            "first_name": data['first_name'],
            "test_number": data['appointment_id'],
            "test_location_line1": data['new_addr1'] if data['new_addr1'] else '',
            "test_location_line2": data['new_addr2'] if data['new_addr2'] else '',
            "test_location_line3": data['new_addr3'] if data['new_addr3'] else '',
            "test_date": test_date,
            "test_time": test_time,
            "test_location_address": "{}, {}, {}".format(data['new_addr1'] if data['new_addr1'] else '',
                                                         data['new_addr2'] if data['new_addr2'] else '',
                                                         data['new_addr3'] if data['new_addr3'] else '')
        }

        message = "Hi {}, we’ve had to change your testing location to {}. If you’re unable to make your " \
                  "appointment because of this change, please visit GoGetTested.com and register for another " \
                  "appointment at a convenient location. We apologize fm ".format(template_vars['first_name'],
                                                                                  template_vars[
                                                                                      'test_location_address'])

        formatted = {
            'to_number': data['phone_number'],
            'message': message
        }
        return formatted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def get_reschedule_email_body(data):
    try:

        scheduled_dt = str(data['scheduled_dt'])
        test_date = datetime.strptime(
            scheduled_dt[0:10], "%Y-%m-%d").strftime('%A %d %B %Y')
        test_time = datetime.strptime(
            str(scheduled_dt[11: len(scheduled_dt)]), "%H:%M:%S").strftime("%I:%M %p")
        template_vars = {
            "first_name": data['first_name'],
            "test_number": data['appointment_id'],
            "test_location_line1": data['new_addr1'] if data['new_addr1'] else '',
            "test_location_line2": data['new_addr2'] if data['new_addr2'] else '',
            "test_location_line3": data['new_addr3'] if data['new_addr3'] else '',
            "test_date": test_date,
            "test_time": test_time,
            "test_location_address": "{}, {}, {}.".format(data['new_addr1'] if data['new_addr1'] else '',
                                                          data['new_addr2'] if data['new_addr2'] else '',
                                                          data['new_addr3'] if data['new_addr3'] else '')
        }
        html_content = await render_template(reschedule_template, **template_vars)
        email_message = {
            'from_email': from_email,
            'from_name': from_name,
            'to_email': data['email'],
            'subject': reschedule_subject,
            'html_content': html_content
        }
        return email_message

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def get_relocate_email_body(data):
    try:

        scheduled_dt = str(data['scheduled_dt'])
        test_date = datetime.strptime(
            scheduled_dt[0:10], "%Y-%m-%d").strftime('%A %d %B %Y')
        test_time = datetime.strptime(
            str(scheduled_dt[11: len(scheduled_dt)]), "%H:%M:%S").strftime("%I:%M %p")
        template_vars = {
            "first_name": data['first_name'],
            "test_number": data['appointment_id'],
            "test_location_line1": data['new_addr1'] if data['new_addr1'] else '',
            "test_location_line2": data['new_addr2'] if data['new_addr2'] else '',
            "test_location_line3": data['new_addr3'] if data['new_addr3'] else '',
            "test_date": test_date,
            "test_time": test_time,
            "test_location_address": "{}, {}, {}.".format(data['new_addr1'] if data['new_addr1'] else '',
                                                          data['new_addr2'] if data['new_addr2'] else '',
                                                          data['new_addr3'] if data['new_addr3'] else '')
        }
        html_content = await render_template(relocate_template, **template_vars)
        email_message = {
            'from_email': from_email,
            'from_name': from_name,
            'to_email': data['email'],
            'subject': relocate_subject,
            'html_content': html_content
        }
        return email_message

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def update_appointments(data):
    sql = """UPDATE appointments 
             SET 
                status = %s
             WHERE
                id = %s;"""
    return exec_batch_execute(sql, data)


async def get_notify_patients(location_id, next_location_id, start_dt, end_dt):
    sql = """SELECT 
    p.phone_number,
    p.email,
    p.first_name,
    p.last_name,
    a.scheduled_dt,
    a.id AS appointment_id,
    l.addr1 AS new_addr1,
    l.addr2 AS new_addr2,
    l.addr3 AS new_addr3
FROM
    appointments a
        INNER JOIN
    patients p ON a.patient_id = p.id,
    locations l
            WHERE a.scheduled_dt >= '{}' AND a.scheduled_dt <= '{}' AND a.location_id = {} 
            AND l.id = {};""".format(start_dt, end_dt, location_id, next_location_id)
    return replica_read_rows(sql)
