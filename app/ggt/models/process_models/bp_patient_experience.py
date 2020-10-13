import requests
from requests.auth import HTTPBasicAuth

from ggt.lib.utils import (
    get_config_val,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic,
    whoami
)

from ggt.lib.sms import (send_sms)

from ggt.models.data_models.signups import (
    get_ui_screen_flow_seq,
    create_pending_signup_record,
    get_signup_record_by_phone_otp,
    get_signup_record_by_token
)

from ggt.models.data_models.patients import (
    create_patient_record,
    get_patient_by_token
)

from ggt.models.data_models.questionnaires import (
    create_patient_questionnaire
)

from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_confirmed_scheduled,
    create_appointment,
    update_appointment_with_receipt_token
)

from ggt.models.data_models.locations import (
    get_location_by_id
)

from ggt.models.data_models.schedules import (
    get_slot_information
)

from ggt.models.data_models.test_results import (
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
    GgtAppointment
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.storage import get_temporary_lab_report_url
########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_screen_flow_seq(group_code):
    screen_seq = get_ui_screen_flow_seq(group_code)
    if screen_seq:
        validations = {}
        screens = []

        if screen_seq['screen_seq']:
            screens = screen_seq['screen_seq'].split(',')

        if screen_seq['required_screens']:
            required_screens = screen_seq['required_screens'].split(',')
            for required_screen in required_screens:
                validations[required_screen] = {
                    "required": True
                }

        if screen_seq['optional_screens']:
            optional_screens = screen_seq['optional_screens'].split(',')
            for optional_screen in optional_screens:
                validations[optional_screen] = {
                    "required": False
                }

        return {
            "screens": screens,
            "validation": validations
        }

    else:
        return None


def bp_initiate_verification_flow(phone_number, with_otp=True):
    # Create a temp record until phone number is validated
    try:
        phone_number = validate_phone_number_format(phone_number)
        otp_code, token = __create_pending_entry(phone_number)

        if otp_code is None:
            raise ValueError(
                'NO OTP / Unable to create a Pending Record for Phone Verification')

        else:
            activation_url = "{}/{}/{}".format(
                get_config_val('base_url'), phone_number, token)

            if with_otp:
                message = "Enter the Code: {}\nOr click {}".format(
                    otp_code, activation_url)
            else:
                message = "Thank you. You're now ready to schedule your GoGetTested COVID-19 test. To start follow this {} to schedule your test".format(
                    activation_url)

            # send SMS
            if __send_otp_sms(phone_number, message):
                log_generic(
                    type=INFO,
                    phone_number=phone_number,
                    otp_code=otp_code,
                    token=token,
                    activation_url=activation_url,
                    sms_message=message,
                    function=whoami(),
                    info='OTP SMS Sent'
                )
                return True

            else:
                raise ValueError('Unable to send OTP SMS')

    except Exception as err:
        log_generic(
            type=ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
    return False


def bp_validate_phone_number(phone_number, otp):
    try:
        # Override OTP under special circumstances
        override_otp_code = get_config_val('pfe.signup.override_otp_code')
        if otp == override_otp_code:
            token = "NOVERIFY{}".format(generate_token()[8:])
        else:
            token = get_signup_record_by_phone_otp(phone_number, otp)

        if token is None:
            raise ValueError('Invalid Token')

        log_generic(
            type=INFO,
            phone_number=phone_number,
            otp=otp,
            token=token,
            function=whoami()
        )

        return {
            "token": token
        }

    except Exception as err:
        log_generic(
            type=ERROR,
            phone_number=phone_number,
            otp=otp,
            function=whoami(),
            error=err
        )

    return False


# def bp_finalize_booking(booking_req: GgtBooking):
#     appointment: GgtAppointment = None
#     try:
#         if not __is_valid_token(booking_req.token):
#             raise ValueError('Invalid Token')

#         # create patient
#         _patient = __extract_patient_from_booking_req(booking_req)
#         booking_req.patient_id = create_patient_record(_patient)
#         if not booking_req.patient_id:
#             raise ValueError('Invalid Patient ID')

#         # create questionnaire
#         booking_req.patient_questionnaire_id = create_patient_questionnaire(
#             booking_req)
#         if not booking_req.patient_questionnaire_id:
#             raise ValueError('Invalid Patient Questionnaire ID')

#         # determine if payment is required, if so, get billing info
#         upfront_payment_info = __evaluate_upfront_payment(booking_req)
#         booking_req.total_cost = upfront_payment_info.total_cost
#         booking_req.billed_amount = upfront_payment_info.billed_amount

#         # generate appointment/booking
#         appointment = __generate_appointment(booking_req)
#         if not appointment:
#             raise ValueError('Invalid Appointment info')

#         # wp_bill_url = ''
#         if payment_required:
#             wp_bill_url = __inject_payment_flow(
#                 wp_customer_info_id, billed_amount, appointment_id, total_cost)

#         else:  # payment not required, confirm the appointment and notify
#             update_appointment_with_confirmed_scheduled(appointment_id)
#             __send_qrcode_sms(
#                 data['first_name'],
#                 appointment['date_text'],
#                 appointment['location_text'],
#                 data['phone_number'],
#                 appointment_id,
#                 data['dob']
#             )

#             return __finalize_booking_response(
#                 appointment['date_text'],
#                 appointment['location_text'],
#                 appointment_id,
#                 billed_amount,
#                 total_cost,
#                 wp_bill_url
#             )

#     except Exception as err:
#         log_generic(
#             type=ERROR,
#             data=booking_req,
#             function=whoami(),
#             error=err
#         )

#     return appointment

def bp_finalize_booking(booking_req: GgtBooking):
    appointment: GgtAppointment = None
    try:
        if not __is_valid_token(booking_req.token):
            raise ValueError('Invalid Token')

        # create patient
        _patient = __extract_patient_from_booking_req(booking_req)
        booking_req.patient_id = create_patient_record(_patient)
        if not booking_req.patient_id:
            raise ValueError('Invalid Patient ID')

        # create questionnaire
        booking_req.patient_questionnaire_id = create_patient_questionnaire(
            booking_req)
        if not booking_req.patient_questionnaire_id:
            raise ValueError('Invalid Patient Questionnaire ID')

        # determine if payment is required, if so, get billing info
        upfront_payment_info = __evaluate_upfront_payment(booking_req)
        booking_req.total_cost = upfront_payment_info.total_cost
        booking_req.billed_amount = upfront_payment_info.billed_amount

        # generate appointment/booking
        appointment = __generate_appointment(booking_req)
        if not appointment:
            raise ValueError('Invalid Appointment info')

        # if a payment is required, generate a payment link
        appointment.payment_url = ''
        if upfront_payment_info.is_payment_required:
            appointment.payment_url = __inject_payment_flow(appointment)
        else:  
            # payment not required, confirm the appointment and notify
            update_appointment_with_confirmed_scheduled(appointment.id)
            __send_qrcode_sms(appointment)

    except Exception as err:
        log_generic(
            type=ERROR,
            data=booking_req,
            function=whoami(),
            error=err
        )

    return appointment


def __create_wellpay_create_bill_request(booking_req: GgtBooking, appointment_id: int):
    r = WellpayCreateBillRequest()
    r.first_name = booking_req.first_name
    r.last_name = booking_req.last_name
    r.phone = booking_req.phone_number
    r.email = booking_req.email
    r.date_of_birth = booking_req.dob
    r.street_address = booking_req.address
    r.city = booking_req.city
    r.state = booking_req.st
    r.zip_code = booking_req.zip
    r.external_account_id = appointment_id
    r.autopay = False
    r.billed_amount = booking_req.tot


def __inject_payment_flow(appointment: GgtAppointment):
    try:
        wp_bill = __create_wp_bill(appointment)

        appointment.wp_receipt_token = wp_bill.receipt_token
        appointment.wp_customer_info_id = wp_bill.customer_id
        appointment.payment_url = wp_bill.url

        if update_appointment_with_receipt_token(appointment):
            return wp_bill.url

        else:
            raise ValueError('Appointment update failed')

    except Exception as err:
        log_generic(
            type=ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )
    
    return None

'''
def __finalize_booking_response(date, location, appointment_id, total_balance='', total_cost='', payment_url=''):
    return {
        'date': date,
        'location': location,
        'appointment_id': appointment_id,
        'total_balance': total_balance,
        'total_cost': total_cost,
        'payment_url': payment_url
    }
'''
# Returns payment_required, total_cost, billed_amount


def __evaluate_upfront_payment(booking_req):
    r = UpfrontPaymemtResponse()

    if booking_req.service_flu_shot:
        r.is_payment_required = True
        r.total_cost = 3000
        r.billed_amount = 3000
    else:
        # business decision to make all testing free 08/06/2020
        r.is_payment_required = False
        r.total_cost = 0
        r.billed_amount = 0

    return r

'''
def __create_wp_customer(data):
    try:
        url = "{}/customers".format(get_config_val('vendors.wellpay.endpoint'))
        headers = {
            'Authorization': 'Bearer {}'.format(get_config_val('vendors.wellpay.auth_token')),
            'Content-Type': 'application/json'
        }
        payload = {
            "date_of_birth": data["dob"],
            "email": data["email"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone": data["phone_number"],
            "street_address": data["address"],
            "city": data["city"],
            "state": data["st"],
            "zip_code": data["zip"]
        }
        r = requests.post(url, headers=headers, json=payload)
        customer_info_id = r.json()[0]['customer_info_id']

        return customer_info_id

    except Exception as err:
        log_generic(
            type=ERROR,
            data=data,
            function=whoami(),
            error='Customer creation failed',
            error_details=err
        )
        return None
'''
'''
def __create_wp_bill_old(customer_info_id, billed_amount, appointment_id):
    try:
        url = "{}/bills".format(get_config_val('vendors.wellpay.endpoint'))
        headers = {
            'Authorization': 'Bearer {}'.format(get_config_val('vendors.wellpay.auth_token')),
            'Content-Type': 'application/json'
        }
        payload = {
            "customer_info_id": customer_info_id,
            "staged": "true",
            "billed_amount": billed_amount,
            "external_bill_id": appointment_id,
            "onSuccess": "{}/appointment/{}/pay/success".format(get_config_val('base_url'), appointment_id),
            "onFailure": "{}/appointment/{}/pay/error".format(get_config_val('base_url'), appointment_id),
        }
        r = requests.post(url, headers=headers, json=payload)
        return r.json()

    except Exception as err:
        log_generic(
            type=ERROR,
            customer_info_id=customer_info_id,
            billed_amount=billed_amount,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )
        return None
'''

def __create_wp_bill(appointment: GgtAppointment):
    res: WellpayCreateBillResponse = WellpayCreateBillResponse()
    try:
        wp_api_key, wp_refresh_token = __get_wp_api_tokens()

        base_url = get_config_val('vendors.wellpay.endpoint')
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
            #"adddress_complement": ''+appointment.patient.addr2,
            "city": appointment.patient.city,
            "state": appointment.patient.st,
            "zip_code": appointment.patient.zip,
            "external_account_id": appointment.id,
            "autopay": False,
            "external_bill_id": appointment.id,
            "billed_amount": int(appointment.billed_amount*100),
            "service_date": appointment.scheduled_dt.strftime('%Y-%m-%d'),

            "onSuccess": "{}/appointment/{}/pay/success".format(get_config_val('base_url'), appointment.id),
            "onFailure": "{}/appointment/{}/pay/error".format(get_config_val('base_url'), appointment.id)
        }

        r = requests.post(url, headers=headers, json=payload)
        response = r.json()
        
        res.url = response['url']
        res.receipt_token = response['receipt_token']

    except Exception as err:
        log_generic(
            type=ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )
    
    return res


def __get_wp_api_tokens():
    base_url = get_config_val('vendors.wellpay.endpoint')
    auth_user = get_config_val('vendors.wellpay.auth_user')
    auth_password = get_config_val('vendors.wellpay.auth_password')

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
            type=ERROR,
            function=whoami(),
            error=err
        )

    return wp_api_key, wp_refresh_token


