import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
from cachetools import cached, LRUCache, TTLCache
import ggt.lib.constants as c
import datetime

from ggt.lib.utils import (
    get_config_val as cfg,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic,
    whoami
)

from ggt.lib.sms import (send_sms)

from ggt.lib.email import (
    render_template,
    render_from_string,
    send_email
)

from ggt.models.data_models.signups import (
    get_group_info,
    create_pending_signup_record,
    get_signup_record_by_phone_otp,
    get_signup_record_by_token
)

from ggt.models.data_models.patients import (
    create_patient_record,
    get_patient_by_token, add_to_ggd_waiting_queue, create_pre_registration,
    get_existing_patients, unlock_patient_info_patients, get_existing_patient_questionnaire, is_un_available_slot,
    create_patient_insurance_record, get_insurance_record_by_id, get_patient_upfront_payment
)

from ggt.models.data_models.questionnaires import (
    create_patient_questionnaire
)

from ggt.models.data_models.appointments import (
    get_appointment,
    get_appointment_count_by_phone_dob,
    create_appointment,
    update_appointment_with_confirmed_scheduled,
    update_appointment_with_receipt_token, release_ggv_slot, lock_ggv_slot, re_schedule_appointment
)

from ggt.models.data_models.locations import (
    get_location_by_id
)

from ggt.models.data_models.schedules import (
    get_slot_information,
    update_slot_information
)

from ggt.models.data_models.clinical_test_results import (
    get_test_result_by_token
)

from ggt.models.data_models.wellpay import (
    WellpayCreateBillRequest,
    WellpayCreateBillResponse,
    WellpayApiCredentials
)

from ggt.models.data_models.data_types import (
    GgtPatient,
    GgtBooking,
    GgtAppointment,
    GgtThirdPartyGroup,
    GgtCustomField,
    PaymentRequestBody,
    PaymentRequestLineItem,
    PaymentRequestNavigation,
    PatientUpfrontPayment
)

from ggt.lib.storage import (
    file_exists_in_insurance_cards,
    upload_insurance_card_from_base64_string
)

from ggt.lib.storage import get_temporary_lab_report_url

from ggt.models.process_models.bp_payment import bp_create_checkout_session
########################################################################################################
# [Public] functions
########################################################################################################
from main import app


def bp_get_ggv_screen_flow_seq(group_code: str):
    group_info: GgtThirdPartyGroup = get_group_info(group_code)

    validations = {}
    screens = []
    config = {}

    if group_info.ggv_screen_seq:
        screens = group_info.ggv_screen_seq
        for screen in screens:
            req = False
            if group_info.ggv_required_screens:
                req = True if (
                    screen in group_info.ggv_required_screens) else False

            validations[screen] = {
                "required": req
            }

    # TODO: Move hardcoded provider name and intro_text to DB, remove OR True
    if group_info.display_group_consent or True:
        config = {
            "consent-provider": {
                "content": {
                    "logo": [group_info.logo_1, group_info.logo_2],
                    "intro_text": "I understand that, by granting the consent below, I am authorizing retention of my (or my child's) disaster-related information by DSHS beyond the 5 year retention period. I further understand that DSHS will include this information in the state's central immunization registry (ImmTrac2). Once in ImmTrac2, my (or my child's) disaster-related information may by law be accessed by: a state agency, for the purpose of aiding and coordinating communicable disease prevention and control efforts, and / or; a physician or other health-care provider legally authorized to administer immunizations, antivirals, and other medications, for treating the client as a patient; I understand that I may withdraw this consent to retain information in the ImmTrac2 Registry beyond the 5 year retention period and my consent to release information from the Registry, at any time by written communication to the Texas Department of State Health Services, ImmTrac2 Group – MC 1946, P. O. Box 149347, Austin, Texas 78714-9347. By my signature below, I GRANT consent to retain my disaster-related information (or my child's information if younger than age 18) in the Texas Immunization registry beyond the 5 year retention period.",
                    # "intro_text": group_info.intro_text,
                    "provider_name": "Texas Immtrac2",
                    # "provider_name": group_info.consent_party_name,
                    "consent_url": group_info.consent_url if (group_info.consent_url and group_info.consent_url != '') else None,
                    "additional_fields": group_info.additional_fields
                }
            }
        }

    return {
        "screens": screens,
        "validation": validations,
        "config": config
    }


