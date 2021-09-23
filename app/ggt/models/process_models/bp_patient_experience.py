import datetime
import json
import os
import uuid
from datetime import datetime, timedelta
import re
import boto3
import requests
import math
from cachetools import cached, TTLCache
from fastapi import HTTPException
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from requests.auth import HTTPBasicAuth
from starlette.responses import StreamingResponse
from wallet.models import Pass, Barcode, Generic
import httpx

import ggt.lib.constants as c
import ggt.models.process_models.jwt as jwt
from ggt.lib.adapters.s3_adapter import read_file, upload_file, get_temp_pkpass_url
from ggt.lib.adapters.twilio_adapter import place_twilio_otp
from ggt.lib.email import (
    render_template,
    render_from_string,
    send_email
)
from ggt.lib.sms import (send_sms)
from ggt.lib.storage import get_temporary_lab_report_url
from ggt.lib.storage import (
    upload_insurance_card_from_base64_string, upload_test_result_image_from_base64_string,
    upload_vax_card_image_from_base64_string,
    upload_vax_card_image_from_twilio
)
from ggt.lib.utils import (
    get_config_val as cfg,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic,
    whoami,
    get_translated_message, is_international
)
from ggt.models.data_models.appointments import (
    get_appointment,
    get_appointment_count_by_phone_dob,
    create_appointment,
    update_appointment_with_confirmed_scheduled,
    update_appointment_with_receipt_token, release_ggv_slot, lock_ggv_slot, re_schedule_appointment, lookup_certificate,
    lookup_pkpass, lookup_pkpass_for_portal, is_open_patient, update_appointment_with_payment_session, save_android_pass_details
)
from ggt.models.data_models.clinical_test_results import (
    get_test_result_by_token
)
from ggt.models.data_models.data_types import (
    GgtPatient,
    GgtBooking,
    GgtAppointment,
    GgtThirdPartyGroup,
    PaymentRequestBody,
    PaymentRequestLineItem,
    PaymentRequestNavigation,
    PatientUpfrontPayment
)
from ggt.models.data_models.data_types import LookupGGVAddVaxCertRequest
from ggt.models.data_models.patients import (
    create_patient_record, update_patient_record,
    get_patient_by_token, add_to_ggd_waiting_queue, create_pre_registration,
    get_existing_patients, unlock_patient_info_patients, is_un_available_slot,
    create_patient_insurance_record, get_insurance_record_by_id, get_patient_upfront_payment,
    get_verification_level_from_patient_id, save_apple_wallet_updates, get_serial_no,
    update_group_code_for_existing_patient,
    get_existing_vax_certificates, get_active_certificates, save_vax_yes_payment_info,
    update_certificates_to_active, update_vax_yes_payment_status, get_patient_by_id,
    get_existing_patient
)
from ggt.models.data_models.questionnaires import (
    create_patient_questionnaire
)
from ggt.models.data_models.schedules import (
    get_slot_information,
    update_slot_information, get_next_available_slot, book_slot, update_appointment, update_ocr, add_vax_yes_activity
)
from ggt.models.data_models.schedules import verify_certificate, get_patient_from_crt_number 
from ggt.models.data_models.signups import (
    get_group_info,
    create_pending_signup_record,
    get_signup_record_by_phone_otp,
    get_signup_record_by_token
)
from ggt.models.data_models.wellpay import (
    WellpayCreateBillResponse
)
from ggt.models.process_models.bp_payment import bp_create_checkout_session, bp_get_checkout_session
from ggt.lib.adapters.s3_adapter import read_file

# from google.cloud import vision
service_account_file = cfg('gcp.service_account_file')
# ios pkpass constants
pass_type_identifier = "pass.com.goget.vaccine"
organization_name = "GoGet, Inc."
team_identifier = "36PVVAHZQN"
cert_pem = "./app/ggt/configs/ios_certs/vaccine_wallet_crt.pem"
key_pem = "./app/ggt/configs/ios_certs/key.pem"
wwdr_pem = "./app/ggt/configs/ios_certs/WWDR.pem"
key_pem_password = "ggtvaccine"
ssl_key = "./app/ggt/configs/ios_certs/ssl.key"

########################################################################################################
# [Public] functions
########################################################################################################


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
                    "consent_url": group_info.consent_url if (
                        group_info.consent_url and group_info.consent_url != '') else None,
                    "additional_fields": group_info.additional_fields
                }
            }
        }

    return {
        "screens": screens,
        "validation": validations,
        "config": config
    }


def bp_get_screen_flow_seq(group_code: str, country_code="US"):
    group_info: GgtThirdPartyGroup = get_group_info(group_code)
    if group_info.screen_seq and group_info.screen_seq == ["groups#US:_DEFAULT_", "MX:_DEFAULT_MX_"]:
        if country_code == "US":
            default_group: GgtThirdPartyGroup = get_group_info("_DEFAULT_")
        if country_code == "MX":
            default_group: GgtThirdPartyGroup = get_group_info("_DEFAULT_MX_")
        else:
            default_group: GgtThirdPartyGroup = get_group_info("_DEFAULT_")

        group_info.screen_seq = default_group.screen_seq
        group_info.required_screens = default_group.required_screens

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
                    "consent_url": group_info.consent_url if (
                        group_info.consent_url and group_info.consent_url != '') else None,
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
        if not with_otp:
            return True
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
            if with_otp:
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


def bp_vax_check_payment(phone_number):
    # Check feature flag
    vax_yes_payment_feature_enabled = cfg('features.vax_yes_payment')
    if not vax_yes_payment_feature_enabled:
        return {
            "payment_required": False
        }

    phone_number = validate_phone_number_format(phone_number)
    # If the phone number is invalid return an error
    if phone_number == "":
        raise ValueError("Invalid phone number")
    # See if there are any certificates
    certificates = get_existing_vax_certificates(phone_number)
    # Payment is required if there are no certificates
    payment_required = len(certificates) == 0
    return {
        "payment_required": payment_required
    }


def bp_vax_yes_payment(req):
    phone_number = req.phone_number
    first_name = req.first_name
    last_name = req.last_name
    dob = req.dob
    amount = req.amount
    currency = req.currency

    patient = get_existing_patient(phone_number, first_name, last_name, dob)

    if not patient:
        return {
            "reason_code": "Patient is not available. Cannot proceed with the payment."
        }

    patient_id = patient['id']
    session_id = str(uuid.uuid4())

    # User has selected 0 as the amount
    if amount == 0:
        # Get the active certificate count for the user
        active_certificates = get_active_certificates(patient_id)
        # See if the count > 0
        active_certificates_available = len(active_certificates) > 0

        # If the active certificates are available, that means user can skip the payment
        # In that case send sms and emails
        if active_certificates_available:
            email = patient['email']
            send_ggv_certificate_level_1_sms(
                first_name.title(), phone_number, "1")
            send_ggv_certificate_level_1_email(
                first_name.title(), email, "1", phone_number=phone_number)
            return {
                "payment_checkout_session": None,
                "session_id": session_id
            }
        # If certificates are not available, payment cannot be skipped, therefore throw an error
        else:
            return {
                "reason_code": "Payment is required"
            }

    stripe_id = __generate_vax_payment_checkout_session(
        amount, currency, phone_number, session_id)

    save_payment_id = save_vax_yes_payment_info(
        patient_id, stripe_id, 'pending')

    # Saved in DB
    if save_payment_id:
        return {
            "payment_checkout_session": stripe_id,
            "session_id": session_id
        }

    return {
        "reason_code": "Error in saving in the database."
    }


def bp_vax_yes_verify_payment(session_id):
    session_info = bp_get_checkout_session(session_id, c.VAX_YES_PAYMENT_FLOW)
    # Check if the payment is done
    if session_info['payment_status'] == 'paid':
        update_vax_yes_payment_status('complete', session_id)
        # Get the updated patients id
        patient_id = update_certificates_to_active(session_id)
        if patient_id:
            patient = get_patient_by_id(patient_id)
            if not patient:
                return {
                    'error_code': 'Patient not available'
                }
            # If the patient is available send the email and phone
            first_name = patient['first_name']
            phone_number = patient['phone_number']
            email = patient['email']
            send_ggv_certificate_level_1_sms(
                first_name.title(), phone_number, "1")
            send_ggv_certificate_level_1_email(
                first_name.title(), email, "1", phone_number=phone_number)

            return {
                "payment_status": "complete"
            }

        return {
            "payment_status": "complete"
        }
    return {
        "reason_code": 'Payment is not complete.'
    }


def bp_initiate_vax_verification_flow(req):
    # Extract fields
    phone_number = req.phone_number
    has_sms = req.has_sms
    price = req.price
    currency = req.currency
    skip = req.skip  # Should the stripe flow needs to be skipped

    # Call the OTP flow
    bp_initiate_verification_flow(phone_number, has_sms)

    stripe_id = None
    session_id = str(uuid.uuid4())

    if not skip:
        certificates = get_existing_vax_certificates(phone_number)
        # If no certificates only we show the payment screen
        if len(certificates) == 0:
            # Generate stripe session
            stripe_id = __generate_vax_payment_checkout_session(
                price, currency, phone_number, session_id)

    return {
        "payment_checkout_session": stripe_id,
        "session_id": session_id
    }


def __generate_vax_payment_checkout_session(price, currency, phone_number, session_id):

    payment_request = PaymentRequestBody()
    payment_request.line_items = __generate_vax_payment_checkout_session_items(
        price)
    payment_request.navigation = __generate_vax_payment_checkout_session_navigations(
        phone_number, session_id)

    locale = "es" if currency == "mxn" else "en"

    payment_request.locale = __inject_locale(locale)

    payment_request.id = session_id
    payment_request.currency = currency

    return bp_create_checkout_session(payment_request, c.VAX_YES_PAYMENT_FLOW)


def __generate_vax_payment_checkout_session_items(price):

    line_items = []
    line_item = PaymentRequestLineItem()
    line_item.product_name = "Thank you for supporting VaxYes"
    line_item.product_description = "Your support goes to maintenance, improvements, and more from the GoGetDoc team"
    line_item.unit_price = price
    line_item.quantity = 1
    line_item.product_images = cfg('image_urls.vax')
    line_items.append(line_item)

    return line_items


def __generate_vax_payment_checkout_session_navigations(phone_number, session_id):

    navigation = PaymentRequestNavigation()
    query_params = 'session_id={}&brand=vax'.format(session_id)
    navigation.success_url = cfg(
        'payment.navigation.vax_success_url').format(query_params)
    navigation.cancel_url = cfg('payment.navigation.vax_cancel_url')

    return navigation


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


def bp_create_pre_registration(patient_id, patient_questionnaire_id, group_code):
    try:
        return create_pre_registration(patient_id, patient_questionnaire_id, group_code)
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


def bp_finalize_booking(booking_req: GgtBooking, finalize_registration_request):
    appointment: GgtAppointment = None
    status_message = None

    selected_services = []
    if "selectedServices" in dict(finalize_registration_request).keys():
        selected_services = finalize_registration_request.selectedServices
    try:
        booking_req, status_message = __create_patient_and_questionnaire(
            booking_req)
        if booking_req is None:
            raise ValueError(status_message)
        patient_id = booking_req.patient_id
        # determine if payment is required, if so, get billing info
        # TODO __evaluate_upfront_payment method combines all the services and calculate total value, it should be able to add items and prices separately in the receipt.
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
            appointment.payment_checkout_session = \
                __inject_payment_checkout_session(
                    appointment, upfront_payment_info, booking_req, selected_services)
            update_appointment_with_payment_session(appointment)
        else:
            # payment not required, confirm the appointment and notify
            update_appointment_with_confirmed_scheduled(appointment)
            __send_qrcode_sms(appointment)
            __send_qrcode_email(
                appointment, __get_country_from_location_services(selected_services))

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


