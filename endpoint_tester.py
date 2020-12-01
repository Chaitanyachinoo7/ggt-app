#!/usr/bin/env python
import sys
import os
import requests
import json
from datetime import datetime
import dateutil.parser
import logging

# logging.basicConfig(level=logging.DEBUG)

if sys.version_info[0] < 3:
    raise Exception('Requires Python 3+')

############## CONFIG ##################
endpoint = 'http://localhost:8888/api'
use_auth = False
username = ''
password = ''


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def print_header(message):
    print('{.HEADER}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok1(message):
    print('{.OKGREEN}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_ok2(message):
    print('{.OKBLUE}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_warning(message):
    print('{.WARNING}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_error(message):
    print('{.FAIL}{}{.ENDC}'.format(bcolors, message, bcolors))


def print_progress_bar_message(message):
    print('{.OKBLUE}{}{.ENDC}\r'.format(bcolors, message, bcolors), end="")


def invoke_get(resource_path):
    print_ok1('Testing {}'.format(resource_path))
    try:
        url = '{}{}'.format(endpoint, resource_path)
        r = requests.get(
            url,
            auth=(username, password)
        )
        return r

    except Exception:
        print_error('No response for {}'.format(resource_path))
        return None


def invoke_post(payload):
    url = '{}{}'.format(endpoint, resource_path)
    r = requests.post(
        url,
        auth=(username, password),
        data=payload
    )


def is_valid_status_code(response, expected_code):
    try:
        if response.status_code == expected_code:
            print_ok2('OK - {}'.format(response.status_code))
            return True

    except Exception:
        pass

    print_error('FAIL - Status code')
    return False


'''
# 1. Test if response body contains sth.
def response_contains_txt():
    if response.text:
        return True

# 2. Handle error if deserialization fails (because of no text or bad format)
def is_json_deserializable(response):
    try:
        responses = response.json()
        return True

    except ValueError:
        return False

# 3. check that .json() did NOT return an empty dict
def is_not_empty_response():
    if responses:
    # ...



# 4. safeguard against malformed data
def is_valid_structure():
    try:
        data = responses[some_key][some_index][...][...]

    except (IndexError, KeyError, TypeError):
        # data does not have the inner structure you expect

# 5. check if data is actually something useful (truthy in this example)
def is_valid_data():
    if data:
        # ...
    else:
        # data is falsy ([], {}, None, 0, '', ...)
'''


def test_get_locations_1():
    res = invoke_get('/get_locations')
    print(json.dumps (res.json(), indent = 3)) 
    if res:
        is_valid_status_code(res, 200)


def test_get_locations_2():
    res = invoke_get('/get_locations/_DEFAULT_')
    if res:
        is_valid_status_code(res, 200)


def test_get_screenflow_seq():
    res = invoke_get('/get_screen_flow_seq/_DEFAULT_')
    if res:
        is_valid_status_code(res, 200)


def test_get_available_dates():
    res = invoke_get('/get_available_dates/_DEFAULT_')
    if res:
        is_valid_status_code(res, 200)


def test_get_available_locations():
    res = invoke_get('/get_available_locations/_DEFAULT_/20201126')
    if res:
        is_valid_status_code(res, 200)


def test_get_locations_near_me_1():
    res = invoke_get('/get_locations_near_me/32.779167/-96.808891')
    if res:
        is_valid_status_code(res, 200)


def test_get_locations_near_me_2():
    res = invoke_get('/get_locations_near_me/32.779167/-96.808891/50')
    if res:
        is_valid_status_code(res, 200)


def test_get_locations_near_me_3():
    res = invoke_get(
        '/get_locations_near_me/_DEFAULT_/32.779167/-96.808891/50')
    if res:
        is_valid_status_code(res, 200)


def test_get_locations_near_me_4():
    res = invoke_get(
        '/get_locations_near_me/_DEFAULT_/20201126/32.779167/-96.808891/50')
    if res:
        is_valid_status_code(res, 200)


def test_get_get_available_times_1():
    res = invoke_get('/get_available_times/7/20201127')
    if res:
        is_valid_status_code(res, 200)


def test_get_get_available_times_2():
    res = invoke_get('/get_available_times/7')
    if res:
        is_valid_status_code(res, 200)


def test_get_lookup_appointments_by_phone():
    res = invoke_get('/lookup_appointments_by_phone/+18018602474/10311980')
    if res:
        is_valid_status_code(res, 200)


def test_get_appointment_results():
    res = invoke_get('/appointment/result/{token}/{dob}')
    if res:
        is_valid_status_code(res, 200)


def test_get_lookup_patient():
    res = invoke_get('/lookup_patient/{phone_number}')
    if res:
        is_valid_status_code(res, 200)


'''
def test_post_verify_phone():
    res = invoke_get('/verify_phone')
    if res:
        is_valid_status_code(res, 200)

def test_post_validate_otp():
    res = invoke_get('/validate_otp')
    if res:
        is_valid_status_code(res, 200)
'''


def run_tests():
    test_get_locations_1()
    test_get_locations_2()
    test_get_screenflow_seq()
    test_get_available_dates()
    test_get_available_locations()
    test_get_locations_near_me_1()
    test_get_locations_near_me_2()
    test_get_locations_near_me_3()
    test_get_locations_near_me_4()
    test_get_get_available_times_1()
    test_get_get_available_times_2()


os.system('clear')
print_header('*********************************')
print_header('Starting GGT-API endpoint testing')
print_header('*********************************')


run_tests()


'''


@router.post("/finalize_registration", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_registration(finalize_registration_request: FinalizeRegistrationRequest):
    return finalize_registration(finalize_registration_request)


@router.post("/finalize_payment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_payment(finalize_payment_request: FinalizePaymentRequest):
    return finalize_payment(finalize_payment_request)


@router.post("/lookup_appointment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_appointment(req: LookupAppointmentRequest):
    return lookup_appointment(
        req.appointment_id,
        req.dob
    )




@router.post("/verify_existing_patient")
async def api_verify_existing_patient(req: VerifyExistingPatientRequest):
    return verify_existing_patient(
        req.phone_number,
        req.dob
    )
'''