def bp_get_screen_flow_seq(group_code: str):
    group_info: GgtThirdPartyGroup = get_group_info(group_code)

    validations = {}
    screens = []
    config = {}

    if group_info.screen_seq:
        screens = group_info.screen_seq
        for screen in screens:
            req = False
            if group_info.required_screens:
                req = True if (
                    screen in group_info.required_screens) else False

            validations[screen] = {
                "required": req
            }

    if group_info.display_group_consent:
        config = {
            "consent-provider": {
                "content": {
                    "logo": [group_info.logo_1, group_info.logo_2],
                    "intro_text": group_info.intro_text,
                    "provider_name": group_info.consent_party_name,
                    "consent_url": group_info.consent_url if (group_info.consent_url and group_info.consent_url != '') else None,
                    "additional_fields": group_info.additional_fields
                }
            }
        }

    return {
        "screens": screens,
        "validation": validations,
        "config": config
    }


def bp_initiate_verification_flow(phone_number: str, with_otp: bool = True):
    # Create a temp record until phone number is validated
    try:
        phone_number = validate_phone_number_format(phone_number)
        existing_patient = get_existing_patients(phone_number)
        token = None
        if existing_patient:
            token = existing_patient['token']
        otp_code, token = __create_pending_entry(phone_number, token)
        print(otp_code)
        if otp_code is None:
            raise ValueError(
                'NO OTP / Cannot create Pending Phone Verification record')

        else:
            # activation_url = "{}/{}/{}".format(
            #     cfg('base_url'), phone_number, token)

            if with_otp:
                # message = "Enter Code: {}\nOr click {} \nReply STOP to cancel msgs".format(
                #     otp_code, activation_url)
                message = "Your GoGet verification code is: {} \nReply STOP to cancel msgs".format(
                    otp_code)
            else:
                return True

            # send SMS
            if __send_otp_sms(phone_number, message):
                log_generic(
                    type=c.INFO,
                    phone_number=phone_number,
                    otp_code=otp_code,
                    token=token,
                    # activation_url=activation_url,
                    sms_message=message,
                    function=whoami(),
                    info='OTP SMS Sent'
                )
                return True

            else:
                raise ValueError('Unable to send OTP SMS')

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
    return False


def bp_validate_phone_number(phone_number: str, otp: str):
    try:
        # Override OTP under special circumstances
        override_otp_code = cfg('pfe.signup.override_otp_code')
        patient = None
        result_token = None
        if otp == override_otp_code:
            token = "NOVERIFY{}".format(generate_token()[8:])
        else:
            token = get_signup_record_by_phone_otp(phone_number, otp)
            patient = get_existing_patients(phone_number)

        if token is None:
            raise ValueError('Invalid Token')

        if patient:
            '''Unlock patient record for 5 minutes.'''
            result_token = unlock_patient_info_patients(phone_number)

        log_generic(
            type=c.INFO,
            phone_number=phone_number,
            otp=otp,
            token=token,
            function=whoami()
        )

        return {
            "token": token,
            "session_token": result_token
        }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            otp=otp,
            function=whoami(),
            error=err
        )

    return False


def bp_add_to_ggd_waiting_queue(patient_id):
    try:
        return add_to_ggd_waiting_queue(patient_id)
        log_generic(
            type=c.INFO,
            patient_id=patient_id,
            function=whoami()
        )
    except Exception as err:
        log_generic(
            type=c.ERROR,
            patient_id=patient_id,
            function=whoami(),
            error=err
        )

    return False


def bp_create_pre_registration(patient_id):
    try:
        return create_pre_registration(patient_id)
        log_generic(
            type=c.INFO,
            patient_id=patient_id,
            function=whoami()
        )
    except Exception as err:
        log_generic(
            type=c.ERROR,
            patient_id=patient_id,
            function=whoami(),
            error=err
        )

    return False


def bp_finalize_booking(booking_req: GgtBooking):
    appointment: GgtAppointment = None
    status_message = None
    try:
        booking_req, status_message = __create_patient_and_questionnaire(booking_req)
        if booking_req is None:
            raise ValueError(status_message)
        patient_id = booking_req.patient_id
        # determine if payment is required, if so, get billing info
        upfront_payment_info = __evaluate_upfront_payment(booking_req)
        booking_req.total_cost = upfront_payment_info.total_cost
        booking_req.billed_amount = upfront_payment_info.billed_amount

        # generate appointment/booking
        appointment = __generate_appointment(booking_req)
        if not appointment:
            raise ValueError('Invalid Appointment info')

        # store insurance card
        if not __save_insurance_image(appointment.id, booking_req.insurance_photo):
            pass  # allow transaction to proceed. TODO: Handle alternative action

        # if a payment is required, generate a payment link
        appointment.payment_url = ''
        if upfront_payment_info.is_payment_required:
            # Below method is commented due to the use of an undefined method
            # appointment.payment_url = __inject_payment_flow(appointment)
            appointment.payment_checkout_session = __inject_payment_checkout_session(appointment, upfront_payment_info)
        else:
            # payment not required, confirm the appointment and notify
            update_appointment_with_confirmed_scheduled(appointment)
            __send_qrcode_sms(appointment)
            __send_qrcode_email(appointment)

    except Exception as err:
        status_message = str(err)
        log_generic(
            type=c.ERROR,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )
        raise HTTPException(status_code=500)

    return appointment, status_message, patient_id, booking_req.result_token