def bp_ggv_finalize_booking(booking_req: GgtBooking, finalize_registration_request):
    try:
        booking_req, status_message = __create_patient_and_questionnaire(
            booking_req)
        selected_services = []
        if "selectedServices" in dict(finalize_registration_request).keys():
            selected_services = finalize_registration_request.selectedServices
        if booking_req is None:
            raise ValueError(status_message)

        patient_id = booking_req.patient_id
        # determine if payment is required, if so, get billing info
        upfront_payment_info = __evaluate_upfront_payment(booking_req)
        booking_req.total_cost = upfront_payment_info.total_cost
        booking_req.billed_amount = upfront_payment_info.billed_amount

        # generate appointment/booking
        appointment_1, appointment_2 = __generate_ggv_appointments(
            booking_req, selected_services)
        # if not (appointment_1 and appointment_2):
        #     raise ValueError('Invalid Appointment info')

        out_of = 2 if __is_dual_dose(selected_services) else 1
        if appointment_1:
            appointment_1 = __handle_vax_appointment(appointment_1, booking_req.insurance_photo, upfront_payment_info,
                                                     number=1, out_of=out_of)
        if appointment_2:
            appointment_2 = __handle_vax_appointment(appointment_2, booking_req.insurance_photo, upfront_payment_info,
                                                     number=2, out_of=out_of)
        # #
        # # # store insurance card
        # if not __save_insurance_image(appointment_1.id, booking_req.insurance_photo):
        #     pass  # allow transaction to proceed. TODO: Handle alternative action
        # # card
        # if not __save_insurance_image(appointment_2.id, booking_req.insurance_photo):
        #     pass  # allow transaction to proceed. TODO: Handle alternative action
        #
        # # if a payment is required, generate a payment link
        # appointment_1.payment_url = ''
        # appointment_2.payment_url = ''
        # if upfront_payment_info.is_payment_required:
        #     appointment_1.payment_url = __inject_payment_flow(appointment_1)
        #     appointment_2.payment_url = __inject_payment_flow(appointment_2)
        # else:
        #     # payment not required, confirm the appointment and notify
        #     update_appointment_with_confirmed_scheduled(appointment_1)
        #     update_appointment_with_confirmed_scheduled(appointment_2)
        #     __send_ggv_qrcode_sms(appointment_1, "1")
        #     __send_ggv_qrcode_email(appointment_1)
        #     __send_ggv_qrcode_sms(appointment_2, "2")
        #     __send_ggv_qrcode_email(appointment_2)

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


def __handle_vax_appointment(appointment, insurance_photo, upfront_payment_info, number=1, out_of=2):
    if not __save_insurance_image(appointment.id, insurance_photo):
        pass
    appointment.payment_url = ''
    if upfront_payment_info.is_payment_required:
        appointment.payment_url = __inject_payment_flow(appointment)
    else:
        # payment not required, confirm the appointment and notify
        update_appointment_with_confirmed_scheduled(appointment)
        __send_ggv_qrcode_sms(appointment, number, out_of)
        __send_ggv_qrcode_email(appointment)
    return appointment


def bp_ggv_finalize_pre_booking(booking_req: GgtBooking):
    status_message = None
    try:
        booking_req, status_message = __create_patient_and_questionnaire(
            booking_req)
        if booking_req is None:
            raise ValueError(status_message)
        patient_id = booking_req.patient_id
        patient_questionnaire_id = booking_req.patient_questionnaire_id
        __send_ggv_pre_registration_sms(
            booking_req.first_name, booking_req.phone_number)
        __send_ggv_pre_registration_email(
            booking_req.first_name, booking_req.email)
    except Exception as err:
        status_message = str(err)
        log_generic(
            type=c.ERROR,
            booking_req=booking_req,
            function=whoami(),
            error=err
        )
        raise HTTPException(status_code=500)

    return status_message, patient_id, patient_questionnaire_id


def bp_finalize_payment(appointment_id: int, wp_receipt_token: str):
    try:
        appointment = get_appointment(appointment_id)
        if appointment.wp_receipt_token == wp_receipt_token:
            update_appointment_with_confirmed_scheduled(appointment)
            __send_qrcode_sms(appointment)
            __send_qrcode_email(appointment, __get_country_from_location_services(
                appointment.service_selection_codes))
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
        parts = token.split("+")
        test_id = ""
        if len(parts) == 2:
            token = parts[0]
            test_id = parts[1]

        lab_result = get_test_result_by_token(token, test_id)

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


def bp_lookup_certificate(phone_number, dob, first_name, last_name, token):
    try:
        first_name = first_name.strip()
        last_name = last_name.strip()
        return lookup_certificate(phone_number, dob, first_name, last_name, token)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            dob=dob,
            function=whoami(),
            error=err
        )

    return None, None


def bp_reschedule_first_appointment(otp, appointment_id_1, appointment_id_2, appointment_1_dt_id, appointment_2_dt_id,
                                    phone_number):
    try:
        '''
            TODO: Confirm with product team if we need OTP verification here.
        '''
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


def bp_reschedule_second_appointment(appointment_id_1, appointment_id_2, appointment_2_dt_id):
    try:

        if __is_first_shot_taken(appointment_id_1):
            release_ggv_slot(appointment_id_2)
            slot_2 = get_slot_information(appointment_2_dt_id, slot_type='vax')
            lock_ggv_slot(appointment_id_2, appointment_2_dt_id)
            appointment_2 = re_schedule_appointment(appointment_id_2, slot_2)
            __send_ggv_qrcode_sms(appointment_2, "2")
            __send_ggv_qrcode_email(appointment_2)
            return True
        else:
            log_generic(
                type=c.INFO,
                appointment_id_1=appointment_id_1,
                appointment_id_2=appointment_id_2,
                message="First shot has not been taken yet.",
                function=whoami()
            )
            return False

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id_2=appointment_id_2,
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


def bp_get_vax_certificate(patient_id, cert_id, pass_through=False):
    if __is_open(patient_id) or pass_through:

        key = "{}/{}".format(patient_id, cert_id)
        bucket = cfg('aws.vax_certificate_bucket')

        blob = read_file(bucket, key)

        def get_image(b):
            yield b

        if blob:
            return StreamingResponse(get_image(blob),
                                     media_type="image/jpg",
                                     headers={
                                         'Content-Disposition': 'inline; filename="vaccine_certificate.png"'
            }
            )

        else:
            raise HTTPException(status_code=404, detail='Image not found')
    else:
        return None


def bp_send_wallet_pass_update_to_apple(token):
    try:
        print(token)
        print('https://api.push.apple.com/3/device/'+token)
        cert = (cert_pem, ssl_key, key_pem_password)
        client = httpx.Client(http2=True, cert=cert, headers={'apns-push-type': 'alert'})
        r = client.post('https://api.push.apple.com/3/device/'+token, headers={
            'apns-push-type': 'alert'}, data=json.dumps({"aps": {"alert": "GoGetDoc Pass Update"}}))
        print(r.status_code)
        return True
    except Exception as err:
        print(err)
    return False


def bp_get_wallet_pass(pkpass_req, portal=False):
    try:
        log_generic(
            type=c.INFO,
            function=whoami(),
            msg="PATIENT-GET-WALLET-PASS-REQUEST-RECEIVED",
            phone_number=pkpass_req.phone_number,
            dob=pkpass_req.dob,
            first_name=pkpass_req.first_name,
            last_name=pkpass_req.last_name,
            token=pkpass_req.token,
            req_type=pkpass_req.type
        )
        if not portal:
            patient = lookup_pkpass(pkpass_req.phone_number, pkpass_req.dob,
                                    pkpass_req.first_name, pkpass_req.last_name, pkpass_req.token)
        if portal:
            patient = lookup_pkpass_for_portal(pkpass_req.phone_number, pkpass_req.dob,
                                               pkpass_req.first_name, pkpass_req.last_name)
        print(patient)
        if patient:
            log_generic(
                type=c.INFO,
                function=whoami(),
                msg="PATIENT-GET-WALLET-PASS-PATIENT_FOUND",
                patient_id=patient["patient_id"],
                first_name=patient["first_name"],
                last_name=patient["last_name"],
                dob=patient["dob"],
                level=patient["level"],
                verfiedDate=patient["verfiedDate"],
                certificates=patient["certificates"],
                certNo=patient["certNo"]
            )
            return __generate_wallet_pass(pkpass_req, patient, verification=None)
        else:
            log_generic(
                type=c.ERROR,
                function=whoami(),
                msg="PATIENT-GET-WALLET-PASS-PATIENT_NOT_FOUND",
                phone_number=pkpass_req.phone_number,
                dob=pkpass_req.dob,
                first_name=pkpass_req.first_name,
                last_name=pkpass_req.last_name,
                token=pkpass_req.token,
                req_type=pkpass_req.type,
            )
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            msg="PATIENT-GET-WALLET-PASS-REQUEST-FAILED",
            phone_number=pkpass_req.phone_number,
            dob=pkpass_req.dob,
            first_name=pkpass_req.first_name,
            last_name=pkpass_req.last_name,
            token=pkpass_req.token,
            req_type=pkpass_req.type,
            err=err
        )
    return False


def bp_vax_wallet_pass_apple_upadte(device_id, pass_type, serial_no, pushToken, auth):
    try:
        patient_id = __get_patient_id(auth.replace('ApplePass ', ''))
        print("patient_id", patient_id)
        if(patient_id):
            save_apple_wallet_updates(
                patient_id, device_id, pass_type, serial_no, pushToken)
            return True
    except Exception as err:
        log_generic(
            type=c.ERROR,
            device_id=device_id,
            serial_no=serial_no,
            function=whoami(),
            error=err
        )
    return False


def bp_vax_wallet_pass_apple_upadte_serial(device_id, pass_type):
    try:
        serial = __get_serial(device_id, pass_type)
        print("serial", serial)
        print({
            "lastUpdated": datetime.now(),
            "serialNumbers": [serial['serial_no']]
        })
        return {
            "lastUpdated": datetime.now(),
            "serialNumbers": [serial['serial_no']]
        }
    except Exception as err:
        log_generic(
            type=c.ERROR,
            device_id=device_id,
            function=whoami(),
            error=err
        )
    return False


def bp_vax_wallet_get_new_pass(serial_no, auth):
    patient_id = __get_patient_id(auth.replace('ApplePass ', ''))
    print(patient_id)
    if(patient_id):
        blob = read_file('pkpass-prod', patient_id+'.pkpass')

        def get_pkpass(b):
            yield b
        if blob:
            return StreamingResponse(
                get_pkpass(blob),
                media_type="application/vnd.apple.pkpass",
                headers={
                    'LastModified': datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f")
                }
            )
        else:
            raise HTTPException(status_code=404, detail='Pass not found')
    else:
        raise HTTPException(status_code=404, detail='Pass not found')


def bp_call_non_sms_phone(phone_number):
    try:
        phone_number = validate_phone_number_format(phone_number)
        existing_patient = get_existing_patients(phone_number)
        token = None
        if existing_patient:
            token = existing_patient['token']
        otp_code, token = __create_pending_entry(phone_number, token)
        print(otp_code)
        return place_twilio_otp(phone_number, otp_code, "Go Get")

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
    return False


def __sanitize_names(req: LookupGGVAddVaxCertRequest):
    req.first_name = req.first_name.strip()
    req.last_name = req.last_name.strip()

    if req.pristine:
        req.pristine.first_name = req.pristine.first_name.strip(
        ) if req.pristine.first_name else None
        req.pristine.last_name = req.pristine.last_name.strip(
        ) if req.pristine.last_name else None
    return req


