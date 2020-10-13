import requests

from ggt.lib.utils import (
    get_config_val,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic
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
            log_generic(type="error",
                        phone_number=phone_number,
                        otp_code=otp_code,
                        token=token,
                        function='initiate_verification_flow',
                        error='NO OTP / Unable to create a Pending Record for Phone Verification')
            return False

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
                log_generic(type="info", phone_number=phone_number, otp_code=otp_code, token=token, activation_url=activation_url,
                            sms_message=message, function='initiate_verification_flow', info='OTP SMS Sent')
                return True
            else:
                log_generic(type="error", phone_number=phone_number, otp_code=otp_code, token=token, activation_url=activation_url,
                            sms_message=message, function='initiate_verification_flow', error='Unable to send OTP SMS')
                return False

    except Exception as err:
        log_generic(type="error",
                    phone_number=phone_number,
                    function='bp_initiate_verification_flow',
                    error=err)
        return False


def bp_validate_phone_number(phone_number, otp):
    # Override OTP under special circumstances
    override_otp_code = get_config_val('pfe.signup.override_otp_code')
    if otp == override_otp_code:
        return {
            "token": "NOVERIFY{}".format(generate_token()[8:])
        }

    row = get_signup_record_by_phone_otp(phone_number, otp)
    token = row['token']

    if token is None:
        log_generic(
            type="error",
            phone_number=phone_number,
            otp=otp,
            token=token,
            function='validate_phone_number',
            error='empty token'
        )
        return False

    else:
        log_generic(
            type="info",
            phone_number=phone_number,
            otp=otp,
            token=token,
            function='validate_phone_number'
        )
        return {
            "token": token
        }


def bp_finalize_booking(data):
    try:
        if not __is_valid_token(data['token']):
            raise ValueError('Invalid Token')

        data['patient_id'] = __create_patient_record(data)
        if not data['patient_id']:
            raise ValueError('Invalid Patient ID')

        data['patient_questionnaire_id'] = create_patient_questionnaire(data)
        if not data['patient_questionnaire_id']:
            raise ValueError('Invalid Patient Questionnaire ID')

        # for every registration, create a wellpay user
        wp_customer_info_id = __create_wp_customer(data)

        payment_required, total_cost, billed_amount = __upfront_payment(
            data['group_code'], data['location']
        )

        # generate appointment
        appointment = generate_appointment(
            data['time_slot'],
            data['patient_id'],
            data['patient_questionnaire_id'],
            data['group_code'],
            wp_customer_info_id,
            total_cost/100,
            billed_amount/100
        )

        appointment_id = appointment['appointment_id']

        if not appointment_id:
            raise ValueError('Invalid Appointment info')

        wp_bill_url = ''
        if payment_required:
            wp_bill_url = __inject_payment_flow(
                wp_customer_info_id, billed_amount, appointment_id, total_cost)

        else:  # payment not required, confirm the appointment and notify
            update_appointment_with_confirmed_scheduled(appointment_id)
            __send_qrcode_sms(
                data['first_name'],
                appointment['date_text'],
                appointment['location_text'],
                data['phone_number'],
                appointment_id,
                data['dob']
            )

            return __finalize_booking_response(
                appointment['date_text'],
                appointment['location_text'],
                appointment_id,
                billed_amount,
                total_cost,
                wp_bill_url
            )

    except Exception as err:
        log_generic(
            type="error",
            data=data,
            function='bp_finalize_booking',
            error=err)

    return False


def __inject_payment_flow(wp_customer_info_id, billed_amount, appointment_id, total_cost):
    try:
        if wp_customer_info_id is None:
            raise ValueError('Invalid Customer ID')

        else:
            wp_bill = __create_wp_bill(
                wp_customer_info_id,
                billed_amount,
                appointment_id
            )

            if update_appointment_with_receipt_token(
                    wp_bill['receipt_token'],
                    wp_customer_info_id,
                    appointment_id):
                return wp_bill['url']

            else:
                raise ValueError('Appointment update failed')

    except Exception as err:
        log_generic(
            type="error",
            wp_customer_info_id=wp_customer_info_id,
            billed_amount=billed_amount,
            appointment_id=appointment_id,
            total_cost=total_cost,
            function='__inject_payment_flow',
            error=err)
        return None


def __finalize_booking_response(date, location, appointment_id, total_balance='', total_cost='', payment_url=''):
    return {
        'date': date,
        'location': location,
        'appointment_id': appointment_id,
        'total_balance': total_balance,
        'total_cost': total_cost,
        'payment_url': payment_url
    }

# Returns payment_required, total_cost, billed_amount


def __upfront_payment(group_code, location):
    return False, 0, 0  # business decision to make all testing free 08/06/2020

    total_cost = 17500
    billed_amount = 7000

    if group_code == 'QTCORP' or group_code == 'BMSC' or group_code == 'EATZ' or group_code == 'LOWES' or group_code == 'LOWE\'S' or group_code == 'WICHITA':
        return False, 0, 0
    if location == 11 or location == 7 or location == 18 or location == 28 or location == 24 or location == 26 or location == 9 or location == 26 or location == 34 or location == 36:
        return False, 0, 0
    else:
        return True, total_cost, billed_amount


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
            type="error",
            data=data,
            function='__create_wp_customer',
            error='Customer creation failed',
            error_details=err
        )
        return None