def bp_ggv_finalize_booking(booking_req: GgtBooking):
    try:
        booking_req, status_message = __create_patient_and_questionnaire(booking_req)
        if booking_req is None:
            raise ValueError(status_message)

        patient_id = booking_req.patient_id
        # determine if payment is required, if so, get billing info
        upfront_payment_info = __evaluate_upfront_payment(booking_req)
        booking_req.total_cost = upfront_payment_info.total_cost
        booking_req.billed_amount = upfront_payment_info.billed_amount

        # generate appointment/booking
        appointment_1, appointment_2 = __generate_ggv_appointments(booking_req)
        if not (appointment_1 and appointment_2):
            raise ValueError('Invalid Appointment info')
        #
        # # store insurance card
        if not __save_insurance_image(appointment_1.id, booking_req.insurance_photo):
            pass  # allow transaction to proceed. TODO: Handle alternative action
        #card
        if not __save_insurance_image(appointment_2.id, booking_req.insurance_photo):
            pass  # allow transaction to proceed. TODO: Handle alternative action

        # if a payment is required, generate a payment link
        appointment_1.payment_url = ''
        appointment_2.payment_url = ''
        if upfront_payment_info.is_payment_required:
            appointment_1.payment_url = __inject_payment_flow(appointment_1)
            appointment_1.payment_url = __inject_payment_flow(appointment_1)
        else:
            # payment not required, confirm the appointment and notify
            update_appointment_with_confirmed_scheduled(appointment_1)
            update_appointment_with_confirmed_scheduled(appointment_2)
            __send_ggv_qrcode_sms(appointment_1, "1")
            __send_ggv_qrcode_email(appointment_1)
            __send_ggv_qrcode_sms(appointment_2, "2")
            __send_ggv_qrcode_email(appointment_2)

    except Exception as err:
        status_message = str(err)
        log_generic(
            type=c.ERROR,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )
        raise HTTPException(status_code=500)

    return appointment_1, appointment_2, status_message, patient_id, booking_req.result_token


def bp_ggv_finalize_pre_booking(booking_req: GgtBooking):
    status_message = None
    try:
        booking_req, status_message = __create_patient_and_questionnaire(booking_req)
        if booking_req is None:
            raise ValueError(status_message)
        patient_id = booking_req.patient_id
        __send_ggv_pre_registration_sms(booking_req.first_name, booking_req.phone_number)
        __send_ggv_pre_registration_email(booking_req.first_name, booking_req.email)
    except Exception as err:
        status_message = str(err)
        log_generic(
            type=c.ERROR,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )
        raise HTTPException(status_code=500)

    return status_message, patient_id


def bp_finalize_payment(appointment_id: int, wp_receipt_token: str):
    try:
        appointment = get_appointment(appointment_id)
        if appointment.wp_receipt_token == wp_receipt_token:
            update_appointment_with_confirmed_scheduled(appointment_id)
            __send_qrcode_sms(appointment)
            __send_qrcode_email(appointment)
            return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            wp_receipt_token=wp_receipt_token,
            function=whoami(),
            error=err
        )

    return False


def bp_get_test_result(token: str, dob: str):
    try:
        lab_result = get_test_result_by_token(token)

        if lab_result:
            patient_dob_us = lab_result['dob'].strftime("%m%d%Y")
            patient_dob_iso = lab_result['dob'].strftime("%Y%m%d")
            test_result = lab_result['test_result']
            test_id = lab_result['test_id']

            if test_result == 'neg':
                result = 'Negative'
            elif test_result == 'pos':
                result = 'Positive'
            else:
                result = 'Unknown'

            try:
                url = get_temporary_lab_report_url('{}.pdf'.format(test_id))
            except Exception as err:
                url = ''

            if url is None:
                url = ''

            if dob == patient_dob_us or dob == patient_dob_iso:
                return {
                    "result": result,
                    "lab_report_url": url
                }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            token=token,
            function=whoami(),
            error=err
        )

    return False


def bp_has_appointments(phone_number: str, dob: str) -> bool:
    try:
        if get_appointment_count_by_phone_dob(phone_number, dob) > 0:
            log_generic(
                type=c.INFO,
                phone_number=phone_number,
                dob=dob,
                function=whoami()
            )
            return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            dob=dob,
            function=whoami(),
            error=err
        )

    return False


