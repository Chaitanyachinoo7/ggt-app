from datetime import datetime
import sys
import inspect

import logging
import aiohttp
import json
import pyotp
import uuid
import phonenumbers
import requests
from pprint import pprint, pformat

from ggt.configs.config_loader import cfg

# TODO: Enahancd logging context with user session and client device/ip info etc.


def get_config_val(key):
    key_list = key.split('.')
    key_depth = len(key_list)
    if key_depth == 1:
        return cfg[key_list[0]]
    elif key_depth == 2:
        return cfg[key_list[0]][key_list[1]]
    elif key_depth == 3:
        return cfg[key_list[0]][key_list[1]][key_list[2]]
    else:
        return ""


def generate_otp():
    otp = pyotp.TOTP('base32secret3232')
    return otp.now()


def generate_session_id():
    return generate_token()


def generate_token():
    return str(uuid.uuid4())


def validate_phone_number_format(phone_number):
    """
    Validates given phone number and returns E164 format.
    """
    try:
        parsed = phonenumbers.parse(phone_number, "US")
        formatted_number = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164)
        return formatted_number
    except phonenumbers.NumberParseException as e:
        return ""


def convert_to_bool(val):
    if val == 'false' or val == 'no' or val == 'none' or val == '0' or val == 0 or val == False or val == None:
        return 0
    else:
        return 1


# TODO replace with Google Cloud Logger
def log_generic(**kwargs):
    for key in kwargs.keys():
        globals()[key] = kwargs[key]

    kwargs['source'] = inspect.stack()[1][4]
    kwargs['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    if 'error' in kwargs:
        logging.error(pformat(kwargs))
    elif 'info' in kwargs:
        logging.info(pformat(kwargs))
    else:
        logging.debug(pformat(kwargs))

    # pprint(kwargs)


def x_response(res, allow=True):
    try:
        if allow and res:
            return success_response(res)

    except Exception as err:
        log_generic(type="error", res=res, function="x_response", error=err)
    return failure_response()


def y_response(res, allow=True):
    try:
        if allow and res:
            return success_response_array(res)

    except Exception as err:
        log_generic(type="error", res=res, function="y_response", error=err)
    return failure_response()


def success_response(kv=None):
    if kv is None or kv is True:
        kv = {}
    kv['status'] = 'success'
    return kv


def success_response_array(kv=None):
    if kv is None or kv is True:
        kv = {}
    res = {}
    res['status'] = 'success'
    res['results'] = kv
    return res


def failure_response(kv=None):
    if kv is None:
        kv = {}
    kv['status'] = 'failure'
    return kv


'''
def __sumo_log(payload):
    url = 'https://endpoint6.collection.us2.sumologic.com/receiver/v1/http/ZaVnC4dhaV089RJkF1MhGi12i2uKBw-BI23tO1u7ZLSkBwKlBGBfHG8UxS_m5RLU02_leUwIY8lm9PVNmWYdU02jbwj7BKjSV2H6TMPBoBjJm9W539bKnQ=='
    payload['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    pprint(payload)
    try:
        requests.post(url, json=payload)
    except Exception as err:
        print(sys.exc_info()[0])
        print(err)
'''
