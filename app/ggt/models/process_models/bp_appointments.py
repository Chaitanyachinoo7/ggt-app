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
def bp_get_appointment_info(appointment_id, dob):
    try:
        appointment: GgtAppointment = get_appointment(appointment_id)
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


def bp_appointment_update(provider_update_appointment_request, user):
    usuccess = False
    appointment_id = provider_update_appointment_request.appointment_id
    action = provider_update_appointment_request.action
    workstation_id = provider_update_appointment_request.workstation_id
    try:
        appointment: GgtAppointment = get_appointment(appointment_id)

        if action == c.APPOINTMENT_ACTION_START_VAX:
            usuccess = update_appointment_with_start_vax(appointment, user, workstation_id)

        if action == c.APPOINTMENT_ACTION_VERIFY_INSURANCE:
            usuccess = update_appointment_with_verify_insurance(appointment, user)
            if usuccess:
                __save_insurance_image(appointment_id, provider_update_appointment_request.insurance_photo)

        if action == c.APPOINTMENT_ACTION_END_VAX:
            usuccess = update_appointment_with_end_vax(appointment, user, workstation_id)
            if usuccess:
                __send_vax_completion_sms(appointment.patient.first_name, appointment.patient.phone_number)
                __send_vax_completion_confirmation_in_15_minutes(appointment.patient.first_name,
                                                                 appointment.patient.phone_number)

        if action == c.APPOINTMENT_ACTION_NOTES_VAX:
            usuccess = update_appointment_with_notes_vax(appointment, user, workstation_id,
                                                         provider_update_appointment_request.injection_site,
                                                         provider_update_appointment_request.no_adverse_reactions)
            if usuccess:
                create_consultation_note(user, appointment_id, provider_update_appointment_request.appointment_notes)

        if action == c.APPOINTMENT_ACTION_CHECK_IN:
            usuccess = update_appointment_with_checkin(appointment, user)

        elif action == c.APPOINTMENT_ACTION_START_TEST:
            usuccess = __appointment_begin_test(user, appointment, workstation_id)

        elif action == c.APPOINTMENT_ACTION_SCAN_VIAL:
            usuccess, reason_code = update_appointment_with_scan_vial(appointment, provider_update_appointment_request.vial_data.vial_id, user)
            if not usuccess:
                return {
                    c.STATUS: c.FAILED,
                    c.REASON_CODE: reason_code
                }

        elif action == c.APPOINTMENT_ACTION_SCAN_VIAL_VAX:
            usuccess, reason_code = update_appointment_with_scan_vial_vax(appointment, provider_update_appointment_request.vial_data,
                                                             user)
            if not usuccess:
                return {
                    c.STATUS: c.FAILED,
                    c.REASON_CODE: reason_code
                }

        elif action == c.APPOINTMENT_ACTION_END_TEST:
            usuccess = update_appointment_with_test_completed(appointment, user)
            if usuccess:
                __send_test_complete_sms(appointment)

        elif action == c.APPOINTMENT_ACTION_REPRINT:
            usuccess = __appointment_reprint_label(user, appointment, workstation_id)

        # TODO: This allows the start_test to be invoked twice (print the label twice). And every other action only to be invoked once.
        # essentially works by waiting to catch the appointment status update in the next round
        # Ideally, this should be handled at the printer label processor
        if usuccess and (action != c.APPOINTMENT_ACTION_START_TEST or __is_pre_labeled(appointment, workstation_id)):
            appointment: GgtAppointment = get_appointment(appointment_id)

        if usuccess:
            return {
                'appointment_id': appointment.id,
                'next_action': __next_action(appointment, __is_pre_labeled(appointment, workstation_id))
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
    return True if (appointment.location.test_type_offered == 'oral_fluid' or workstation_id > 10000) else False


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
    service = get_service_type_by_appointment_id(appointment.id)

    if service and service['appointment_type'] == "test":
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
    elif service and service['appointment_type'] == "vax":

        if __has_insurance_info(appointment.patient.id):
            switcher = {
                c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
                c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_VERIFY_INSURANCE,
                c.APPOINTMENT_ACTION_VERIFY_INSURANCE: c.APPOINTMENT_ACTION_START_VAX,
                c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_SCAN_VIAL_VAX,
                c.APPOINTMENT_ACTION_SCAN_VIAL_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
                c.APPOINTMENT_ACTION_NOTES_VAX: c.APPOINTMENT_ACTION_END_VAX
            }
        else:
            switcher = {
                c.APPOINTMENT_STATUS_SCHEDULED: c.APPOINTMENT_ACTION_CHECK_IN,
                c.APPOINTMENT_STATUS_CHECKED_IN: c.APPOINTMENT_ACTION_START_VAX,
                c.APPOINTMENT_ACTION_START_VAX: c.APPOINTMENT_ACTION_SCAN_VIAL_VAX,
                c.APPOINTMENT_ACTION_SCAN_VIAL_VAX: c.APPOINTMENT_ACTION_NOTES_VAX,
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
    return send_sms(appointment.patient.phone_number, message)


def __appointment_begin_test(user, appointment, workstation_id=1):
    update_appointment_with_test_start(user, appointment, workstation_id)

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

    # send_twilio_sms(to_number, msg)


def __send_vax_completion_confirmation_in_15_minutes(name, to_number):
    msg = """Hi {} \nThank you for getting your vaccine with GoGetVax.com.  Please alert the staff immediately if you 
    currently feel unwell .  If you are not near staff, call 911.  Your Vaccine record is located here 
    https://start.gogettested.com/provider.  Remember to still practice social distancing and continue to wear a mask.""".format(
        name)

    r = {
        "message": msg,
        "to_number": to_number
    }

    r = ujson.dumps(r)
    push_sqs_message(get_config_val('aws.vax_sms_que'), r, delay_seconds=900)