def bp_reschedule_first_appointment(otp, appointment_id_1, appointment_id_2, appointment_1_dt_id, appointment_2_dt_id, phone_number):
    try:
        if __validate_otp(phone_number, otp):
            release_ggv_slot(appointment_id_1)
            release_ggv_slot(appointment_id_2)
            slot_1 = get_slot_information(appointment_1_dt_id, slot_type='vax')
            slot_2 = get_slot_information(appointment_2_dt_id, slot_type='vax')
            lock_ggv_slot(appointment_id_1, appointment_1_dt_id)
            lock_ggv_slot(appointment_id_2, appointment_2_dt_id)
            appointment_1 = re_schedule_appointment(appointment_id_1, slot_1)
            appointment_2 = re_schedule_appointment(appointment_id_2, slot_2)
            __send_ggv_qrcode_sms(appointment_1, "1")
            __send_ggv_qrcode_email(appointment_1)
            __send_ggv_qrcode_sms(appointment_2, "2")
            __send_ggv_qrcode_email(appointment_2)
            return True
        else:
            log_generic(
                type=c.INFO,
                phone_number=phone_number,
                otp=otp,
                message="Invalid OTP",
                function=whoami()
            )
            return False

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return False


@cached(cache=TTLCache(maxsize=1024, ttl=14.5))
def bp_get_wellpay_api_key():
    return __get_wp_api_tokens()


def bp_get_wellpay_insurance_eligibility(insurance_eligibility_request):
    return __bp_get_wellpay_insurance_eligibility(insurance_eligibility_request)


def bp_search_insurance_payer_list(insurance_search_payer_request):
    return __bp_search_insurance_payer_list(insurance_search_payer_request)


def bp_verify_verification_token(token):
    if is_un_available_slot(token) is None:
        return True
    else:
        return False
########################################################################################################
# [Protected] functions
########################################################################################################

# TODO: Prevent from looking up slots that are already assigned to an appointment
# TODO, doesn't check if it's already booked
# TEMP, not using fixed slots since operational conditions allow oversubscribing


def __validate_otp(phone_number, otp):
    return get_signup_record_by_phone_otp(phone_number, otp)


def __generate_appointment(booking_req: GgtBooking):
    appointment: GgtAppointment = None
    try:
        booking_req.timeslot = get_slot_information(booking_req.timeslot_id)
        if not booking_req.timeslot:
            raise ValueError('Invalid Slot')

        appointment = create_appointment(booking_req)

        if appointment:
            update_slot_information(booking_req.timeslot_id, appointment.id)

            '''
            log_generic(
                type=c.INFO,
                booking_req=booking_req,
                appointment=appointment,
                function=whoami(),
                info='appointment_created'
            )
            '''

        else:
            raise ValueError('error_creating_appointment')

    except Exception as err:
        log_generic(
            type=c.ERROR,
            data=booking_req,
            function=whoami(),
            error=err
        )

    return appointment


def __generate_ggv_appointments(booking_req: GgtBooking):
    appointment_1: GgtAppointment = None
    appointment_2: GgtAppointment = None
    try:
        booking_req.slot_1 = get_slot_information(booking_req.appointmentOneTime, slot_type='vax')
        booking_req.slot_2 = get_slot_information(booking_req.appointmentTwoTime, slot_type='vax')
        if not (booking_req.slot_1 and booking_req.slot_2):
            raise ValueError('Invalid Slot')

        booking_req.timeslot = booking_req.slot_1
        appointment_1 = create_appointment(booking_req, ggv_slot=1)

        booking_req.timeslot = booking_req.slot_2
        appointment_2 = create_appointment(booking_req, ggv_slot=2)

        if appointment_1 and appointment_2:
            update_slot_information(booking_req.appointmentOneTime, appointment_1.id, slot_type='vax')
            update_slot_information(booking_req.appointmentTwoTime, appointment_2.id, slot_type='vax')

            '''
            log_generic(
                type=c.INFO,
                booking_req=booking_req,
                appointment=appointment,
                function=whoami(),
                info='appointment_created'
            )
            '''

        else:
            raise ValueError('error_creating_appointment')

    except Exception as err:
        log_generic(
            type=c.ERROR,
            data=booking_req,
            function=whoami(),
            error=err
        )

    return appointment_1, appointment_2


def __create_pending_entry(phone_number: str, token):
    try:
        override, otp_code = __override_random_otp(phone_number)

        if not override:
            otp_code = generate_otp()

        if token is None:
            token = generate_token()

        log_generic(
            type=c.INFO,
            phone_number=phone_number,
            otp_code=otp_code,
            token=token,
            function=whoami())

        record_id = create_pending_signup_record(
            phone_number,
            otp_code,
            token
        )
        if record_id > 0:
            return otp_code, token
        else:
            return None, None

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
        return None, None