def bp_add_vax_certificate(req, booster=False):
    try:
        req = __sanitize_names(req)
        pristine = req.pristine
        log_generic(
            type=c.INFO,
            function=whoami(),
            msg="PATIENT-CERTIFICATE-ADD-REQUEST-RECEIVED",
            first_name=req.first_name,
            last_name=req.last_name,
            phone_number=req.phone_number,
            email=req.email,
            dob=req.dob,
            vax_type=req.vax_type,
            first_vax_dt=req.first_vax_dt,
            vax_1_lot_number=req.vax_1_lot_number,
            second_vax_dt=req.second_vax_dt,
            vax_2_lot_number=req.vax_2_lot_number,
            pristine_dob=pristine.dob if pristine else None,
            pristine_first_name=pristine.first_name if pristine else None,
            pristine_last_name=pristine.last_name if pristine else None,
            vax_image=1 if req.vax_image else 0,
            id_image=1 if req.id_image else 0
        )
        from ggt.models.process_models.bp_portal_experience import bp_add_vax_certificate as add_vax_certificate
        ocr = {
            "patient_id": None,
            "first_name": 0,
            "last_name": 0,
            "vax_type": 0,
            "dob": 0,
            "cert1_id": None,
            "first_vax_dt": 0,
            "vax_1_lot_number": 0,
            "cert2_id": None,
            "second_vax_dt": 0,
            "vax_2_lot_number": 0
        }
        if pristine and pristine.dob == req.dob and pristine.first_name == req.first_name and \
                pristine.last_name == req.last_name:
            cert_details = add_vax_certificate(req)

            show_payment_view = not cert_details['active_certificates_available']

            ocr["patient_id"] = cert_details["patient_id"]
            ocr["cert1_id"] = cert_details["cert1_id"]
            if cert_details["cert2_id"]:
                ocr["cert2_id"] = cert_details["cert2_id"]
            is_vax_card_pristine = __vax_card_pristine(
                cert_details["patient_id"], cert_details["cert1_id"], req, ocr)
            is_photo_id_pristine = __photo_id_pristine(
                cert_details["patient_id"], cert_details["cert1_id"], req, ocr)

            __update_ocr_status(ocr["patient_id"], ocr["first_name"], ocr["last_name"], ocr["vax_type"], ocr["dob"],
                                ocr["cert1_id"], ocr["first_vax_dt"], ocr["vax_1_lot_number"],
                                ocr["cert2_id"], ocr["second_vax_dt"], ocr["vax_2_lot_number"])

            if is_vax_card_pristine:
                log_generic(
                    type=c.INFO,
                    function=whoami(),
                    msg="PATIENT-CERTIFICATE-OCR-VERIFIED",
                    first_name=req.first_name,
                    last_name=req.last_name,
                    phone_number=req.phone_number,
                    email=req.email,
                    dob=req.dob,
                    vax_type=req.vax_type,
                    first_vax_dt=req.first_vax_dt,
                    vax_1_lot_number=req.vax_1_lot_number,
                    second_vax_dt=req.second_vax_dt,
                    vax_2_lot_number=req.vax_2_lot_number,
                    pristine_dob=pristine.dob if pristine else None,
                    pristine_first_name=pristine.first_name if pristine else None,
                    pristine_last_name=pristine.last_name if pristine else None,
                    vax_image=1 if req.vax_image else 0,
                    id_image=1 if req.id_image else 0
                )
            if is_photo_id_pristine:
                log_generic(
                    type=c.INFO,
                    function=whoami(),
                    msg="PATIENT-ID-OCR-VERIFIED",
                    first_name=req.first_name,
                    last_name=req.last_name,
                    phone_number=req.phone_number,
                    email=req.email,
                    dob=req.dob,
                    vax_type=req.vax_type,
                    first_vax_dt=req.first_vax_dt,
                    vax_1_lot_number=req.vax_1_lot_number,
                    second_vax_dt=req.second_vax_dt,
                    vax_2_lot_number=req.vax_2_lot_number,
                    pristine_dob=pristine.dob if pristine else None,
                    pristine_first_name=pristine.first_name if pristine else None,
                    pristine_last_name=pristine.last_name if pristine else None,
                    vax_image=1 if req.vax_image else 0,
                    id_image=1 if req.id_image else 0
                )
            if is_vax_card_pristine and is_photo_id_pristine:
                if verify_certificate([cert_details["cert1_id"]], "2"):
                    log_generic(
                        type=c.INFO,
                        function=whoami(),
                        msg="PATIENT-CERTIFICATE-1-VERIFIED-LEVEL-2",
                        first_name=req.first_name,
                        last_name=req.last_name,
                        phone_number=req.phone_number,
                        email=req.email,
                        dob=req.dob,
                        vax_type=req.vax_type,
                        first_vax_dt=req.first_vax_dt,
                        vax_1_lot_number=req.vax_1_lot_number,
                        second_vax_dt=req.second_vax_dt,
                        vax_2_lot_number=req.vax_2_lot_number,
                        pristine_dob=pristine.dob if pristine else None,
                        pristine_first_name=pristine.first_name if pristine else None,
                        pristine_last_name=pristine.last_name if pristine else None,
                        vax_image=1 if req.vax_image else 0,
                        id_image=1 if req.id_image else 0
                    )
                else:
                    log_generic(
                        type=c.ERROR,
                        function=whoami(),
                        msg="PATIENT-CERTIFICATE-1-VERIFICATION-DB-UPDATE-FAILED",
                        first_name=req.first_name,
                        last_name=req.last_name,
                        phone_number=req.phone_number,
                        email=req.email,
                        dob=req.dob,
                        vax_type=req.vax_type,
                        first_vax_dt=req.first_vax_dt,
                        vax_1_lot_number=req.vax_1_lot_number,
                        second_vax_dt=req.second_vax_dt,
                        vax_2_lot_number=req.vax_2_lot_number,
                        pristine_dob=pristine.dob if pristine else None,
                        pristine_first_name=pristine.first_name if pristine else None,
                        pristine_last_name=pristine.last_name if pristine else None,
                        vax_image=1 if req.vax_image else 0,
                        id_image=1 if req.id_image else 0
                    )
                if cert_details["cert2_id"]:
                    if verify_certificate([cert_details["cert2_id"]], "2"):
                        log_generic(
                            type=c.INFO,
                            function=whoami(),
                            msg="PATIENT-CERTIFICATE-2-VERIFIED-LEVEL-2",
                            first_name=req.first_name,
                            last_name=req.last_name,
                            phone_number=req.phone_number,
                            email=req.email,
                            dob=req.dob,
                            vax_type=req.vax_type,
                            first_vax_dt=req.first_vax_dt,
                            vax_1_lot_number=req.vax_1_lot_number,
                            second_vax_dt=req.second_vax_dt,
                            vax_2_lot_number=req.vax_2_lot_number,
                            pristine_dob=pristine.dob if pristine else None,
                            pristine_first_name=pristine.first_name if pristine else None,
                            pristine_last_name=pristine.last_name if pristine else None,
                            vax_image=1 if req.vax_image else 0,
                            id_image=1 if req.id_image else 0
                        )
                    else:
                        log_generic(
                            type=c.ERROR,
                            function=whoami(),
                            msg="PATIENT-CERTIFICATE-2-VERIFICATION-DB-UPDATE-FAILED",
                            first_name=req.first_name,
                            last_name=req.last_name,
                            phone_number=req.phone_number,
                            email=req.email,
                            dob=req.dob,
                            vax_type=req.vax_type,
                            first_vax_dt=req.first_vax_dt,
                            vax_1_lot_number=req.vax_1_lot_number,
                            second_vax_dt=req.second_vax_dt,
                            vax_2_lot_number=req.vax_2_lot_number,
                            pristine_dob=pristine.dob if pristine else None,
                            pristine_first_name=pristine.first_name if pristine else None,
                            pristine_last_name=pristine.last_name if pristine else None,
                            vax_image=1 if req.vax_image else 0,
                            id_image=1 if req.id_image else 0
                        )
                send_ggv_certificate_level_1_sms(
                    req.first_name.title(), req.phone_number, "2")
                send_ggv_certificate_level_1_email(
                    req.first_name.title(), req.email, "2")
                return {
                    "level": 2,
                    "cert_1": cert_details["cert1_id"],
                    "cert_2": cert_details["cert2_id"] if cert_details["cert2_id"] else None,
                    "show_payment_view": show_payment_view
                }
            else:
                log_generic(
                    type=c.INFO,
                    function=whoami(),
                    msg="PATIENT-CERTIFICATE-OCR-VERIFICATION-FAILED",
                    first_name=req.first_name,
                    last_name=req.last_name,
                    phone_number=req.phone_number,
                    email=req.email,
                    dob=req.dob,
                    vax_type=req.vax_type,
                    first_vax_dt=req.first_vax_dt,
                    vax_1_lot_number=req.vax_1_lot_number,
                    second_vax_dt=req.second_vax_dt,
                    vax_2_lot_number=req.vax_2_lot_number,
                    pristine_dob=pristine.dob if pristine else None,
                    pristine_first_name=pristine.first_name if pristine else None,
                    pristine_last_name=pristine.last_name if pristine else None,
                    vax_image=1 if req.vax_image else 0,
                    id_image=1 if req.id_image else 0
                )
                return {
                    "level": 1,
                    "cert_1": cert_details["cert1_id"],
                    "cert_2": cert_details["cert2_id"] if cert_details["cert2_id"] else None,
                    "show_payment_view": show_payment_view
                }
        else:
            log_generic(
                type=c.INFO,
                function=whoami(),
                msg="PATIENT-CERTIFICATE-ADD-REQUEST-NOT-PRISTINE",
                first_name=req.first_name,
                last_name=req.last_name,
                phone_number=req.phone_number,
                email=req.email,
                dob=req.dob,
                vax_type=req.vax_type,
                first_vax_dt=req.first_vax_dt,
                vax_1_lot_number=req.vax_1_lot_number,
                second_vax_dt=req.second_vax_dt,
                vax_2_lot_number=req.vax_2_lot_number,
                pristine_dob=pristine.dob if pristine else None,
                pristine_first_name=pristine.first_name if pristine else None,
                pristine_last_name=pristine.last_name if pristine else None,
                vax_image=1 if req.vax_image else 0,
                id_image=1 if req.id_image else 0
            )
            cert_details = add_vax_certificate(req, booster)

            show_payment_view = not cert_details['active_certificates_available'] and not booster

            if cert_details:
                # send_ggv_certificate_level_1_sms(req.first_name.title(), req.phone_number, "1")
                # send_ggv_certificate_level_1_email(req.first_name.title(), req.email, "1")
                return {
                    "level": 1,
                    "cert_1": cert_details["cert1_id"],
                    "cert_2": cert_details["cert2_id"] if cert_details["cert2_id"] else None,
                    "show_payment_view": show_payment_view
                }
            else:
                raise Exception('Add vax certificate failed')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            msg="PATIENT-CERTIFICATE-ADD-REQUEST-ERROR",
            function=whoami(),
            first_name=req.first_name,
            last_name=req.last_name,
            phone_number=req.phone_number,
            email=req.email,
            dob=req.dob,
            vax_type=req.vax_type,
            first_vax_dt=req.first_vax_dt,
            vax_1_lot_number=req.vax_1_lot_number,
            second_vax_dt=req.second_vax_dt,
            vax_2_lot_number=req.vax_2_lot_number,
            pristine_dob=pristine.dob if pristine else None,
            pristine_first_name=pristine.first_name if pristine else None,
            pristine_last_name=pristine.last_name if pristine else None,
            vax_image=1 if req.vax_image else 0,
            id_image=1 if req.id_image else 0,
            error=err
        )
    return False


