import datetime

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_rows,
    exec_batch_execute)

import ggt.lib.constants as c

from ggt.lib.sms import send_sms
from ggt.models.data_models.data_types import NotificationEnum


def notify_patients(req):
    location_id = req.location_id
    type = req.type
    start_dt = req.start_dt
    end_dt = req.end_dt
    reschedule_mins = req.reschedule_mins
    reschedule_hours = req.reschedule_hours
    reschedule_days = req.reschedule_days

    patients = get_notify_patients(location_id, start_dt, end_dt)
    reschedule_list = []

    try:
        for p in patients:
            phone_number = p['phone_number']
            email = p['email']
            first_name = p['first_name']
            last_name = p['last_name']
            appointment_id = p['appointment_id']
            scheduled_dt = p['scheduled_dt']
            new_schedule = get_new_schedule_dt(scheduled_dt, reschedule_mins, reschedule_hours, reschedule_days)
            message = get_message(type, first_name, last_name, new_schedule)
            reschedule = (str(new_schedule), appointment_id)
            reschedule_list.append(reschedule)
            # send_sms(phone_number, message)

        update_appointments(reschedule_list)
    except Exception as err:
            log_generic(
                type=c.ERROR,
                function=whoami(),
                error=err
            )


def update_appointments(data):
    sql = """UPDATE appointments 
             SET 
                scheduled_dt = %s
             WHERE
                id = %s;"""
    return exec_batch_execute(sql, data)


def get_message(type, first_name, last_name, new_schedule):

    if type is NotificationEnum.reschedule:
        message = "Hi {}, your GoGetTested.com COVID-19 test appointment is rescheduled. Your new appointment is {}. " \
              "Please follow this link for more " \
              "information https://start.gogettested.com".format(first_name, new_schedule)

    if type is NotificationEnum.cancelled:
        message = "Hi {}, your GoGetTested.com COVID-19 test appointment is cancelled." \
              "Please follow this link for more " \
              "information https://start.gogettested.com".format(first_name)
    return message


def get_notify_patients(location_id, start_dt, end_dt):
    sql = """SELECT 
                p.phone_number,
                p.email,
                p.first_name,
                p.last_name,
                a.scheduled_dt,
                a.id as appointment_id
            FROM
                appointments a inner join
                patients p on a.patient_id = p.id 
            WHERE a.scheduled_dt >= '{}' AND a.scheduled_dt <= '{}' AND a.location_id = {};""".format(start_dt, end_dt,
                                                                                                      location_id)
    return read_rows(sql)


def get_new_schedule_dt(date, mins=0, hours=0, days=0):
    try:
        new_date = date + datetime.timedelta(days=days,
                                             hours=hours,
                                             minutes=mins,
                                             seconds=0,
                                             microseconds=0)
        return new_date

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