def __create_wp_bill(customer_info_id, billed_amount, appointment_id):
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
            type="error",
            customer_info_id=customer_info_id,
            billed_amount=billed_amount,
            appointment_id=appointment_id,
            function='__create_wp_bill',
            error=err
        )
        return None


def bp_finalize_payment(appointment_id, wp_receipt_token):
    try:
        appointment = get_appointment(appointment_id)
        if appointment['wp_receipt_token'] == wp_receipt_token:
            update_appointment_with_confirmed_scheduled(appointment_id)
            location = "{}, {} {}  {}".format(appointment['addr1'],
                                              appointment['city'],
                                              appointment['st'],
                                              appointment['zip'])
            date = str(appointment["scheduled_dt"].strftime(
                "%a, %-d %b %Y @ %-I:%M %p"))
            result = __send_qrcode_sms(appointment['first_name'], date, location,
                                       appointment['phone_number'], appointment_id, str(appointment['dob']))
            return True

    except Exception as err:
        log_generic(
            type="error",
            appointment_id=appointment_id,
            wp_receipt_token=wp_receipt_token,
            function='bp_finalize_payment',
            error=err
        )

    return False


'''
def handle_action_schedule_and_print(phone_number, appointment_id):
    return True #TODO: REVISIT this and move to admin section maybe....
    
    send_sms = True
    try:
        p1 = get_config_val('pfe.signup.special_phone_1')
        p2 = get_config_val('pfe.signup.special_phone_2')
        p3 = get_config_val('pfe.signup.special_phone_3')
        p4 = get_config_val('pfe.signup.special_phone_4')

        if phone_number == p1:
            appointment_begin_test(appointment_id, 2)
            update_appointment_with_test_start(appointment_id)
            send_sms=False
        if phone_number == p2:
            appointment_begin_test(appointment_id, 3)
            send_sms=False
        if phone_number == p3:
            appointment_begin_test(appointment_id, 2)
            send_sms=False
        if phone_number == p4:
            appointment_begin_test(appointment_id, 3)
            send_sms=False
    except Exception as err:
        log_generic(type="error", phone_number=phone_number, appointment_id=appointment_id, function='handle_action_schedule_and_print', error=err)
    
    return send_sms
'''


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
        log_generic(type="error", token=token,
                    function='lookup_test_result_by_token', error=err)

    return False


