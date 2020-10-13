import datetime 

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)
from ggt.lib.sms import (send_sms)
from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_checkin,
    update_appointment_with_test_start,
    update_appointment_with_test_completed
)

'''
,
    get_monthy_calendar,
    positive_result_followup,
    update_positive_result_followup,
    get_user_role,
    get_test_results
'''

from ggt.lib.sys_log import (write_syslog)

'''
from ggt.models.data_models.test_results import (
    update_appointment_with_checkin,
    update_test_with_test_start,
    update_test_with_test_completed
)
'''
########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_appointment_info(appointment_id, dob):
    try:
        appointment = get_appointment(appointment_id)
        if dob != 'allowdoboverride' and appointment.patient.dob.strftime("%Y%m%d") != dob:
            return False

        if appointment['status'] == 'pending':
            return False
        else:
            return {
                "appointment_id": appointment.id,
                "date": __formatted_date_text(appointment),
                "location": __formatted_location_text(appointment),
                "patient_dob": __formatted_patient_dob(appointment),
                "patient_name": __formatted_patient_name(appointment),
                "patient_address": __formatted_patient_address(appointment),
                "next_action": __next_action(appointment)
            }
    except Exception as err:
        log_generic(
            type=ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return False


def bp_appointment_update(appointment_id, action, workstation_id):
    try:
        appointment = get_appointment(appointment_id)

        if action == 'checkin' or action == 'check_in':
            update_appointment_with_checkin(appointment_id)
        elif action == 'start_test':
            __appointment_begin_test(appointment_id, workstation_id)
        elif action == 'end_test':
            update_appointment_with_test_completed(appointment_id)
            __send_test_complete_sms(
                appointment['phone_number'], appointment['first_name'])
        elif action == 'reprint':
            __appointment_reprint_label(appointment_id, workstation_id)

        return {
            'appointment_id': appointment_id,
            'next_action': __next_action(appointment),
        }
    except Exception as err:
        log_generic(
            type=ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return False


'''
def bp_get_monthly_calendar(date, location_id):
    try:
        print(date, location_id)
        date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        from_date = date_time_obj.date().replace(day=1)
        to_date = date_time_obj.date().replace(day=31)
        results = get_monthy_calendar(from_date, to_date, location_id)
        # print(results)
        response = []
        for record in results:
            # print(record)
            appointment = {}
            appointment['title'] = record['last_name'] + \
                ", " + record['first_name']
            appointment['start'] = record['scheduled_dt']
            appointment['end'] = record['scheduled_dt'] + \
                datetime.timedelta(minutes=30)
            appointment['allDay'] = False
            appointment['backgroundColor'] = "#3c8dbc"
            response.append(appointment)
        return response
    except Exception as err:
        log_generic(
            type=ERROR,
            date=date,
            location_id=location_id,
            function=whoami(),
            error=err
        )


def bp_provider_positive_result_followup():
    try:
        results = positive_result_followup()
        update_positive_result_followup(
            results['test_id'], datetime.datetime.now())
        return results
    except Exception as err:
        log_generic(
            type=ERROR,
            location_id="",
            function=whoami(),
            error=err
        )


'''
########################################################################################################
# [Protected] functions
########################################################################################################


def __formatted_date_text(appointment):
    return appointment.scheduled_dt.strftime("%a, %-d %b %Y @ %-I:%M %p")


def __formatted_location_text(appointment):
    # 6155 Sports Village Rd, Frisco, TX 75033
    return "{}, {} {}  {}".format(appointment.location.addr1,
                                  appointment.location.city,
                                  appointment.location.st,
                                  appointment.location.zip)


def __formatted_patient_address(appointment):
    return "{}, {} {}  {}".format(appointment.patient.addr1,
                                  appointment.patient.city,
                                  appointment.patient.st,
                                  appointment.patient.zip)


def __formatted_patient_name(appointment):
    return "{} {} {}".format(
        appointment.patient.first_name,
        appointment.patient.middle_name,
        appointment.patient.last_name)


def __formatted_patient_dob(appointment):
    return appointment.patient.dob.strftime("%m/%d/%Y")


def __next_action(appointment):
    switcher = {
        'scheduled': 'check_in',
        'checked_in': 'start_test',
        'test_in_progress': 'end_test'
    }
    return switcher.get(appointment.status, "")


def __send_test_complete_sms(phone, first_name):
    message = "Hi {}, thank you for getting tested with GoGetTested.com. Your COVID-19 test results will be available in 48-96hours. If you have any questions, please visit GoGetTested.com".format(
        first_name)
    log_generic(
        type="info",
        first_name=first_name,
        message=message,
        function='__send_test_complete_sms'
    )
    return send_sms(phone, message)


def __appointment_begin_test(appointment_id, workstation_id=1):
    update_appointment_with_test_start(appointment_id)
    return __send_label_to_printer(appointment_id, workstation_id)


def __appointment_reprint_label(appointment_id, workstation_id=1):
    return __send_label_to_printer(appointment_id, workstation_id)


def __send_label_to_printer(appointment_id, queue_id):
    import json
    import boto3

    try:
        appointment = get_appointment(appointment_id)
        date_text = appointment['scheduled_dt'].strftime(
            "%a, %-d %b %Y @ %-I:%M %p")
        patient_name = "{}, {} {}".format(appointment['last_name'],
                                          appointment['first_name'],
                                          appointment['middle_name'],
                                          )

        queue_url = "{}-{}".format(get_config_val(
            'aws.sqs_print_queue_base_url'), queue_id)

        write_syslog("print", INFO, appointment_id)

        # TODO FIX all this
        payload = {
            "barcode_text": "{}".format(appointment_id),
            "name_text": patient_name,
            "dob_text": appointment['dob'].strftime("%m/%d/%Y"),
            "timestamp_text": date_text
        }

        sqs = boto3.client(
            "sqs",
            aws_access_key_id=get_config_val('aws.access_key_id'),
            aws_secret_access_key=get_config_val('aws.secret_access_key'),
            region_name='us-east-1'
        )
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageBody=(json.dumps(payload))
        )
        print(response['MessageId'])

        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            appointment_id=appointment_id,
            function=whoami(), 
            error=err
        )
        write_syslog("print", ERROR, appointment_id)
        return False