def bp_update_group_code(req):
    update_group_code_for_existing_patient(req)
    return True


def bp_pass_verification(req):
    try:
        patient_id = __get_patient_id(req.query)
        if (__is_pass_verification_blocked_for(patient_id)):
            return False

        certs = get_verification_level_from_patient_id(patient_id, req.dob)
        if (certs == None or len(certs) == 0):
            __register_pass_verification_fail(patient_id)

        if("COVID_19_VACCINE_JNJ" not in certs[0]['service_code'] and certs[0]['verification_level'] > 1 and certs[1]['verification_level'] > 1):
            return {
                "fully_vaccinated": True,
                "level": certs[0]['verification_level'],
                "image1": get_temp_pkpass_url(str(patient_id) + "/"+str(certs[0]['id']) + ".jpg", "ggt-vax-certificates"),
                "image2": get_temp_pkpass_url(str(patient_id) + "/"+str(certs[1]['id']) + ".jpg", "ggt-vax-certificates")
            }
        elif("COVID_19_VACCINE_JNJ" in certs[0]['service_code'] and certs[0]['verification_level'] > 1):
            print("I am here")
            return {
                "fully_vaccinated": True,
                "level": certs[0]['verification_level'],
                "image1": get_temp_pkpass_url(str(patient_id) + "/"+str(certs[0]['id']) + ".jpg", "ggt-vax-certificates"),
                "image2": None
            }
        return {
            "fully_vaccinated": False,
            "level": certs[0]['verification_level'],
            "image1": get_temp_pkpass_url(str(patient_id) + "/"+str(certs[0]['id']) + ".jpg", "ggt-vax-certificates"),
            "image2": get_temp_pkpass_url(str(patient_id) + "/"+str(certs[1]['id']) + ".jpg", "ggt-vax-certificates")
        }
    except Exception as err:
        log_generic(
            type=c.ERROR,
            msg="PASS-VERIFICATION",
            function=whoami(),
            query=req.query,
            dob=req.dob,
            error=err
        )
    return False


def bp_update_android_pass(req):
    try:
        payloadObject = json.loads(req.objectResourcePayload)
        payloadClass = json.loads(req.classResourcePayload)
        classResponse = __updateClass(payloadClass, payloadClass["id"])
        objectResponse = __updateObject(payloadObject, payloadObject["id"])

        __handleInsertCallStatusCode(
            classResponse, "class", payloadClass["id"], None, None)

        __handleInsertCallStatusCode(
            objectResponse, "object", payloadObject["id"], payloadClass["id"], None)
        return True
    except Exception as err:
        log_generic(
            type=c.ERROR,
            msg="WALLET-PASS-UPDATE",
            function=whoami(),
            error=err
        )
    return False

########################################################################################################
# [Protected] functions
########################################################################################################

# TODO: Prevent from looking up slots that are already assigned to an appointment
# TODO, doesn't check if it's already booked
# TEMP, not using fixed slots since operational conditions allow oversubscribing


def __get_serial(devide_id, pass_type):
    return get_serial_no(devide_id, pass_type)


def __get_patient_id(query):
    try:
        boto_client = boto3.client(
            'kms',
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
            region_name='us-east-2'
        )
        print(query)
        query = query.encode('utf-8')
        from base64 import b64encode, decodebytes
        print(decodebytes(query))
        response = boto_client.decrypt(CiphertextBlob=decodebytes(query))
        print(response)
        print(response['Plaintext'].decode('utf-8'))
        return response['Plaintext'].decode('utf-8')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            query=query,
            function=whoami(),
            error=err
        )


def __get_vax_card_ocr(patient_id, cert_id):
    boto_client = boto3.client(
        'textract',
        aws_access_key_id=cfg('aws.access_key_id'),
        aws_secret_access_key=cfg('aws.secret_access_key'),
        region_name='us-east-2'
    )
    print('{}/{}.jpg'.format(patient_id, cert_id))
    response = boto_client.analyze_document(
        Document={
            'S3Object': {
                'Bucket': cfg('aws.vax_certificate_bucket'),
                'Name': '{}/{}.jpg'.format(patient_id, cert_id)
            }
        },
        FeatureTypes=[
            'TABLES'
        ]
    )
    # print(response)
    card_string = ""
    for index, item in enumerate(response["Blocks"]):
        if "Text" in item and item["BlockType"] == "WORD":
            card_string = card_string + " " + item["Text"].replace(" ", "")
    return card_string.lstrip().strip("0").lower()


def __get_vax_card_ocr_gcp(content):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './ggt/configs/gpay/ggt-pfe-prod-e3201b1cc798.json'
    client = vision.ImageAnnotatorClient()
    # import binascii
    # content1 = binascii.a2b_base64(content)
    image = vision.Image()
    image.source.image_uri = content
    # print(image)
    response = client.text_detection(image=image)
    print(response.full_text_annotation.text)
    return response.full_text_annotation.text


def __photo_id_pristine(patient_id, cert_id, cert_request: LookupGGVAddVaxCertRequest, ocr):
    id_ocr_string = __get_vax_card_ocr(patient_id, str(cert_id) + '_id_image')
    log_generic(
        type=c.INFO,
        function=whoami(),
        msg="PATIENT-CERTIFICATE-ADD-REQUEST-ID-OCR-STRING",
        ocr_string=str(id_ocr_string)
        # first_name=cert_request.first_name,
        # last_name=cert_request.last_name,
        # phone_number=cert_request.phone_number,
        # email=cert_request.email,
        # dob=cert_request.dob,
        # vax_type=cert_request.vax_type,
        # first_vax_dt=cert_request.first_vax_dt,
        # vax_1_lot_number=cert_request.vax_1_lot_number,
        # second_vax_dt=cert_request.second_vax_dt,
        # vax_2_lot_number=cert_request.vax_2_lot_number,
        # pristine_dob=cert_request.pristine.dob if cert_request.pristine else None,
        # pristine_first_name=cert_request.pristine.first_name if cert_request.pristine else None,
        # pristine_last_name=cert_request.pristine.last_name if cert_request.pristine else None,
        # vax_image=1 if cert_request.vax_image else 0,
        # id_image=1 if cert_request.id_image else 0,
    )
    date_of_birth = datetime.strptime(cert_request.dob, '%Y-%m-%d')
    ocr["first_name"] = 1 if cert_request.first_name.lower() in id_ocr_string else 0
    ocr["last_name"] = 1 if cert_request.last_name.lower() in id_ocr_string else 0
    ocr["dob"] = 1 if match_the_date(date_of_birth, id_ocr_string) else 0
    # if (cert_request.first_name.lower() in id_ocr_string and
    #         cert_request.last_name.lower() in id_ocr_string and
    #         (date_of_birth.strftime('%-m/%-d/%y') in id_ocr_string or date_of_birth.strftime(
    #             '%m/%d/%y') in id_ocr_string or
    #          date_of_birth.strftime('%-m/%-d/%Y') in id_ocr_string or date_of_birth.strftime(
    #                     '%m/%d/%Y') in id_ocr_string or
    #          date_of_birth.strftime('%-m,%-d,%y') in id_ocr_string or date_of_birth.strftime(
    #                     '%b/%-d/%Y') in id_ocr_string)):
    #     print("first_name, last_name and dob matched in photo id ocr")
    #     return True
    # print("first_name, last_name or dob did not match in photo id ocr")
    # return False
    return (cert_request.first_name.lower() in id_ocr_string) if ((cert_request.first_name.lower() in id_ocr_string) == (cert_request.last_name.lower() in id_ocr_string)) else match_the_date(date_of_birth, id_ocr_string)


def __vax_card_pristine(patient_id, cert_id, cert_request: LookupGGVAddVaxCertRequest, ocr):
    try:
        vax_ocr_string = __get_vax_card_ocr(patient_id, cert_id)
        # vax_ocr_string = vax_ocr_string + " " + __get_vax_card_ocr_gcp(cert_request.vax_image_url)
        log_generic(
            type=c.INFO,
            function=whoami(),
            msg="PATIENT-CERTIFICATE-ADD-REQUEST-CERT-OCR-STRING",
            ocr_string=str(vax_ocr_string)
            # first_name=cert_request.first_name,
            # last_name=cert_request.last_name,
            # phone_number=cert_request.phone_number,
            # email=cert_request.email,
            # dob=cert_request.dob,
            # vax_type=cert_request.vax_type,
            # first_vax_dt=cert_request.first_vax_dt,
            # vax_1_lot_number=cert_request.vax_1_lot_number,
            # second_vax_dt=cert_request.second_vax_dt,
            # vax_2_lot_number=cert_request.vax_2_lot_number,
            # pristine_dob=cert_request.pristine.dob if cert_request.pristine else None,
            # pristine_first_name=cert_request.pristine.first_name if cert_request.pristine else None,
            # pristine_last_name=cert_request.pristine.last_name if cert_request.pristine else None,
            # vax_image=1 if cert_request.vax_image else 0,
            # id_image=1 if cert_request.id_image else 0,
        )
        first_vax_dt = datetime.strptime(cert_request.first_vax_dt, '%Y-%m-%d')
        if cert_request.vax_2_lot_number != "" and cert_request.vax_2_lot_number is not None:
            second_vax_dt = datetime.strptime(
                cert_request.second_vax_dt, '%Y-%m-%d')

        ocr["vax_type"] = 1 if cert_request.vax_type.lower() in vax_ocr_string else 0
        ocr["first_vax_dt"] = 1 if match_the_date(
            first_vax_dt, vax_ocr_string) else 0
        ocr["vax_1_lot_number"] = 1 if cert_request.vax_1_lot_number.strip(
            "0").lower() in vax_ocr_string else 0
        if cert_request.vax_2_lot_number != "" and cert_request.vax_2_lot_number is not None:
            ocr["second_vax_dt"] = 1 if match_the_date(
                second_vax_dt, vax_ocr_string) else 0
            ocr["vax_2_lot_number"] = 1 if cert_request.vax_2_lot_number.strip(
                "0").lower() in vax_ocr_string else 0
        if (cert_request.vax_2_lot_number != "" and cert_request.vax_2_lot_number is not None):
            return True if (cert_request.vax_type.lower() in vax_ocr_string or
                            match_the_date(first_vax_dt, vax_ocr_string) or
                            cert_request.vax_1_lot_number.strip("0").lower() in vax_ocr_string) and (cert_request.vax_type.lower() in vax_ocr_string or
                                                                                                     match_the_date(second_vax_dt, vax_ocr_string) or
                                                                                                     cert_request.vax_2_lot_number.strip("0").lower() in vax_ocr_string) else False

        elif (cert_request.vax_2_lot_number == "" or cert_request.vax_2_lot_number is None):
            return True if (cert_request.vax_type.lower() in vax_ocr_string or
                            match_the_date(first_vax_dt, vax_ocr_string) or
                            cert_request.vax_1_lot_number.strip("0").lower() in vax_ocr_string) else False

    except Exception as err:
        log_generic(
            type=c.ERROR,
            patient_id=patient_id,
            function=whoami(),
            error=err
        )