def __send_qrcode_sms(appointment: GgtAppointment):
    try:
        message = "" \
            "Hi {}, thank you for completing your registration at GoGetTested.com " \
            "Your appointment is confirmed for {} at {}. Details at {}/appointment/{}/{} " \
            "\nReply STOP to cancel msgs".format(
                appointment.patient.first_name,
                appointment.date_text,
                appointment.location_text,
                cfg('base_url'),
                appointment.id,
                appointment.patient.dob.strftime('%Y%m%d')
            )
        result_1 = send_sms(appointment.patient.phone_number,
                            message.replace('\t', ''))

        followup_message = "" \
            "Please arrive 15 minutes prior to your appointment. Bring this QR code, and an Acceptable ID when you arrive at the test. " \
            "We will scan the QR code to check you in for testing. Please, no eating or drinking at least 15 minutes prior to testing as this may impact your test results."
        result_2 = send_sms(appointment.patient.phone_number, followup_message)

        log_generic(
            type=c.INFO,
            appointment=appointment,
            phone_number=appointment.patient.phone_number,
            message=message,
            function=whoami()
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return None


def __send_ggv_qrcode_sms(appointment: GgtAppointment, dose):
    try:
        message = "Hi {} " \
                  "\nYour COVID-19 Vaccine Dose {} of 2 appointment is confirmed for {} at {}." \
                  " Details at {}/appointment/{}/{}.  " \
                  "Please arrive at the vaccine location 15 minutes early. Also make sure to bring an Acceptable ID, " \
                  "and QR code. Though not required, please bring your health insurance card as well." \
                  "\nReply Stop to cxl msgs".format(
                appointment.patient.first_name,
                dose,
                appointment.date_text,
                appointment.location_text,
                "https://start.gogetvax.com",
                appointment.id,
                appointment.patient.dob.strftime('%Y%m%d')
            )
        send_sms(appointment.patient.phone_number,
                            message.replace('\t', ''))

        log_generic(
            type=c.INFO,
            appointment=appointment,
            phone_number=appointment.patient.phone_number,
            message=message,
            function=whoami()
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return None


def __send_ggv_pre_registration_sms(first_name, phone_number):
    try:
        message = "Hi {} " \
                  "\nYou have successfully joined the waitlist for the COVID-19 vaccine.  " \
                  "We will notify you once  you have been cleared to book an appointment." \
                  "\nReply Stop to cxl msgs".format(first_name)
        send_sms(phone_number,
                            message.replace('\t', ''))

        log_generic(
            type=c.INFO,
            first_name=first_name,
            phone_number=phone_number,
            message=message,
            function=whoami()
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return None


def __send_qrcode_email(appointment: GgtAppointment):
    try:
        from_email = cfg('notifications.from_email')
        from_name = cfg('notifications.from_name')

        template_vars = {
            "first_name": appointment.patient.first_name,
            "date_text": appointment.date_text,
            "location_text": appointment.location_text,
            "base_url": cfg('base_url'),
            "appointment_id": appointment.id,
            "dob": appointment.patient.dob.strftime('%Y%m%d'),
            "appointment_url": '{}/appointment/{}/{}'.format(
                cfg('base_url'),
                appointment.id,
                appointment.patient.dob.strftime('%Y%m%d')
            )
        }

        subject = render_from_string(
            cfg('notifications.confirmation_subject'),
            **template_vars
        )

        template_name = cfg('notifications.confirmation_template')
        html_content = render_template(
            template_name,
            **template_vars
        )

        send_email(
            from_email,
            from_name,
            appointment.patient.email,
            subject,
            html_content
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return False


def __send_ggv_qrcode_email(appointment: GgtAppointment):
    try:
        from_email = cfg('notifications.from_email')
        from_name = cfg('notifications.from_name')

        template_vars = {
            "first_name": appointment.patient.first_name,
            "date_text": appointment.date_text,
            "location_text": appointment.location_text,
            "base_url": "https://start.gogetvax.com",
            "appointment_id": appointment.id,
            "dob": appointment.patient.dob.strftime('%Y%m%d'),
            "appointment_url": '{}/appointment/{}/{}'.format(
                "https://start.gogetvax.com",
                appointment.id,
                appointment.patient.dob.strftime('%Y%m%d')
            )
        }

        subject = render_from_string(
            cfg('notifications.confirmation_subject_ggv'),
            **template_vars
        )

        template_name = cfg('notifications.confirmation_template_ggv')
        html_content = render_template(
            template_name,
            **template_vars
        )

        send_email(
            from_email,
            from_name,
            appointment.patient.email,
            subject,
            html_content
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return False


def __send_ggv_pre_registration_email(first_name, email):
    try:
        from_email = cfg('notifications.from_email')
        from_name = cfg('notifications.from_name')

        template_vars = {
            "first_name": first_name,
        }

        subject = render_from_string(
            "COVID-19 Vaccine pre registration confirmation",
            **template_vars
        )

        template_name = "GGV-4-PRE_REGISTRATION_REQUEST-EMAIL.html"
        html_content = render_template(
            template_name,
            **template_vars
        )

        send_email(
            from_email,
            from_name,
            email,
            subject,
            html_content
        )

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            first_name=first_name,
            email=email,
            function=whoami(),
            error=err
        )

    return False


def __send_otp_sms(phone_number: str, message: str) -> bool:
    try:
        log_generic(
            type=c.INFO,
            phone_number=phone_number,
            message=message,
            function=whoami()
        )
        return send_sms(phone_number, message, 1)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            message=message,
            function=whoami(),
            error=err
        )

    return False


def __override_random_otp(phone_number: str):
    try:
        p1 = cfg('pfe.signup.special_phone_1')
        p2 = cfg('pfe.signup.special_phone_2')
        override_otp_code = cfg('pfe.signup.override_otp_code')

        if phone_number == p1 or phone_number == p2:
            return True, override_otp_code

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return False, None


def __is_valid_token(token: str) -> bool:
    try:
        # Allows overriding phone number validation
        if token.startswith("NOVERIFY"):
            # Check Duplicate Token
            if get_patient_by_token(token, expect_no_match=True):
                print('Duplicate Token: {}', token)
                return False
            else:
                return True
        else:
            # return True
            return get_signup_record_by_token(token)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            token=token,
            function=whoami(),
            error=err
        )

    return False


def __extract_patient_from_booking_req(booking_req: GgtBooking) -> GgtPatient:
    try:
        patient: GgtPatient = GgtPatient()
        patient.token = booking_req.token
        patient.phone_number = validate_phone_number_format(
            booking_req.phone_number)
        patient.first_name = booking_req.first_name
        patient.middle_name = booking_req.middle_name
        patient.last_name = booking_req.last_name
        patient.gender = booking_req.gender
        patient.phone_number_verified = True
        patient.addr1 = booking_req.address
        patient.city = booking_req.city
        patient.zip = booking_req.zip
        patient.email = booking_req.email
        patient.dob = booking_req.dob
        patient.height_ft = booking_req.height
        patient.weight_lb = booking_req.weight
        patient.ethnicity = booking_req.ethnicity
        patient.race = booking_req.race
        patient.st = booking_req.st
        return patient

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            booking_req=booking_req,
            error=err
        )

    return None


@cached(cache=TTLCache(maxsize=1024, ttl=14.5))
def __get_wp_api_tokens():
    base_url = cfg('vendors.wellpay.endpoint')
    auth_user = cfg('vendors.wellpay.auth_user')
    auth_password = cfg('vendors.wellpay.auth_password')

    wp_api_key = None
    wp_refresh_token = None

    try:
        url = "{}/gen_token".format(base_url)
        auth = HTTPBasicAuth(auth_user, auth_password)
        payload = {}
        headers = {}
        r = requests.post(url, auth=auth, headers=headers, data=payload)
        response = r.json()

        wp_api_key = response['api_key']
        wp_refresh_token = response['refresh_token']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return wp_api_key, wp_refresh_token


class UpfrontPaymemtResponse():
    is_payment_required: bool = None
    total_cost: int = None
    billed_amount: int = None


def __save_insurance_image(appointment_id: int, insurance_image: str) -> bool:
    try:
        if insurance_image and len(insurance_image) > 0:
            if "," in insurance_image:
                base64string = insurance_image.split(",")[1]

            dest_file_name = '{}.png'.format(appointment_id)
            if upload_insurance_card_from_base64_string(base64string, 'image/png', dest_file_name):
                print('uploaded image: {}'.format(dest_file_name))
                return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            insurance_image=insurance_image,
            function=whoami(),
            error=err
        )

    return False


