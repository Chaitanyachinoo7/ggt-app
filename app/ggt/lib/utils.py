import json
import logging
import sys
import uuid
from datetime import datetime
from pprint import pformat

import phonenumbers
import pyotp

from ggt.configs.config_loader import cfg
from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    ERROR)
# TODO: Enahance logging context with user session and client device/ip info etc.
from ggt.models.data_models.data_types import User


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def whoami():
    return sys._getframe(1).f_code.co_name


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
        print(e)
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

    #kwargs['source'] = inspect.stack()[1][4]
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
        log_generic(
            type=ERROR,
            res=res,
            function=whoami(),
            error=err
        )
    return failure_response()


def y_response(res, allow=True):
    try:
        if allow and res:
            return success_response_array(res)

    except Exception as err:
        log_generic(
            type=ERROR,
            res=res,
            function=whoami(),
            error=err
        )
    return failure_response()


def success_response(kv=None):
    if kv is None or kv is True:
        kv = {}
    kv[STATUS] = SUCCESS
    return kv


def success_response_array(kv=None):
    if kv is None or kv is True:
        kv = {}
    res = {}
    res[STATUS] = SUCCESS
    res['results'] = kv
    return res


def failure_response(kv=None):
    if kv is None:
        kv = {}
    kv[STATUS] = FAILED
    return kv


def is_admin(user: User):
    return (user and user.roles) and (get_config_val('app.roles.admin') in json.loads(user.roles))


def is_care_provider(user: User):
    return (user and user.roles) and (get_config_val('app.roles.care_provider') in json.loads(user.roles))


def is_clinical_provider(user: User):
    return (user and user.roles) and (get_config_val('app.roles.clinical_provider') in json.loads(user.roles))


def is_site_admin(user: User):
    return (user and user.roles) and (get_config_val('app.roles.site_admin') in json.loads(user.roles))


def is_contact_center(user: User):
    return (user and user.roles) and (get_config_val('app.roles.contact_center') in json.loads(user.roles))