def match_the_date(date, ocr_string):
    id_ocr_string = ocr_string
    dob_month = int(date.strftime('%-m'))
    dob_day = int(date.strftime('%-d'))
    dob_year = int(date.strftime('%Y'))
    dob_month_str = ""
    if dob_month < 10:
        dob_month_str += "(" + str(dob_month) + \
            "@|0@\s*" + str(dob_month) + "@)"
    else:
        dob_month_str = str(int(dob_month / 10)) + \
            "@\s*" + str(dob_month % 10) + "@"
    dob_month_str = dob_month_str.replace("0", "[o0]").replace(
        "1", "[1il\/]").replace("@", "{1}")
    dob_day_str = ""
    if dob_day < 10:
        dob_day_str += "(" + str(dob_day) + "@|0@\s*" + str(dob_day) + "@)"
    else:
        dob_day_str = str(int(dob_day / 10)) + "@\s*" + str(dob_day % 10) + "@"
    dob_day_str = dob_day_str.replace("0", "[o0]").replace(
        "1", "[1il\/]").replace("@", "{1}")
    dob_cent = 20
    if (dob_year > 100):
        dob_cent = int(dob_year / 100)
        dob_year = dob_year % 100
    dob_cent_str = ""
    if dob_cent < 10:
        dob_cent_str += "(" + str(dob_cent) + "@|0@\s*" + str(dob_cent) + "@)"
    else:
        dob_cent_str = str(int(dob_cent / 10)) + "@\s*" + \
            str(dob_cent % 10) + "@"
    dob_cent_str = dob_cent_str.replace("0", "[o0]").replace(
        "1", "[1il\/]").replace("@", "{1}")
    dob_year_str = ""
    if dob_year < 10:
        dob_year_str += "(" + str(dob_year) + "@|0@\s*" + str(dob_year) + "@)"
    else:
        dob_year_str = str(int(dob_year / 10)) + "@\s*" + \
            str(dob_year % 10) + "@"
    dob_year_str = dob_year_str.replace("0", "[o0]").replace(
        "1", "[1il\/]").replace("@", "{1}")
    regexstr = "\s*" + dob_month_str + "\s*[1il\/\.\-\\\\]{1}\s*" + dob_day_str + \
        "\s*[1il\/\.\-\\\\]{1}\s*(" + dob_year_str + "|" + \
        dob_cent_str + "\s*" + dob_year_str + "){1}"
    print("ocr:" + id_ocr_string)
    print("Regex:" + regexstr)
    if re.search(regexstr, id_ocr_string, re.IGNORECASE):
        print("it is a match")
        return True
    else:
        return False


def __update_ocr_status(patient_id, first_name, last_name, vax_type, dob, cert1_id, first_vax_dt, vax_1_lot_number,
                        cert2_id, second_vax_dt, vax_2_lot_number):
    print(patient_id, first_name, last_name, vax_type, dob, cert1_id, first_vax_dt, vax_1_lot_number, cert2_id,
          second_vax_dt, vax_2_lot_number)
    return update_ocr(patient_id, first_name, last_name, vax_type, dob, cert1_id, first_vax_dt, vax_1_lot_number,
                      cert2_id, second_vax_dt, vax_2_lot_number)


def __generate_wallet_pass(pkpass_req, patient, verification):
    try:
        url_path = __get_barcode_string(pkpass_req.phone_number, patient)
        if pkpass_req.type == 'i':
            __generate_pk_pass(pkpass_req, patient, verification, url_path)
            print("__generate_pk_pass execution complete")
            print("uploading from: ",
                  "/tmp/{}.{}".format(str(patient["patient_id"]), "pkpass"))
            print("uploading as:", str(patient["patient_id"]) + ".pkpass")
            print("uploading to:", "pkpass-prod")
            uploaded = upload_file("/tmp/{}.{}".format(str(patient["patient_id"]), "pkpass"),
                                   str(patient["patient_id"]) + ".pkpass", "pkpass-prod")
            print("upload_file execution complete")
            if uploaded:
                return {
                    "pkpass_url": get_temp_pkpass_url(
                        str(patient["patient_id"]) + ".pkpass", "pkpass-prod")
                }
            else:
                return None
        elif pkpass_req.type == 'a':
            return __generate_gpay_pass(pkpass_req, patient, verification, url_path, pkpass_req.phone_number)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            pkpass_req=pkpass_req,
            function=whoami(),
            error=err
        )


def __get_barcode_string(phone, patient):
    try:
        boto_client = boto3.client(
            'kms',
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
            region_name='us-east-2'
        )
        patient["first_name"] + " " + patient["last_name"]
        str(patient["dob"])
        response = boto_client.encrypt(
            KeyId="e684baec-2a09-4348-b0bc-7f45dc0b2822", Plaintext=str(patient["patient_id"]))
        # print(response)
        from base64 import b64encode, b64decode
        print(response['CiphertextBlob'])
        print(b64encode(response['CiphertextBlob']))
        print(b64encode(response['CiphertextBlob']).decode('utf-8'))
        return b64encode(response['CiphertextBlob']).decode('utf-8')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone=phone,
            function=whoami(),
            error=err
        )


def __generate_gpay_pass(pkpass_req, patient, verification, url_path, phone):
    try:
        classUid = 'EVENTTICKET_CLASS_' + str(uuid.uuid4())
        classId = '%s.%s' % ("3388000000009256028", classUid)
        objectUid = 'EVENTTICKET_OBJECT_' + str(uuid.uuid4())
        objectId = '%s.%s' % ("3388000000009256028", objectUid)
        saved = save_android_pass_details(
            str(patient["patient_id"]), classId, objectId)
        if(saved):
            return __skinnyJwt("EVENTTICKET", classId, objectId, patient, url_path)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req=pkpass_req,
            function=whoami(),
            error=err
        )
    return None