def __inject_payment_flow(appointment: GgtAppointment):
    try:
        wp_bill = te_wp_bill(appointment)

        appointment.wp_receipt_token = wp_bill.receipt_token
        appointment.wp_customer_info_id = wp_bill.customer_id
        appointment.payment_url = wp_bill.url

        if update_appointment_with_receipt_token(appointment):
            return wp_bill.url

        else:
            raise ValueError('Appointment update failed')

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return None


# This util method will contain business logic to decide whether a patient needs
# to do an upfront payment
def __should_charge_upfront_payment(upfront_payment_info: PatientUpfrontPayment):
    return upfront_payment_info.is_payment_required


# Returns payment_required, total_cost, billed_amount
def  __evaluate_upfront_payment(booking_req: GgtBooking):
    try:
        patient_upfront_payment = PatientUpfrontPayment()
        # Set initial value to false
        patient_upfront_payment.is_payment_required = False
        patient_upfront_payment.total_cost = 0
        patient_upfront_payment.billed_amount = 0

        # Get the list of location services
        location_services = booking_req.location_services
        # If no location services, return the empty payment object
        if not location_services:
            return patient_upfront_payment

        services_list = []
        # Get the list of service codes
        for service in location_services:
            services_list.append(service.service_code)

        # Get list of upfront payments
        service_payments = get_patient_upfront_payment(services_list)

        if not service_payments:
            return patient_upfront_payment

        # Get the total patient payment sum
        total = 0
        for payment in service_payments:
            total += payment.selfpay_amount

        # Here we consider all the service charges into one bill
        patient_upfront_payment.is_payment_required = total > 0
        patient_upfront_payment.billed_amount = total
        patient_upfront_payment.total_cost = total

    except Exception as err:
        log_generic(
            type=c.ERROR,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )

    return patient_upfront_payment


