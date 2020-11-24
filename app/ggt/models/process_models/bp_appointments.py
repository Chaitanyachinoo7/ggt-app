import datetime

import ggt.lib.constants as c

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.sms import (
    send_sms
)

from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_checkin,
    update_appointment_with_test_start,
    update_appointment_with_scan_vial,
    update_appointment_with_test_completed
)

from ggt.lib.sys_log import (write_syslog)

########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_appointment_info(appointment_id, dob):
    try:
        appointment = get_appointment(appointment_id)
        if dob != 'allowdoboverride' and appointment.patient.dob.strftime("%Y%m%d") != dob:
            raise ValueError('Invalid Appointment and DOB')

        if appointment.status == 'pending':
            raise ValueError('Appointment is still pending')

        else:
            return {
                "appointment_id": appointment.id,
                "date": __formatted_date_text(appointment),
                "location": __formatted_location_text(appointment),
                "patient_dob": __formatted_patient_dob(appointment),
                "patient_name": __formatted_patient_name(appointment),
                "patient_address": __formatted_patient_address(appointment),
                "next_action": __next_action(appointment),
                "service_selection": appointment.service_selection,
                "service_selection_codes": appointment.service_selection_codes
            }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return False


def bp_appointment_update(appointment_id: int, action: str, workstation_id: int):
    try:
        appointment = get_appointment(appointment_id)
            
        if action == c.APPOINTMENT_ACTION_CHECK_IN:
            update_appointment_with_checkin(appointment_id)

        elif action == c.APPOINTMENT_ACTION_START_TEST:
            __appointment_begin_test(appointment_id, workstation_id)

        elif action == c.APPOINTMENT_ACTION_SCAN_VIAL:
            update_appointment_with_scan_vial(appointment_id)
            
        elif action == c.APPOINTMENT_ACTION_END_TEST:
            update_appointment_with_test_completed(appointment_id)
            __send_test_complete_sms(appointment)
            
        elif action == c.APPOINTMENT_ACTION_REPRINT:
            __appointment_reprint_label(appointment_id, workstation_id)

        #TODO: This allows the start_test to be invoked twice (print the label twice). And every other action only to be invoked once.
        # essentially works by waiting to catch the appointment status update in the next round
        # Ideally, this should be handled at the printer label processor
        if action != c.APPOINTMENT_ACTION_START_TEST:
            appointment = get_appointment(appointment_id)

        return {
            'appointment_id': appointment.id,
            'next_action': __next_action(appointment, __is_pre_labeled(workstation_id)),
        }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return False

########################################################################################################
# [Protected] functions
########################################################################################################
def __is_pre_labeled(workstation_id: int) -> bool:
    return False if workstation_id<100000 else True

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


def __next_action(appointment, pre_labeled=False):
    switcher = {
        c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
        c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_TEST,
        c.APPOINTMENT_STATUS_TEST_IN_PROGRESS: c.APPOINTMENT_ACTION_SCAN_VIAL,
        c.APPOINTMENT_STATUS_VIAL_SCANNED: c.APPOINTMENT_ACTION_END_TEST,
        c.APPOINTMENT_STATUS_TEST_COMPLETED: c.APPOINTMENT_ACTION_NONE
    }

    if not pre_labeled: #vial scanning not required
        switcher = {
            c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
            c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_TEST,
            c.APPOINTMENT_STATUS_TEST_IN_PROGRESS: c.APPOINTMENT_ACTION_END_TEST,
            c.APPOINTMENT_STATUS_TEST_COMPLETED: c.APPOINTMENT_ACTION_NONE
        }

    return switcher.get(appointment.status, c.APPOINTMENT_ACTION_NONE)


#TODO: [GGT-80] Move copy to CMS
def __send_test_complete_sms(appointment):
    message = "" \
        "Hi {}, thank you for getting tested with GoGetTested.com. Your COVID-19 test results will be available in 48-96hours. " \
        "If you have any questions, please visit GoGetTested.com Reply STOP to cancel msgs".format(appointment.patient.first_name)

    log_generic(
        type="info",
        first_name=appointment.patient.first_name,
        message=message,
        function='__send_test_complete_sms'
    )
    return send_sms(appointment.patient.phone_number, message)


def __appointment_begin_test(appointment_id, workstation_id=1):
    update_appointment_with_test_start(appointment_id)

    if __is_pre_labeled(workstation_id):
        return True
    
    return __send_label_to_printer(appointment_id, workstation_id)

def __appointment_reprint_label(appointment_id, workstation_id=1):
    return __send_label_to_printer(appointment_id, workstation_id)


#TODO: [GGT-86] Refactor, decouple integration code
def __send_label_to_printer(appointment_id, queue_id):
    import json
    import boto3

    try:
        appointment = get_appointment(appointment_id)
        date_text = appointment.scheduled_dt.strftime(
            "%a, %-d %b %Y @ %-I:%M %p")
        patient_name = "{}, {} {}".format(appointment.patient.last_name,
                                          appointment.patient.first_name,
                                          appointment.patient.middle_name,
                                          )

        queue_url = "{}-{}".format(get_config_val(
            'aws.sqs_print_queue_base_url'), queue_id)

        write_syslog("print", c.INFO, appointment_id)

        payload = {
            "barcode_text": "{}".format(appointment_id),
            "name_text": patient_name,
            "dob_text": appointment.patient.dob.strftime("%m/%d/%Y"),
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
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )
        write_syslog("print", c.ERROR, appointment_id)
        return False