def __skinnyJwt(verticalType, classId, objectId, patient, url_path):
    try:
        print(classId, objectId, url_path, patient["level"])
        skinnyJwt, objectResourcePayload, classResourcePayload = __makeSkinnyJwt(
            verticalType, classId, objectId, patient, url_path)
        if skinnyJwt is not None:
            return {
                "gpayPassURL": "https://pay.google.com/gp/v/save/" + skinnyJwt.decode('UTF-8')
            }
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __makeSkinnyJwt(verticalType, classId, objectId, patient, url_path):
    try:
        signedJwt = None
        classResourcePayload = None
        objectResourcePayload = None
        classResponse = None
        objectResponse = None

        try:
            # get class definition and object definition
            classResourcePayload, objectResourcePayload = getClassAndObjectDefinitions(
                verticalType, classId, objectId, classResourcePayload, objectResourcePayload, patient, url_path)

            # make authorized REST call to explicitly insert class into Google server.
            # if this is successful, you can check/update class definitions in Merchant Center GUI: https://pay.google.com/gp/m/issuer/list
            classResponse = __insertClass(verticalType, classResourcePayload)

            # make authorized REST call to explicitly insert object into Google server.
            objectResponse = __insertObject(
                verticalType, objectResourcePayload)

            # continue based on insert response status. Check https://developers.google.com/pay/passes/reference/v1/statuscodes
            # check class insert response. Will print out if class insert succeeds or not. Throws error if class resource is malformed.
            __handleInsertCallStatusCode(
                classResponse, "class", classId, None, None)

            # check object insert response. Will print out if object insert succeeds or not. Throws error if object resource is malformed, or if existing objectId's classId does not match the expected classId
            __handleInsertCallStatusCode(
                objectResponse, "object", objectId, classId, verticalType)

            print("put into JSON Web Token (JWT) format for Google Pay API for Passes")
            googlePassJwt = jwt.googlePassJwt()

            print(
                "only need to add objectId in JWT because class and object definitions were pre-inserted via REST call")
            __loadObjectIntoJWT(verticalType, googlePassJwt, {"id": objectId})

            print("sign JSON to make signed JWT")
            signedJwt = googlePassJwt.generateSignedJwt()

        except ValueError as err:
            print(err)

        # return "skinny" JWT. Try putting it into save link.
        # See https://developers.google.com/pay/passes/guides/get-started/implementing-the-api/save-to-google-pay#add-link-to-email
        return signedJwt, objectResourcePayload, classResourcePayload
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __loadObjectIntoJWT(verticalType, googlePassJwt, objectResourcePayload):
    try:
        googlePassJwt.addEventTicketObject(objectResourcePayload)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __handleInsertCallStatusCode(insertCallResponse, idType, id, checkClassId=None, verticalType=None):
    try:
        if insertCallResponse.status_code == 200:
            print('%sId (%s) insertion success!\n' % (idType, id))
        elif insertCallResponse.status_code == 409:  # id resource exists for this issuer account
            print('%sId: (%s) already exists. %s' %
                  (idType, id, "PASS ALREADY EXISTS"))

            # for object insert, do additional check
            if idType == "object":
                getCallResponse = None
                # get existing object Id data
                # if it is a new object Id, expected status is 409
                getCallResponse = __getObject(verticalType, id)
                # check if object's classId matches target classId
                classIdOfObjectId = getCallResponse.json()['classId']
                if classIdOfObjectId != checkClassId and checkClassId is not None:
                    raise ValueError(
                        'the classId of inserted object is (%s). It does not match the target classId (%s). The saved object will not have the class properties you expect.' % (
                            classIdOfObjectId, checkClassId))
        else:
            raise ValueError('%s insert issue.' %
                             (idType), insertCallResponse.text)

        return
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __getObject(verticalType, objectId):
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        credentials = __makeOauthCredential()

        response = None

        # Define get() REST call of target vertical
        uri = 'https://walletobjects.googleapis.com/walletobjects/v1'
        postfix = 'Object'
        path = __createPath(verticalType, postfix, objectId)

        # There is no Google API for Passes Client Library for Python.
        # Authorize a http client with credential generated from Google API client library.
        # see https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        authed_session = AuthorizedSession(credentials)

        # make the GET request to make an get(); this returns a response object
        # other methods require different http methods; for example, get() requires authed_Session.get(...)
        # check the reference API to make the right REST call
        # https://developers.google.com/pay/passes/reference/v1/
        # https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        response = authed_session.get(
            uri + path  # REST API endpoint
            , headers=headers  # Header; optional
        )

        return response
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __createPath(verticalType, postfix, id_to_use=''):
    try:
        return '/%s%s/%s' % ("eventTicket", postfix, id_to_use)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __makeOauthCredential():
    try:
        # the variables are in config file
        credentials = service_account.Credentials.from_service_account_file(
            './app/ggt/configs/gpay/ggt-pfe-prod-e3201b1cc798.json',
            scopes=['https://www.googleapis.com/auth/wallet_object.issuer'])

        return credentials
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __insertClass(verticalType, payload):
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        credentials = __makeOauthCredential()
        response = None

        # Define insert() REST call of target vertical
        uri = 'https://walletobjects.googleapis.com/walletobjects/v1'
        postfix = 'Class'
        path = __createPath(verticalType, postfix)

        # There is no Google API for Passes Client Library for Python.
        # Authorize a http client with credential generated from Google API client library.
        # see https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        authed_session = AuthorizedSession(credentials)
        print(authed_session)
        # make the POST request to make an insert(); this returns a response object
        # other methods require different http methods; for example, get() requires authed_Session.get(...)
        # check the reference API to make the right REST call
        # https://developers.google.com/pay/passes/reference/v1/
        # https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        response = authed_session.post(
            uri + path  # REST API endpoint
            , headers=headers  # Header; optional
            # non-form-encoded Payload for POST. Check rest API for format based on method.
            , json=payload
        )
        return response
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __updateClass(payload, id_to_use):
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        credentials = __makeOauthCredential()
        response = None

        # Define insert() REST call of target vertical
        uri = 'https://walletobjects.googleapis.com/walletobjects/v1'
        postfix = 'Class'
        path = __createPath(None, postfix, id_to_use=id_to_use)

        # There is no Google API for Passes Client Library for Python.
        # Authorize a http client with credential generated from Google API client library.
        # see https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        authed_session = AuthorizedSession(credentials)
        print(authed_session)
        # make the POST request to make an insert(); this returns a response object
        # other methods require different http methods; for example, get() requires authed_Session.get(...)
        # check the reference API to make the right REST call
        # https://developers.google.com/pay/passes/reference/v1/
        # https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        response = authed_session.put(
            uri + path  # REST API endpoint
            , headers=headers  # Header; optional
            # non-form-encoded Payload for POST. Check rest API for format based on method.
            , json=payload
        )
        return response
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __insertObject(verticalType, payload):
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        credentials = __makeOauthCredential()
        response = None

        # Define insert() REST call of target vertical
        uri = 'https://walletobjects.googleapis.com/walletobjects/v1'
        postfix = 'Object'
        path = __createPath(verticalType, postfix)
        # There is no Google API for Passes Client Library for Python.
        # Authorize a http client with credential generated from Google API client library.
        # see https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        authed_session = AuthorizedSession(credentials)

        # make the POST request to make an insert(); this returns a response object
        # other methods require different http methods; for example, get() requires authed_Session.get(...)
        # check the reference API to make the right REST call
        # https://developers.google.com/pay/passes/reference/v1/
        # https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        response = authed_session.post(
            uri + path  # REST API endpoint
            , headers=headers  # Header; optional
            # non-form-encoded Payload for POST. Check rest API for format based on method.
            , json=payload
        )
        return response
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __updateObject(payload, id_to_use):
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        credentials = __makeOauthCredential()
        response = None

        # Define insert() REST call of target vertical
        uri = 'https://walletobjects.googleapis.com/walletobjects/v1'
        postfix = 'Object'
        path = __createPath(None, postfix, id_to_use=id_to_use)
        # There is no Google API for Passes Client Library for Python.
        # Authorize a http client with credential generated from Google API client library.
        # see https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        authed_session = AuthorizedSession(credentials)

        # make the POST request to make an insert(); this returns a response object
        # other methods require different http methods; for example, get() requires authed_Session.get(...)
        # check the reference API to make the right REST call
        # https://developers.google.com/pay/passes/reference/v1/
        # https://google-auth.readthedocs.io/en/latest/user-guide.html#making-authenticated-requests
        response = authed_session.put(
            uri + path  # REST API endpoint
            , headers=headers  # Header; optional
            # non-form-encoded Payload for POST. Check rest API for format based on method.
            , json=payload
        )
        print(response)
        return response
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def getClassAndObjectDefinitions(verticalType, classId, objectId, classResourcePayload, objectResourcePayload, patient, url_path):
    try:
        classResourcePayload = __makeEventTicketClassResource(classId, patient)
        objectResourcePayload = __makeEventTicketObjectResource(
            classId, objectId, patient, url_path)
        return classResourcePayload, objectResourcePayload
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __makeEventTicketClassResource(classId, patient):
    try:
        # Define the resource representation of the Class
        # values should be from your DB/services; here we hardcode information
        textModulesData = [{
            "header": "STATUS", "body": 'Covid 19 | Level ' + patient["level"] + ' Verified ', "id": "status"
        }]
        certs = patient["certificates"]

        if len(certs) > 0:
            textModulesData.append({
                "header": "DOSE 1", "body": certs[0]["brand"], "id": "dose1"
            })
            textModulesData.append({
                "header": "LOT", "body": certs[0]["lot_no"], "id": "lot1"
            })
            textModulesData.append({
                "header": "DATE", "body": certs[0]["appointment_date"], "id": "date1"
            })
            textModulesData.append({
                "header": "CERT.#", "body": patient["certNo"], "id": "cert"
            })
            textModulesData.append({
                "header": "DATE VERIFIED", "body": patient["verfiedDate"], "id": "certdate"
            })
            if len(certs) > 1:
                textModulesData.append({
                    "header": "DOSE 2", "body": certs[1]["brand"], "id": "dose2"
                })
                textModulesData.append({
                    "header": "LOT", "body": certs[1]["lot_no"], "id": "lot2"
                })
                textModulesData.append({
                    "header": "DATE", "body": certs[1]["appointment_date"], "id": "date2"
                })

        payload = {}

        # below defines an event ticket class. For more properties, check:
        # https://developers.google.com/pay/passes/reference/v1/eventticketclass/insert
        # https://developers.google.com/pay/passes/guides/pass-verticals/event-tickets/design
        payload = {
            # required fields
            "id": classId,
            "issuerName": "Go Get Inc.",
            "eventName": {
                "defaultValue": {
                    "language": "en-US",
                    "value": patient["first_name"] + " " + patient["last_name"]
                }
            },
            "reviewStatus": "underReview",  # optional
            "textModulesData": textModulesData,
            "classTemplateInfo": {
                "cardTemplateOverride": {
                    "cardRowTemplateInfos": [{
                        "threeItems": {
                            "startItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['dose1']"
                                    }]
                                },
                                "secondValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['lot1']"
                                    }]
                                }
                            },
                            "middleItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['date1']"
                                    }]
                                }
                            },
                            "endItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['cert']"
                                    }]
                                }
                            },
                        }
                    }, {
                        "threeItems": {
                            "startItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['dose2']"
                                    }]
                                },
                                "secondValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['lot2']"
                                    }]
                                }
                            },
                            "middleItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['date2']"
                                    }]
                                }
                            },
                            "endItem": {
                                "firstValue": {
                                    "fields": [{
                                        "fieldPath": "class.textModulesData['certdate']"
                                    }]
                                }
                            },
                        }
                    }]
                }
            },
            "logo": {
                "kind": "walletobjects#image", "sourceUri": {
                    "kind": "walletobjects#uri",
                    "uri": "https://ggv-images.s3.us-east-2.amazonaws.com/GGV+android+wallet.png",
                    "description": "https://gogetdoc.com/vaxyes/"
                }
            }
        }
        return payload
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __makeEventTicketObjectResource(classId, objectId, patient, url_path):
    try:
        # Define the resource representation of the Object
        # values should be from your DB/services; here we hardcode information

        textModulesData = [{
            "header": "STATUS", "body": 'Covid 19 | Level ' + patient["level"] + ' Verified ', "id": "status"
        }]
        certs = patient["certificates"]

        if len(certs) > 0:
            textModulesData.append({
                "header": "DOSE 1", "body": certs[0]["brand"], "id": "dose1"
            })
            textModulesData.append({
                "header": "LOT", "body": certs[0]["lot_no"], "id": "lot1"
            })
            textModulesData.append({
                "header": "DATE", "body": certs[0]["appointment_date"], "id": "date1"
            })
            textModulesData.append({
                "header": "CERT.#", "body": patient["certNo"], "id": "cert"
            })
            textModulesData.append({
                "header": "DATE VERIFIED", "body": patient["verfiedDate"], "id": "certdate"
            })
            if len(certs) > 1:
                textModulesData.append({
                    "header": "DOSE 2", "body": certs[1]["brand"], "id": "dose2"
                })
                textModulesData.append({
                    "header": "LOT", "body": certs[1]["lot_no"], "id": "lot2"
                })
                textModulesData.append({
                    "header": "DATE", "body": certs[1]["appointment_date"], "id": "date2"
                })

        # below defines an event ticket object. For more properties, check:
        # https://developers.google.com/pay/passes/reference/v1/eventticketobject/insert
        # https://developers.google.com/pay/passes/guides/pass-verticals/event-tickets/design
        payload = {
            # required fields
            "id": objectId,
            "classId": classId,
            "state": "active",
            "barcode": {
                "kind": "walletobjects#barcode", "type": "QR_CODE", "value": "https://start.gogetdoc.com/vaxyes/verify?brand=vax&query=" + url_path,
                "alternateText": 'Covid 19 | Level ' + patient["level"] + ' Verified '
            },
            "textModulesData": textModulesData,
            "linksModuleData": {
                "uris": [{
                    "kind": "walletobjects#uri", "uri": "https://start.gogetdoc.com/login",
                    "description": "https://gogetdoc.com/vaxyes"
                }]
            }, "imageModulesData": [{
                "mainImage": {
                    "kind": "walletobjects#image", "sourceUri": {
                        "kind": "walletobjects#uri",
                        "uri": "https://ggv-images.s3.us-east-2.amazonaws.com/GGV+android+2.png",
                        "description": "https://gogetdoc.com/vaxyes/"
                    }
                }
            }],
            "hexBackgroundColor": "#2c1b4b"
        }
        print(json.dumps(payload))
        return payload
    except Exception as err:
        log_generic(
            type=c.ERROR,
            gpaypass_req={},
            function=whoami(),
            error=err
        )


def __generate_pk_pass(pkpass_req, patient, verification, url_path):
    try:
        cardInfo = Generic()
        certs = patient["certificates"]
        message = "https://start.gogetdoc.com/vaxyes/verify?brand=vax&query=" + url_path
        print("message", message)
        cardInfo.addHeaderField(
            'header', 'Covid 19 | Level ' + patient["level"] + ' Verified ', 'STATUS')
        cardInfo.addPrimaryField(
            key='Name', value=patient["first_name"] + " " + patient["last_name"], label='NAME')
        if len(certs) > 2:
            cardInfo.addSecondaryField(
                'InitialBrand', certs[1]["brand"], 'Initial Brand')
            cardInfo.addSecondaryField(
                'InitialDoseComplete', certs[1]["appointment_date"], 'Initial Dose Complete')
            cardInfo.addSecondaryField('CRT', patient["certNo"], 'CERT.#')
            cardInfo.addAuxiliaryField(
                'BoosterBrand', certs[2]["brand"], 'Booster Brand')
            cardInfo.addAuxiliaryField(
                'BoosterDate', certs[2]["appointment_date"], 'Booster Date')
            cardInfo.addAuxiliaryField(
                'DateVerified', patient["verfiedDate"], 'DATE VERIFIED')
        elif len(certs) > 1 and certs[0]["brand"] == "J & J":
            cardInfo.addSecondaryField(
                'InitialBrand', certs[0]["brand"], 'Initial Brand')
            cardInfo.addSecondaryField(
                'InitialDoseComplete', certs[0]["appointment_date"], 'Initial Dose Complete')
            cardInfo.addSecondaryField('CRT', patient["certNo"], 'CERT.#')
            cardInfo.addAuxiliaryField(
                'BoosterBrand', certs[1]["brand"], 'Booster Brand')
            cardInfo.addAuxiliaryField(
                'BoosterDate', certs[1]["appointment_date"], 'Booster Date')
            cardInfo.addAuxiliaryField(
                'DateVerified', patient["verfiedDate"], 'DATE VERIFIED')
        elif len(certs) > 0:
            cardInfo.addSecondaryField('DOSE1', certs[0]["brand"], 'DOSE 1')
            cardInfo.addSecondaryField(
                'LOT1', certs[0]["lot_no"], 'LOT NUMBER')
            cardInfo.addSecondaryField(
                'DATE1', certs[0]["appointment_date"], 'DATE')
            cardInfo.addSecondaryField('CRT', patient["certNo"], 'CERT.#')
            if len(certs) > 1 and certs[0]["brand"] != "J & J":
                cardInfo.addAuxiliaryField(
                    'DOSE2', certs[1]["brand"], 'DOSE 2')
                cardInfo.addAuxiliaryField(
                    'LOT2', certs[1]["lot_no"], 'LOT NUMBER')
                cardInfo.addAuxiliaryField(
                    'DATE2', certs[1]["appointment_date"], 'DATE')
            cardInfo.addAuxiliaryField(
                'DateVerified', patient["verfiedDate"], 'DATE VERIFIED')

        passfile = Pass(cardInfo,
                        passTypeIdentifier=pass_type_identifier,
                        organizationName=organization_name,
                        teamIdentifier=team_identifier)
        passfile.serialNumber = str(patient["patient_id"])
        passfile.description = "COVID 19 Vaccination card for " + \
                               patient["first_name"] + \
            " " + patient["last_name"]
        passfile.backgroundColor = "rgb(44, 27, 75)"
        passfile.foregroundColor = "rgb(255, 255, 255)"
        passfile.labelColor = "rgb(238, 191, 217)"
        passfile.barcode = Barcode(message=message, format="PKBarcodeFormatQR")
        passfile.webServiceURL = 'https://{}{}'.format(
            cfg('applewallet.host'), cfg('applewallet.path'))
        passfile.authenticationToken = url_path
        # print("LAMBDA_TASK_ROOT", os.environ['LAMBDA_TASK_ROOT'])
        # print("reading file from", os.environ['LAMBDA_TASK_ROOT'] + "/ggt/configs/images/Group 4GGV-4.png")
        # for root, dirs, files in os.walk("."):
        #     print(root)
        #     print(dirs)
        #     for filename in files:
        #         print(filename)
        passfile.addFile("icon.png", open(
            "./app/ggt/configs/images/Asset 4x.png", "rb"))
        print("./app/ggt/configs/images/Asset 4x.png was found")
        passfile.addFile("logo.png", open(
            "./app/ggt/configs/images/Asset 4x.png", "rb"))
        print("./app/ggt/configs/images/Asset 4x.png was found")
        print("pkpass temp path:",
              "/tmp/{}.{}".format(str(patient["patient_id"]), "pkpass"))
        _ = passfile.create(cert_pem,
                            key_pem,
                            wwdr_pem,
                            key_pem_password,
                            "/tmp/{}.{}".format(str(patient["patient_id"]), "pkpass"))
        print("file was created at:",
              "/tmp/{}.{}".format(str(patient["patient_id"]), "pkpass"))
        return _
    except Exception as err:
        log_generic(
            type=c.ERROR,
            pkpass_req=pkpass_req,
            function=whoami(),
            error=err
        )
        return False