def __create_wp_bill(appointment: GgtAppointment):
    res: WellpayCreateBillResponse = WellpayCreateBillResponse()
    try:
        wp_api_key, wp_refresh_token = __get_wp_api_tokens()

        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/bill/submit".format(base_url)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }

        payload = {
            "first_name": appointment.patient.first_name,
            "last_name": appointment.patient.last_name,
            "phone": appointment.patient.phone_number,
            "email": appointment.patient.email,
            "date_of_birth": appointment.patient.dob.strftime('%Y-%m-%d'),
            "street_address": appointment.patient.addr1,
            # "adddress_complement": ''+appointment.patient.addr2,
            "city": appointment.patient.city,
            "state": appointment.patient.st,
            "zip_code": appointment.patient.zip,
            "external_account_id": appointment.id,
            "autopay": False,
            "external_bill_id": appointment.id,
            "billed_amount": int(appointment.billed_amount*100),
            "service_date": appointment.scheduled_dt.strftime('%Y-%m-%d'),

            "onSuccess": "{}/appointment/{}/pay/success".format(cfg('base_url'), appointment.id),
            "onFailure": "{}/appointment/{}/pay/error".format(cfg('base_url'), appointment.id)
        }

        r = requests.post(url, headers=headers, json=payload)
        response = r.json()

        res.url = response['url']
        res.receipt_token = response['receipt_token']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return res


def __bp_get_wellpay_insurance_eligibility(insurance_eligibility_request):
    try:
        wp_api_key, wp_refresh_token = __get_wp_api_tokens()
        customer_id = __create_wellpay_customer(
            wp_api_key, insurance_eligibility_request)
        if(__add_wellpay_customer_insurance(
                wp_api_key, insurance_eligibility_request, customer_id)):
            eligibility = __add_wellpay_customer_insurance_eligibility(
                wp_api_key, insurance_eligibility_request, customer_id)
            if(eligibility['isEligible']):
                return __get_wellpay_customer_insurance_plans(
                    wp_api_key, insurance_eligibility_request, eligibility['eligibility_request_id'])
            return eligibility
        return {"isEligible": False}
    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment="appointment",
            function=whoami(),
            error=err
        )
        return {"isEligible": False}


def __create_wellpay_customer(wp_api_key, insurance_eligibility_request):
    try:
        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/bill/submit".format(base_url)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }

        payload = {
            "first_name": insurance_eligibility_request.first_name,
            "last_name": insurance_eligibility_request.last_name,
            "phone": insurance_eligibility_request.phone_number,
            "email": insurance_eligibility_request.email,
            "date_of_birth": insurance_eligibility_request.dob,
            "street_address": insurance_eligibility_request.addr1,
            "city": insurance_eligibility_request.city,
            "state": insurance_eligibility_request.state,
            "zip_code": insurance_eligibility_request.zip_code,
        }

        r = requests.post(url, headers=headers, json=payload)
        print(payload)
        response = r.json()
        print(response)
        return response['customer_id']
    except Exception as err:
        print(err)


def __add_wellpay_customer_insurance(wp_api_key, insurance_eligibility_request, customer_id):
    try:
        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/customers/{}/insurance".format(base_url, customer_id)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }
        print(url)
        payload = {
            "insurance_id_number": insurance_eligibility_request.insurance_id_number,
            "insurance_payer_id": insurance_eligibility_request.insurance_payer_id,
            "insurance_group_number": insurance_eligibility_request.insurance_group_number,
            "level": insurance_eligibility_request.level.lower(),
        }

        r = requests.post(url, headers=headers, json=payload)
        print(payload)
        response = r.json()
        print(response)
        return True
    except Exception as err:
        print(err)


