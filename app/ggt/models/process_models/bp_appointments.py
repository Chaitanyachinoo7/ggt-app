import datetime

import ujson
import boto3

from cachetools import cached, LRUCache, TTLCache

import ggt.lib.constants as c
from ggt.lib.adapters.sqs_adapter import push_sqs_message
from ggt.lib.adapters.twilio_adapter import send_twilio_sms

from ggt.models.data_models.data_types import (
    GgtAppointment
)

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami, is_international
)

from ggt.lib.sms import (
    send_sms
)

from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_checkin,
    update_appointment_with_test_start,
    update_appointment_with_scan_vial,
    update_appointment_with_test_completed, update_appointment_with_start_vax, update_appointment_with_notes_vax,
    update_appointment_with_scan_vial_vax, update_appointment_with_end_vax, __has_insurance_info,
    update_appointment_with_verify_insurance, get_service_type_by_appointment_id, create_consultation_note
)

from ggt.lib.sys_log import (write_syslog)


########################################################################################################
# [Public] functions
########################################################################################################
from ggt.models.process_models.bp_patient_experience import __save_insurance_image


@cached(cache=TTLCache(maxsize=1024, ttl=30))
def bp_get_appointment_info(appointment_id, dob, org_id=None):
    try:
        appointment: GgtAppointment = get_appointment(appointment_id, org_id=org_id)
        if dob != 'allowdoboverride' and appointment.patient.dob.strftime("%Y%m%d") != dob:
            raise ValueError('Invalid Appointment and DOB')

        if appointment.status == 'pending':
            raise ValueError('Appointment is still pending')

        else:
            return {
                "appointment_id": appointment.id,
                "org_name": appointment.org_name,
                "date": __formatted_date_text(appointment),
                "location": __formatted_location_text(appointment),
                "patient_dob": __formatted_patient_dob(appointment),
                "patient_name": __formatted_patient_name(appointment),
                "patient_address": __formatted_patient_address(appointment),
                "next_action": __next_action(appointment, appointment.service_selection_codes[0]),
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


def bp_appointment_update(provider_update_appointment_request, user):
    usuccess = False
    appointment_id = provider_update_appointment_request.appointment_id
    action = provider_update_appointment_request.action
    workstation_id = provider_update_appointment_request.workstation_id
    operator_location_id = provider_update_appointment_request.operator_location_id
    service_code = provider_update_appointment_request.service_code

    log_generic(
        position=1,
        type=c.INFO,
        appointment_id=appointment_id,
        function=whoami(),
        action=action,
        workstation_id=workstation_id,
        operator_location_id=operator_location_id
    )

    try:
        appointment: GgtAppointment = get_appointment(appointment_id)

        if action == c.APPOINTMENT_ACTION_START_VAX:
            usuccess = update_appointment_with_start_vax(appointment, user, operator_location_id=operator_location_id)

        elif action == c.APPOINTMENT_ACTION_VERIFY_INSURANCE:
            usuccess = update_appointment_with_verify_insurance(appointment, user,
                                                                operator_location_id=operator_location_id)
            if usuccess:
                __save_insurance_image(appointment_id, provider_update_appointment_request.insurance_photo)

        elif action == c.APPOINTMENT_ACTION_END_VAX:
            usuccess = update_appointment_with_end_vax(appointment, user, workstation_id,
                                                       operator_location_id=operator_location_id)
            if usuccess:
                __send_vax_completion_sms(appointment.patient.first_name, appointment.patient.phone_number)
                __send_vax_completion_confirmation_in_15_minutes(appointment.patient.first_name,
                                                                 appointment.patient.phone_number)

        elif action == c.APPOINTMENT_ACTION_NOTES_VAX:
            usuccess = update_appointment_with_notes_vax(appointment, user, workstation_id,
                                                         provider_update_appointment_request.injection_site,
                                                         provider_update_appointment_request.no_adverse_reactions,
                                                         operator_location_id=operator_location_id)
            if usuccess:
                create_consultation_note(user, appointment_id, provider_update_appointment_request.appointment_notes)

        elif action == c.APPOINTMENT_ACTION_CHECK_IN:
            usuccess = update_appointment_with_checkin(appointment, user, operator_location_id=operator_location_id)

        elif action == c.APPOINTMENT_ACTION_START_TEST:
            usuccess = __appointment_begin_test(user, appointment, workstation_id,
                                                operator_location_id=operator_location_id)

        elif action == c.APPOINTMENT_ACTION_SCAN_VIAL:
            usuccess, reason_code = update_appointment_with_scan_vial(appointment,
                                                                      provider_update_appointment_request.vial_data.vial_id,
                                                                      user, operator_location_id=operator_location_id)
            if not usuccess:
                return {
                    c.STATUS: c.FAILED,
                    c.REASON_CODE: reason_code
                }

        elif action == c.APPOINTMENT_ACTION_SCAN_VIAL_VAX:
            usuccess, reason_code = update_appointment_with_scan_vial_vax(appointment, provider_update_appointment_request.vial_data,
                                                             user, operator_location_id=operator_location_id)
            if not usuccess:
                return {
                    c.STATUS: c.FAILED,
                    c.REASON_CODE: reason_code
                }

        elif action == c.APPOINTMENT_ACTION_END_TEST:
            usuccess = update_appointment_with_test_completed(appointment, user,
                                                              operator_location_id=operator_location_id)
            if usuccess:
                __send_test_complete_sms(appointment)

        elif action == c.APPOINTMENT_ACTION_REPRINT:
            usuccess = __appointment_reprint_label(user, appointment, workstation_id)

        # TODO: This allows the start_test to be invoked twice (print the label twice). And every other action only to be invoked once.
        # essentially works by waiting to catch the appointment status update in the next round
        # Ideally, this should be handled at the printer label processor
        if usuccess and (action != c.APPOINTMENT_ACTION_START_TEST or __is_pre_labeled(appointment, workstation_id)):
            appointment: GgtAppointment = get_appointment(appointment_id)
        next_action = __next_action(appointment, service_code,  __is_pre_labeled(appointment, workstation_id))
        if usuccess:
            '''
                Added this log to identify GGT-531 issue.
            '''
            log_generic(
                position=2,
                type=c.INFO,
                appointment_id=appointment_id,
                function=whoami(),
                action=action,
                next_action=next_action,
                workstation_id=workstation_id,
                operator_location_id=operator_location_id
            )

            return {
                'appointment_id': appointment.id,
                'next_action': next_action
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

def __is_pre_labeled(appointment: GgtAppointment, workstation_id: int) -> bool:
    return True
    '''Now we dont use workstations to print labels, this code is to be depreciate'''
    # return True if (appointment.location.test_type_offered == 'oral_fluid' or workstation_id > 10000) else False


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


def __next_action(appointment, service_code, pre_labeled=False):
    # service = get_service_type_by_appointment_id(appointment.id)

    if service_code == c.SERVICE_CODE_COVID19_TEST or service_code == c.SERVICE_CODE_COVID19_TEST_ANTIGEN:
        switcher = {
            c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
            c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_TEST,
            c.APPOINTMENT_STATUS_TEST_IN_PROGRESS: c.APPOINTMENT_ACTION_SCAN_VIAL,
            c.APPOINTMENT_STATUS_VIAL_SCANNED: c.APPOINTMENT_ACTION_END_TEST,
            c.APPOINTMENT_STATUS_TEST_COMPLETED: c.APPOINTMENT_ACTION_NONE
        }

        if not pre_labeled:  # vial scanning not required
            switcher = {
                c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
                c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_TEST,
                c.APPOINTMENT_STATUS_TEST_IN_PROGRESS: c.APPOINTMENT_ACTION_END_TEST,
                c.APPOINTMENT_STATUS_TEST_COMPLETED: c.APPOINTMENT_ACTION_NONE
            }
    elif service_code == c.SERVICE_CODE_COVID19_TEST_MEXICO or \
            service_code == c.SERVICE_CODE_COVID19_TEST_MEXICO_ANTIGEN:
        switcher = {
            c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
            c.APPOINTMENT_ACTION_CHECK_IN: c.APPOINTMENT_ACTION_NONE
        }
    elif service_code == c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_1 or \
            service_code == c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_2 or \
            service_code == c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_1 or \
            service_code == c.SERVICE_CODE_COVID_19_VACCINE_JNJ or \
            service_code == c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_2:

        if __has_insurance_info(appointment.id):
            switcher = {
                c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
                c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_VERIFY_INSURANCE,
                c.APPOINTMENT_ACTION_VERIFY_INSURANCE: c.APPOINTMENT_ACTION_START_VAX,
                c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
                # c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_SCAN_VIAL_VAX,
                # c.APPOINTMENT_ACTION_SCAN_VIAL_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
                c.APPOINTMENT_ACTION_NOTES_VAX: c.APPOINTMENT_ACTION_END_VAX
            }
        else:
            switcher = {
                c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
                c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_VAX,
                c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
                # c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_SCAN_VIAL_VAX,
                # c.APPOINTMENT_ACTION_SCAN_VIAL_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
                c.APPOINTMENT_ACTION_NOTES_VAX: c.APPOINTMENT_ACTION_END_VAX
            }

    return switcher.get(appointment.status, c.APPOINTMENT_ACTION_NONE)


# TODO: [GGT-80] Move copy to CMS
def __send_test_complete_sms(appointment):
    message = "" \
              "Hi {}, thank you for getting tested with GoGetTested.com. Your COVID-19 test results will be available in 48-96hours. " \
              "If you have any questions, please visit GoGetTested.com Reply STOP to cancel msgs".format(
        appointment.patient.first_name)

    log_generic(
        type="info",
        first_name=appointment.patient.first_name,
        message=message,
        function='__send_test_complete_sms'
    )
    international = is_international(appointment.patient.phone_number)
    return send_sms(appointment.patient.phone_number, message, international=international)


def __appointment_begin_test(user, appointment, workstation_id=1, operator_location_id=None):
    update_appointment_with_test_start(user, appointment, workstation_id, operator_location_id=operator_location_id)

    if __is_pre_labeled(appointment, workstation_id):
        return True

    return __send_label_to_printer(appointment.id, workstation_id)


def __appointment_reprint_label(user, appointment, workstation_id=1):
    return __send_label_to_printer(appointment.id, workstation_id)


# TODO: [GGT-86] Refactor, decouple integration code
def __send_label_to_printer(appointment_id, queue_id):
    try:
        appointment: GgtAppointment = get_appointment(appointment_id)
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
            MessageBody=(ujson.dumps(payload))
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


def __send_vax_completion_sms(name, to_number):
    msg = """Hi {} \nYour 15 minute observation period has begun.  Please alert the staff immediately if you feel 
    unwell.  If you are not near staff  call 911""".format(name)
    r = {
        "message": msg,
        "to_number": to_number
    }
    r = ujson.dumps(r)
    push_sqs_message(get_config_val('aws.vax_sms_que'), r, delay_seconds=0)


def __send_vax_completion_confirmation_in_15_minutes(name, to_number):
    msg = """Hi {} \nYou are free to leave if you feel well. 
    Please alert the staff immediately if you feel unwell or call 911 if you're not near staff. Your vaccine record is 
    located here https://start.gogetvax.com/provider. \nRemember to still practice social distancing and to continue 
    wearing a mask.""".format(name)
    r = {
        "message": msg,
        "to_number": to_number
    }
    r = ujson.dumps(r)
    push_sqs_message(get_config_val('aws.vax_sms_que'), r, delay_seconds=900)