def __is_open(patient_id):
    return is_open_patient(patient_id)


def __is_first_shot_taken(appointment_id):
    appointment = get_appointment(appointment_id)
    if appointment and appointment.status == c.APPOINTMENT_ACTION_END_VAX:
        return True
    else:
        return False


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
            if not update_slot_information(booking_req.timeslot_id, appointment.id):
                __assign_to_next_available_slot(
                    booking_req.timeslot, appointment.id)

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


def __generate_ggv_appointments(booking_req: GgtBooking, selected_services):
    if __is_dual_dose(selected_services):
        return __dual_shot_vaccinations(booking_req)
    else:
        return __single_shot_vaccinations(booking_req)


def __is_dual_dose(selected_services):
    if selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_1 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_1 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_NOVAVAX_1 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_AZ_1 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_AZ_2 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_NOVAVAX_2 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_2 or \
            selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_2:
        return True
    elif selected_services[0] == c.SERVICE_CODE_COVID_19_VACCINE_JNJ:
        return False


def __dual_shot_vaccinations(booking_req: GgtBooking):
    appointment_1: GgtAppointment = None
    appointment_2: GgtAppointment = None
    try:
        booking_req.slot_1 = get_slot_information(
            booking_req.appointmentOneTime, slot_type='vax')
        booking_req.slot_2 = get_slot_information(
            booking_req.appointmentTwoTime, slot_type='vax')
        if not (booking_req.slot_1 and booking_req.slot_2):
            raise ValueError('Invalid Slot')

        booking_req.timeslot = booking_req.slot_1
        appointment_1 = create_appointment(booking_req, ggv_slot=1)

        booking_req.timeslot = booking_req.slot_2
        appointment_2 = create_appointment(booking_req, ggv_slot=2)

        if appointment_1 and appointment_2:
            update_1 = update_slot_information(
                booking_req.appointmentOneTime, appointment_1.id, slot_type='vax')
            if not update_1:
                __assign_to_next_available_slot(
                    booking_req.slot_1, appointment_1.id, slot_type='vax')
            update_2 = update_slot_information(
                booking_req.appointmentTwoTime, appointment_2.id, slot_type='vax')
            if not update_2:
                __assign_to_next_available_slot(
                    booking_req.slot_2, appointment_2.id, slot_type='vax')

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


def __assign_to_next_available_slot(slot, appointment_id, slot_type='test'):
    next_available_slot = get_next_available_slot(
        slot.id, slot.location_id, slot_type)
    if next_available_slot:
        if book_slot(slot.id, appointment_id, slot_type):
            if update_appointment(appointment_id, next_available_slot['start_dt']):
                return next_available_slot
            else:
                return None
        else:
            return None
    else:
        return None


# TODO: consolidate __dual_shot_vaccinations and __single_shot_vaccinations in to a single function.
# For that we have to re-structure the request body.
def __single_shot_vaccinations(booking_req: GgtBooking):
    appointment: GgtAppointment = None
    try:
        booking_req.timeslot = get_slot_information(
            booking_req.appointmentOneTime, slot_type='vax')
        if not booking_req.timeslot:
            raise ValueError('Invalid Slot')
        appointment = create_appointment(booking_req)

        if appointment:
            log_generic(
                type=c.INFO,
                message="Updating slot information",
                function=whoami(),
                appointment_id=appointment.id,
                slot_id=booking_req.appointmentOneTime
            )
            update = update_slot_information(
                booking_req.appointmentOneTime, appointment.id, slot_type='vax')
            if not update:
                log_generic(
                    type=c.INFO,
                    message="Updating slot information FAILED",
                    function=whoami(),
                    appointment_id=appointment.id,
                    slot_id=booking_req.appointmentOneTime
                )
                __assign_to_next_available_slot(
                    booking_req.timeslot, appointment.id, slot_type='vax')
            log_generic(
                type=c.INFO,
                message="Updated slot information",
                function=whoami(),
                appointment_id=appointment.id,
                slot_id=booking_req.appointmentOneTime
            )

        else:
            raise ValueError('error_creating_appointment')

    except Exception as err:
        log_generic(
            type=c.ERROR,
            data=booking_req,
            function=whoami(),
            error=err
        )

    return appointment, None


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
        registration_complete_template = get_translated_message(
            'ggt_sms_registration_complete')(appointment.language)
        message = registration_complete_template.format(
            appointment.patient.first_name,
            appointment.date_text,
            appointment.location_text,
            cfg('base_url'),
            appointment.id,
            appointment.patient.dob.strftime('%Y%m%d')
        )

        international = is_international(appointment.patient.phone_number)
        result_1 = send_sms(appointment.patient.phone_number,
                            message.replace('\t', ''), international=international)

        followup_message = get_translated_message(
            'ggt_sms_followup_message')(appointment.language)
        result_2 = send_sms(appointment.patient.phone_number,
                            followup_message, international=international)

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


def __send_ggv_qrcode_sms(appointment: GgtAppointment, dose, out_of):
    try:
        message = "Hi {} " \
                  "\nYour COVID-19 Vaccine Dose {} of {} appointment is confirmed for {} at {}." \
                  "QR CODE TO GET VAX HERE: {}/appointment/{}/{}.  " \
                  "DO NOT ARRIVE EARLY OR LATE. You will not be allowed in the building or in the line more than 5 minutes early. If you are over 30 minutes late your appointment may be given to someone else to ensure vaccine is not wasted. Also make sure to bring an Acceptable ID, " \
                  "and QR code. Though not required, please bring your health insurance card as well." \
                  "\nReply Stop to cxl msgs".format(
                      appointment.patient.first_name,
                      dose,
                      out_of,
                      appointment.date_text,
                      appointment.location_text,
                      "https://start.gogetdoc.com",
                      appointment.id,
                      appointment.patient.dob.strftime('%Y%m%d')
                  )
        international = is_international(appointment.patient.phone_number)
        send_sms(appointment.patient.phone_number,
                 message.replace('\t', ''), international=international)

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


def send_ggv_certificate_level_1_sms(first_name, phone_number, level):
    message = ''
    if level == "1":
        message = """Hi {}, your VaxYes submission was successful - your level 1 digital card is available for immediate access through the secure online portal:\nhttps://start.gogetdoc.com/login \nYou'll receive an update when our team has verified your submission to level 2. Please allow extra time for processing due to volume.""".format(
            first_name,
        )
        promo_message = "Share this unique link with family & friends so they can get their digital cards too:\nhttps://www.gogetdoc.com/vaxyes"
    elif level == "booster":
        message = """Hi {}, Your booster submission was successful. Your updated VaxYes card with booster record is now available here:\nhttps://start.gogetdoc.com/login""".format(
            first_name,
        )
        promo_message = "Share this unique link with family & friends so they can get their digital cards too:\nhttps://www.gogetdoc.com/vaxyes"
    elif level == "2" or level == "3" or level == "4":
        message = """Hi {}, congrats! Your VaxYes submission has been updated to level {} verification. Your updated card is available here:\nhttps://start.gogetdoc.com/login""".format(
            first_name, level,
        )
        promo_message = "Share this unique link with family & friends so they can get their digital cards too:\nhttps://www.gogetdoc.com/vaxyes"
    if send_sms(phone_number, message.replace('\t', '')):
        log_generic(
            type=c.INFO,
            msg="SENT-GGV-VERIFICATION-SMS",
            level=level,
            first_name=first_name,
            phone_number=phone_number,
            message=message,
            function=whoami()
        )
    else:
        log_generic(
            type=c.ERROR,
            msg="SENT-GGV-VERIFICATION-SMS-FAILED",
            level=level,
            first_name=first_name,
            phone_number=phone_number,
            message=message,
            function=whoami()
        )

    if send_sms(phone_number, promo_message):
        log_generic(
            type=c.INFO,
            msg="SENT-GGV-PROMO-SMS",
            level=level,
            first_name=first_name,
            phone_number=phone_number,
            message=promo_message,
            function=whoami()
        )
    else:
        log_generic(
            type=c.ERROR,
            msg="SENT-GGV-PROMO-SMS-FAILED",
            level=level,
            first_name=first_name,
            phone_number=phone_number,
            message=promo_message,
            function=whoami()
        )


def __send_ggv_pre_registration_sms(first_name, phone_number):
    try:
        message = "Hi {} " \
                  "\nYou have successfully joined the waitlist for the COVID-19 vaccine.  " \
                  "We will notify you once  you have been cleared to book an appointment." \
                  "\nReply Stop to cxl msgs".format(first_name)
        international = is_international(phone_number)
        send_sms(phone_number,
                 message.replace('\t', ''), international=international)

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