def __add_wellpay_customer_insurance_eligibility(wp_api_key, insurance_eligibility_request, customer_id):
    try:
        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/customers/{}/eligibility".format(base_url, customer_id)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }
        print(url)
        print(datetime.datetime.today().strftime('%Y-%m-%d'))
        print(datetime.date.today() + datetime.timedelta(days=10))
        payload = {
            "services": [],
            "insurance_level": insurance_eligibility_request.level.lower(),
            "as_of_date": datetime.datetime.today().strftime('%Y-%m-%d'),
            "to_date": (datetime.date.today() + datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
            "place_of_service_code": "",
            "npi": cfg('vendors.wellpay.npi')
        }

        r = requests.post(url, headers=headers, json=payload)
        print(payload)
        print(headers)
        print(r.json())
        if(r.status_code == 200):
            return {"isEligible": True, "eligibility_request_id": r.json()['request_id'], "error": None}
        return {"isEligible": False, "error": r.text}
    except Exception as err:
        print(err)
        return {"isEligible": False, "error": None}


def __get_wellpay_customer_insurance_plans(wp_api_key, insurance_eligibility_request, eligibility_request_id):
    try:
        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/insurance/{}/plans".format(base_url, eligibility_request_id)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }
        print(url)
        payload = {}
        r = requests.get(url, headers=headers, json=payload)
        print(payload)
        if(r.status_code == 200):
            return {"isEligible": True, "benefits": r.json(), "error": None}
        elif(r.status_code == 404):
            return {"isEligible": False, "benefits": None, "error": "Benefits not found"}
        return {"isEligible": False, "error": r.text}
    except Exception as err:
        print(err)
        return {"isEligible": False, "error": None}


def __bp_search_insurance_payer_list(insurance_search_payer_request):
    try:
        wp_api_key, wp_refresh_token = __get_wp_api_tokens()
        base_url = cfg('vendors.wellpay.endpoint')
        url = "{}/eligibility/searchPayersList".format(base_url)
        headers = {
            'Authorization': 'Bearer {}'.format(wp_api_key),
            'Content-Type': 'application/json'
        }

        payload = {
            "searchQuery": insurance_search_payer_request.search_query,
            "page": insurance_search_payer_request.page,
            "limit": insurance_search_payer_request.limit
        }

        r = requests.post(url, headers=headers, json=payload)
        print(payload)
        response = r.json()
        print(response)
        return {"response": response}
    except Exception as err:
        print(err)


def __create_patient_and_questionnaire(booking_req):
    try:
        if not __is_valid_token(booking_req.token):
            raise ValueError('Invalid Token')

        # create patient
        _patient = __extract_patient_from_booking_req(booking_req)
        existing_patient = get_existing_patients(
            phone_number=_patient.phone_number,
            first_name=_patient.first_name,
            last_name=_patient.last_name,
            dob=_patient.dob
        )
        if existing_patient is None:
            p = get_existing_patients(token=_patient.token)
            if p:
                _patient.token = generate_token()
            patient_id = create_patient_record(_patient)
            booking_req.result_token = unlock_patient_info_patients(_patient.phone_number)
        else:
            patient_id = existing_patient['id']
            booking_req.result_token = unlock_patient_info_patients(existing_patient['phone_number'])
        booking_req.patient_id = patient_id

        if not booking_req.patient_id:
            raise ValueError('Invalid Patient ID')

        if not booking_req.result_token:
            raise ValueError('Invalid result_token')

        if not get_insurance_record_by_id(patient_id):
            create_patient_insurance_record(booking_req)
        # create questionnaire
        booking_req.patient_questionnaire_id = create_patient_questionnaire(
                booking_req)
        if not booking_req.patient_questionnaire_id:
            raise ValueError('Invalid Patient Questionnaire ID')
        return booking_req, None
    except Exception as err:
        status_message = str(err)
        log_generic(
            type=c.ERROR,
            status_message=status_message,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )
        return None, status_message


# This function will inject the checkout session in to the payment object
def __inject_payment_checkout_session(appointment: GgtAppointment, upfront_payment_info: PatientUpfrontPayment):
    if not __should_charge_upfront_payment(upfront_payment_info):
        raise ValueError('Checkout session is only be generated to upfront payments')

    payment_request = PaymentRequestBody()
    payment_request.line_items = __generate_payment_checkout_session_items(upfront_payment_info)
    payment_request.navigation = __generate_payment_checkout_session_navigation(appointment)

    # Return the session object which contains session id
    return bp_create_checkout_session(payment_request)


def __generate_payment_checkout_session_items(upfront_payment_info: PatientUpfrontPayment):
    line_item = PaymentRequestLineItem()

    line_item.product_name = 'Registration Charges'  # To be filled with correct name
    line_item.unit_price = upfront_payment_info.total_cost
    line_item.quantity = 1
    line_item.product_images = cfg('image_urls.payment')

    return [line_item]


def __generate_payment_checkout_session_navigation(appointment: GgtAppointment):
    navigation = PaymentRequestNavigation()
    navigation.success_url = cfg('payment.navigation.success_url').format(appointment.id, appointment.wp_receipt_token)
    navigation.cancel_url = cfg('payment.navigation.cancel_url')

    return navigation