def bp_finalize_payment(appointment_id, wp_receipt_token):
    try:
        appointment = get_appointment(appointment_id)
        if appointment['wp_receipt_token'] == wp_receipt_token:
            update_appointment_with_confirmed_scheduled(appointment_id)
            result = __send_qrcode_sms(appointment)
            return True

    except Exception as err:
        log_generic(
            type=ERROR,
            appointment_id=appointment_id,
            wp_receipt_token=wp_receipt_token,
            function=whoami(),
            error=err
        )

    return False


def bp_get_test_result(token, dob):
    try:
        lab_result = get_test_result_by_token(token)

        if lab_result:
            patient_dob = lab_result['dob'].strftime("%m%d%Y")
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

            if dob == patient_dob:
                return {
                    "result": result,
                    "lab_report_url": url
                }

    except Exception as err:
        log_generic(
            type=ERROR,
            token=token,
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
def __generate_appointment(booking_req: GgtBooking):
    appointment: GgtAppointment = None
    try:
        booking_req.timeslot = get_slot_information(booking_req.timeslot_id)
        if not booking_req.timeslot:
            raise ValueError('Invalid Slot')

        appointment = create_appointment(booking_req)

        if appointment:
            log_generic(
                type=INFO,
                booking_req=booking_req,
                appointment=appointment,
                function=whoami(),
                info='appointment_created'
            )

        else:
            raise ValueError('error_creating_appointment')

    except Exception as err:
        log_generic(
            type=ERROR,
            data=booking_req,
            function=whoami(),
            error=err
        )
    
    return appointment

def __create_pending_entry(phone_number):
    try:
        override, otp_code = __override_random_otp(phone_number)

        if not override:
            otp_code = generate_otp()

        token = generate_token()

        log_generic(
            type=INFO,
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
            type=ERROR, 
            phone_number=phone_number,
            function=whoami(), 
            error=err
        )
        return None, None


def __send_qrcode_sms(appointment: GgtAppointment):
    # message = "Click here for your Appointment Details\n {}/appointment/{}/{}".format(
    #     get_config_val('base_url'), str(appointment_id).rjust(6, '0'), dob.replace('-', ''))
    message = "Hi {}, thank you for completing your registration at GoGetTested.com. Your appointment is confirmed for {} at {}. Your appointment details can be found here\n {}/appointment/{}/{}".format(
        appointment.patient.first_name, appointment.date_text, appointment.location_text, get_config_val('base_url'), str(appointment.id).rjust(6, '0'), appointment.patient.dob.replace('-', ''))
    log_generic(
        type=INFO,
        appointment=appointment,
        phone_number=appointment.patient.phone_number,
        message=message,
        function=whoami()
    )
    next_message = "Please make sure to bring and show this QR code {}/appointment/{}/{}, and Acceptable ID when you arrive at the test. We will scan the QR code to check you in for testing. Please no eating or drinking at least 15 minutes prior to testing as this may impact your test results.".format(
        get_config_val('base_url'), str(appointment.id).rjust(6, '0'), appointment.patient.dob.replace('-', ''))
    send_sms(appointment.patient.phone_number, message)
    return send_sms(appointment.patient.phone_number, next_message)

def __send_otp_sms(phone_number, message):
    log_generic(
        type=INFO,
        phone_number=phone_number,
        message=message,
        function=whoami()
    )
    return send_sms(phone_number, message)


def __override_random_otp(phone_number):
    p1 = get_config_val('pfe.signup.special_phone_1')
    p2 = get_config_val('pfe.signup.special_phone_2')
    override_otp_code = get_config_val('pfe.signup.override_otp_code')

    if phone_number == p1 or phone_number == p2:
        return True, override_otp_code
    else:
        return False, None


def __is_valid_token(token):
    return True  # to be chnaged
    # Duplicate Token
    if get_patient_by_token(token):
        return False

    # Allows overriding phone number validation
    if token.startswith("NOVERIFY"):
        return True
    else:
        return get_signup_record_by_token(token)


def __extract_patient_from_booking_req(booking_req: GgtBooking):
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


########################################################################################################
# [Protected] functions
########################################################################################################



class UpfrontPaymemtResponse():
    is_payment_required: bool = None
    total_cost: int = None
    billed_amount: int = None