def __send_qrcode_email(appointment: GgtAppointment, country: str = "US"):
    try:
        from_email = cfg('notifications.from_email')
        from_name = cfg('notifications.from_name')
        is_international = None if country == 'US' else 'MX'

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
            ),
            "hide_phone_number": country in cfg('notifications.hide_phone_number_in_countries'),

            "subject_test_scheduled": get_translated_message('ggt_1_subject_test_scheduled')(appointment.language),
            "thanks_scheduling": get_translated_message('ggt_1_thanks_scheduling')(appointment.language),
            "appointment_number": get_translated_message('ggt_1_appointment_number')(appointment.language),
            "test_scheduled": get_translated_message('ggt_1_test_scheduled')(appointment.language),
            "your_date_time": get_translated_message('ggt_1_your_date_time')(appointment.language),
            "please_arrive": get_translated_message('ggt_1_please_arrive')(appointment.language),
            "no_eating": get_translated_message('ggt_1_no_eating')(appointment.language),
            "even_if_better": get_translated_message('ggt_1_even_if_better')(appointment.language),
            "test_location": get_translated_message('ggt_1_test_location')(appointment.language),
            "test_date_time": get_translated_message('ggt_1_test_date_time')(appointment.language),
            "view_appointment": get_translated_message('ggt_1_view_appointment')(appointment.language),
            "about_us": get_translated_message('ggt_1_about_us')(appointment.language),
            "about_us_details": get_translated_message('ggt_1_about_us_details')(appointment.language),
            "start_test": get_translated_message('ggt_1_start_test')(appointment.language),
            "is_international": is_international
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
        from_email = cfg('notifications.from_email_ggd')
        from_name = cfg('notifications.from_name_ggd')

        template_vars = {
            "first_name": appointment.patient.first_name,
            "date_text": appointment.date_text,
            "location_text": appointment.location_text,
            "base_url": "https://start.gogetdoc.com",
            "appointment_id": appointment.id,
            "dob": appointment.patient.dob.strftime('%Y%m%d'),
            "appointment_url": '{}/appointment/{}/{}'.format(
                "https://start.gogetdoc.com",
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


def send_ggv_certificate_level_1_email(first_name, email, level, phone_number=None):
    try:
        from_email = cfg('notifications.from_email_ggd')
        from_name = cfg('notifications.from_name_ggd')

        template_vars = {
            "first_name": first_name
        }

        subject = "{}, The level {} verification of your vaccine card is complete.".format(
            first_name, level)
        if level == "BOOSTER":
            subject = "{}, Your VaxYes card now includes your booster record.".format(
                first_name)

        subject = render_from_string(
            subject,
            **template_vars
        )

        template_name = "GGV-2-COMPLETED-LEVEL-{}.html".format(level)
        html_content = render_template(
            template_name,
            **template_vars
        )

        sent_email = send_email(
            from_email,
            from_name,
            email,
            subject,
            html_content
        )

        if sent_email:
            log_generic(
                type=c.INFO,
                msg="SENT-GGV-VERIFICATION-EMAIL",
                level=level,
                first_name=first_name,
                email=email,
                phone_number=phone_number,
                template_name=template_name,
                function=whoami()
            )
        else:
            log_generic(
                type=c.ERROR,
                msg="SENT-GGV-VERIFICATION-EMAIL-FAILED",
                level=level,
                first_name=first_name,
                email=email,
                phone_number=phone_number,
                template_name=template_name,
                function=whoami()
            )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            email=email,
            function=whoami(),
            error=err
        )
        return False


def send_ggv_reject_email(first_name, email):
    from_email = cfg('notifications.from_email_ggd')
    from_name = cfg('notifications.from_name_ggd')

    template_vars = {
        "first_name": first_name
    }

    subject = "{}, Your VaxYes digital pass request was unable to be processed".format(
        first_name)

    subject = render_from_string(
        subject,
        **template_vars
    )

    template_name = "GGV-2-VAXYES-REJECT.html"
    html_content = render_template(
        template_name,
        **template_vars
    )

    sent_email = send_email(
        from_email,
        from_name,
        email,
        subject,
        html_content
    )

    if sent_email:
        log_generic(
            type=c.INFO,
            msg="SENT-GGV-REJECT-EMAIL",
            first_name=first_name,
            email=email,
            template_name=template_name,
            function=whoami()
        )
    else:
        log_generic(
            type=c.ERROR,
            msg="SENT-GGV-REJECT-EMAIL-FAILED",
            first_name=first_name,
            email=email,
            template_name=template_name,
            function=whoami()
        )


def __send_ggv_pre_registration_email(first_name, email):
    try:
        from_email = cfg('notifications.from_email_ggd')
        from_name = cfg('notifications.from_name_ggd')

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
        international = is_international(phone_number)
        return send_sms(phone_number, message, international=international)

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


def __get_country_from_location_services(service_selection_codes):
    if len(service_selection_codes) > 0:
        service_codes = {
            "COVID_19_TEST_MEXICO_ANTIGEN": "MX",
            "COVID_19_TEST_MEXICO": "MX"
        }
        return service_codes.get(service_selection_codes[0], "US")
    else:
        return "US"


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


def __is_phone_number_verified(token):
    if token.startswith("NOVERIFY"):
        return False
    else:
        return True


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
        patient.phone_number_verified = __is_phone_number_verified(
            booking_req.token)
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
        patient.country = booking_req.country
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


def __upload_test_result_image(result_image: str, appointment_id: int) -> bool:
    try:
        if result_image and len(result_image) > 0:
            if "," in result_image:
                base64string = result_image.split(",")[1]

            dest_file_name = '{}.png'.format(appointment_id)
            if upload_test_result_image_from_base64_string(base64string, dest_file_name):
                print('uploaded image: {}'.format(dest_file_name))
                return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            result_image=result_image,
            function=whoami(),
            error=err
        )

    return False


def upload_vax_card_image(result_image: str, patient_id: int, cert_id: str, user=None) -> bool:
    try:
        log_generic(
            type=c.INFO,
            msg="UPLOAD-IMAGE-REQUEST",
            patient_id=patient_id,
            cert_id=cert_id,
            admin=user,
            function=whoami()
        )
        if result_image.find("api.twilio.com") != -1:
            return upload_vax_card_image_from_twilio(
                result_image, '{}/{}.jpg'.format(patient_id, cert_id), cfg('aws.vax_certificate_bucket'))
        elif result_image and len(result_image) > 0:
            if "," in result_image:
                base64string = result_image.split(",")[1]
            dest_file_name = '{}/{}.jpg'.format(patient_id, cert_id)
            if upload_vax_card_image_from_base64_string(base64string, dest_file_name):
                log_generic(
                    type=c.INFO,
                    msg="UPLOAD-IMAGE-UPLOADED",
                    patient_id=patient_id,
                    cert_id=cert_id,
                    admin=user,
                    function=whoami()
                )
                return True
    except Exception as err:
        log_generic(
            type=c.ERROR,
            msg="UPLOAD-IMAGE-UPLOAD-ERROR",
            patient_id=patient_id,
            cert_id=cert_id,
            admin=user,
            function=whoami(),
            error=err
        )
    log_generic(
        type=c.INFO,
        msg="UPLOAD-IMAGE-UPLOAD-FAILED",
        patient_id=patient_id,
        cert_id=cert_id,
        admin=user,
        function=whoami()
    )
    return False


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
        wp_bill = ""  # te_wp_bill(appointment)

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
def __evaluate_upfront_payment(booking_req: GgtBooking):
    try:
        patient_upfront_payment = PatientUpfrontPayment()
        # Set initial value to false
        patient_upfront_payment.is_payment_required = False
        patient_upfront_payment.total_cost = 0
        patient_upfront_payment.billed_amount = 0

        # Get the list of location services
        location_services = booking_req.location_services
        # Get the currency
        currency = booking_req.currency
        # If no location services, return the empty payment object
        if not location_services:
            return patient_upfront_payment

        services_list = []
        # Get the list of service codes
        for service in location_services:
            services_list.append(service.service_code)

        # Get list of upfront payments
        service_payments = get_patient_upfront_payment(services_list, currency)

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
        patient_upfront_payment.currency = currency

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
            "billed_amount": int(appointment.billed_amount * 100),
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
        if (__add_wellpay_customer_insurance(
                wp_api_key, insurance_eligibility_request, customer_id)):
            eligibility = __add_wellpay_customer_insurance_eligibility(
                wp_api_key, insurance_eligibility_request, customer_id)
            if (eligibility['isEligible']):
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
        if (r.status_code == 200):
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
        if (r.status_code == 200):
            return {"isEligible": True, "benefits": r.json(), "error": None}
        elif (r.status_code == 404):
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
        prev_token = _patient.token

        existing_patient = None

        if not prev_token.startswith("NOVERIFY"):
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
            if not prev_token.startswith("NOVERIFY"):
                booking_req.result_token = unlock_patient_info_patients(
                    _patient.phone_number)
            else:
                booking_req.result_token = _patient.token
        else:
            if existing_patient['gender'] is None:
                update_patient_record(_patient, existing_patient['id'])
            patient_id = existing_patient['id']
            booking_req.result_token = unlock_patient_info_patients(
                existing_patient['phone_number'])
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
def __inject_payment_checkout_session(appointment: GgtAppointment, upfront_payment_info: PatientUpfrontPayment,
                                      booking_req: GgtBooking, selected_services):
    if not __should_charge_upfront_payment(upfront_payment_info):
        raise ValueError(
            'Checkout session is only be generated to upfront payments')

    payment_request = PaymentRequestBody()
    payment_request.line_items = __generate_payment_checkout_session_items(upfront_payment_info, booking_req,
                                                                           selected_services)
    payment_request.navigation = __generate_payment_checkout_session_navigation(
        appointment)
    payment_request.locale = __inject_locale(booking_req.language)
    payment_request.currency = upfront_payment_info.currency
    # Set the appointment id as the payment request id
    payment_request.id = appointment.id

    # Return the session object which contains session id
    return bp_create_checkout_session(payment_request)


def __generate_payment_checkout_session_items(upfront_payment_info: PatientUpfrontPayment, booking_req: GgtBooking,
                                              selected_services):
    line_items = []

    for service in selected_services:
        line_item = PaymentRequestLineItem()
        line_item.product_name = c.SERVICE_TO_NAME_MAP[
            service]  # get_translated_message('registration_charges')(booking_req.language)
        line_item.unit_price = upfront_payment_info.total_cost
        line_item.quantity = 1
        line_item.product_images = cfg('image_urls.payment')
        line_items.append(line_item)

    return line_items


def __generate_payment_checkout_session_navigation(appointment: GgtAppointment):
    navigation = PaymentRequestNavigation()
    navigation.success_url = cfg('payment.navigation.success_url').format(
        appointment.id, appointment.wp_receipt_token)
    navigation.cancel_url = cfg('payment.navigation.cancel_url')

    return navigation


# Stripe requires 'es-419' as the locale for Latin American countries
# Since in the context of GGT, es implies Latin America do the conversion here
def __inject_locale(language):
    return 'es-419' if language == 'es' else language


__failed_pass_ver_tracker: dict = {}
__failed_pass_ver_tracker_last_key_ts: int = 0


def __get_key_for_pass_ver_attempt_tracking(patient_id):
    cur_time = datetime.now()
    five_min_rounded_time = cur_time - timedelta(minutes=cur_time.minute % 5,
                                                 seconds=cur_time.second, microseconds=cur_time.microsecond)
    ticks = math.floor(
        (five_min_rounded_time - datetime(2021, 1, 1)).total_seconds() / 60)

    return {'ts': ticks, 'val': "{0}-{1}".format(patient_id, ticks)}


def __clear_failed_pass_ver_tracker_if_expired(ts):
    global __failed_pass_ver_tracker, __failed_pass_ver_tracker_last_key_ts

    if (ts != __failed_pass_ver_tracker_last_key_ts):
        __failed_pass_ver_tracker.clear()


def __register_pass_verification_fail(patient_id):
    global __failed_pass_ver_tracker, __failed_pass_ver_tracker_last_key_ts

    key = __get_key_for_pass_ver_attempt_tracking(patient_id)
    __clear_failed_pass_ver_tracker_if_expired(key['ts'])
    __failed_pass_ver_tracker_last_key_ts = key['ts']

    if (len(__failed_pass_ver_tracker.keys()) >= 5000):
        return

    if (key['val'] in __failed_pass_ver_tracker):
        __failed_pass_ver_tracker[key['val']
                                  ] = __failed_pass_ver_tracker[key['val']] + 1
    else:
        __failed_pass_ver_tracker[key['val']] = 1
    return


def __is_pass_verification_blocked_for(patient_id):
    global __failed_pass_ver_tracker, __failed_pass_ver_tracker_last_key_ts

    key = __get_key_for_pass_ver_attempt_tracking(patient_id)
    __clear_failed_pass_ver_tracker_if_expired(key['ts'])

    if (key['val'] in __failed_pass_ver_tracker):
        return __failed_pass_ver_tracker[key['val']] > 5
    return False