def generate_appointment(slot_id, patient_id, patient_questionnaire_id, group_code, wp_customer_info_id, total_cost, billed_amount):
    # TODO: Prevent from looking up slots that are already assigned to an appointment
    # TODO, doesn't check if it's already booked
    slot = get_slot_information(slot_id)
    if not slot:
        log_generic(type="error",
                    patient_id=patient_id,
                    patient_questionnaire_id=patient_questionnaire_id,
                    group_code=group_code,
                    function='generate_appointment',
                    error='error_getting_slot_info')
        return False

    location = get_location_by_id(slot['location_id'])
    if not location:
        log_generic(type="error",
                    patient_id=patient_id,
                    patient_questionnaire_id=patient_questionnaire_id,
                    group_code=group_code,
                    slot=slot,
                    function='generate_appointment',
                    error='error_getting_location')
        return False

    appointment_id = create_appointment(
        slot['start_dt'],
        slot['location_id'],
        patient_id,
        patient_questionnaire_id,
        group_code,
        wp_customer_info_id,
        total_cost,
        billed_amount)

    if appointment_id:
        # TODO: update = __update_slot_information(slot_id, appointment_id)

        date_text = slot['start_dt'].strftime("%a, %-d %b %Y @ %-I:%M %p")
        # e.g. 6155 Sports Village Rd, Frisco, TX 75033
        location_text = "{}, {} {}  {}".format(location['addr1'],
                                               location['city'],
                                               location['st'],
                                               location['zip'])

        log_generic(type="info",
                    patient_id=patient_id,
                    patient_questionnaire_id=patient_questionnaire_id,
                    group_code=group_code,
                    slot=slot,
                    location=location,
                    function='generate_appointment',
                    info='appointment_created',
                    appointment_id=appointment_id,
                    appointment_dt=date_text,
                    appointment_location=location_text)

        return {
            'is_success': True,
            'appointment_id': appointment_id,
            'date_text': date_text,
            'location_text': location_text
        }

    else:
        log_generic(type="error",
                    patient_id=patient_id,
                    patient_questionnaire_id=patient_questionnaire_id,
                    group_code=group_code,
                    slot=slot,
                    function='generate_appointment',
                    error='error_creating_appointment')
        return False


########################################################################################################
# [Protected] functions
########################################################################################################

def __create_pending_entry(phone_number):
    try:
        override, otp_code = __override_random_otp(phone_number)

        if not override:
            otp_code = generate_otp()

        token = generate_token()

        log_generic(type="info", phone_number=phone_number,
                    otp_code=otp_code, token=token, function='__create_pending_entry')
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
        log_generic(type="error", phone_number=phone_number,
                    function='__create_pending_entry', error=err)
        return None, None


def __send_qrcode_sms(first_name, date, location, phone_number, appointment_id, dob):
    # message = "Click here for your Appointment Details\n {}/appointment/{}/{}".format(
    #     get_config_val('base_url'), str(appointment_id).rjust(6, '0'), dob.replace('-', ''))
    message = "Hi {}, thank you for completing your registration at GoGetTested.com. Your appointment is confirmed for {} at {}. Your appointment details can be found here\n {}/appointment/{}/{}".format(
        first_name, date, location, get_config_val('base_url'), str(appointment_id).rjust(6, '0'), dob.replace('-', ''))
    log_generic(
        type="info",
        phone_number=phone_number,
        appointment_id=appointment_id,
        message=message,
        function='__send_qrcode_sms'
    )
    next_message = "Please make sure to bring and show this QR code {}/appointment/{}/{}, and Acceptable ID when you arrive at the test. We will scan the QR code to check you in for testing. Please no eating or drinking at least 15 minutes prior to testing as this may impact your test results.".format(
        get_config_val('base_url'), str(appointment_id).rjust(6, '0'), dob.replace('-', ''))
    send_sms(phone_number, message)
    return send_sms(phone_number, next_message)


def __send_otp_sms(phone_number, message):
    log_generic(
        type="info",
        phone_number=phone_number,
        message=message,
        function='__send_otp_sms'
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


def __create_patient_record(data):
    return create_patient_record(
        token=data["token"],
        phone_number=validate_phone_number_format(data["phone_number"]),
        first_name=data["first_name"],
        middle_name=data["middle_name"],
        last_name=data["last_name"],
        gender=data["gender"],
        phone_number_verified='1',
        addr1=data["address"],
        city=data["city"],
        zip=data["zip"],
        email=data["email"],
        dob=data["dob"],
        height_ft=data["height"],
        weight_lb=data["weight"],
        ethnicity=data["ethnicity"],
        race=data["race"],
        st=data["st"]
    )

########################################################################################################
# [Protected] functions
########################################################################################################
