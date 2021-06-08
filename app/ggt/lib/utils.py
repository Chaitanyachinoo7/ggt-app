import jwt
import ujson
import logging
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pformat

# import google.cloud.logging
import phonenumbers
import pyotp

#import google.cloud.logging
#import googlecloudprofiler

import ggt.lib.constants as c
from ggt.configs.config_loader import cfg
from ggt.configs.lang_loader import  load_languages
# TODO: Enahance logging context with user session and client device/ip info etc.
from ggt.models.data_models.data_types import User


def get_config_val(key):
    key_list = key.split('.')
    key_depth = len(key_list)
    if key_depth == 1:
        return cfg[key_list[0]]
    elif key_depth == 2:
        return cfg[key_list[0]][key_list[1]]
    elif key_depth == 3:
        return cfg[key_list[0]][key_list[1]][key_list[2]]
    elif key_depth == 4:
        return cfg[key_list[0]][key_list[1]][key_list[2]][key_list[3]]
    elif key_depth == 5:
        return cfg[key_list[0]][key_list[1]][key_list[2]][key_list[3]][key_list[4]]
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


def log_generic(**kwargs):
    for key in kwargs.keys():
        globals()[key] = kwargs[key]

    if kwargs is not None and 'type' in kwargs:
        kwargs['timestamp'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f")[:-3]

        if kwargs['type'] == c.ERROR in kwargs:
            kwargs['.'] = '⛔️⛔️⛔️'
            # logging.error(pformat(kwargs))
            print(format_log_message(kwargs))
        elif kwargs['type'] == c.WARNING in kwargs:
            kwargs['.'] = '⚠️'
            # logging.warning(pformat(kwargs))
            print(format_log_message(kwargs))
        elif kwargs['type'] == c.INFO in kwargs:
            kwargs['.'] = 'ℹ️'
            # logging.info(format_log_message(kwargs))
            print(format_log_message(kwargs))
        else:
            # logging.debug(format_log_message(kwargs))
            print(format_log_message(kwargs))

    else:
        # logging.warning('Empty log value')
        print('Empty log value')


def format_log_message(kwargs):
    if get_config_val('env').startswith("LOCAL"):
        return pformat(kwargs)
    else:
        return ujson.dumps(kwargs)

#
# def app_init():
#     if get_config_val('gcp.enable_cloud_logger'):
#         init_cloud_logger()

    # if get_config_val('gcp.enable_cloud_profiler'):
    #    init_cloud_profiler()

#
# def init_cloud_logger():
#     '''
#     This will override default behavior of the python logger and stream logs to GCP
#     '''
#     curr_file = Path(__file__)
#     service_account_file = get_config_val('gcp.service_account_file')
#     service_account_file = curr_file.parent.parent.parent.joinpath(
#         'ggt/configs/{}'.format(service_account_file))
#     client = google.cloud.logging.Client.from_service_account_json(
#         service_account_file)
#
#     client.get_default_handler()
#     client.setup_logging()
#
#
# def init_cloud_profiler():
#     # TODO: Untested/Doesn't work
#     # Profiler initialization. It starts a daemon thread which continuously
#     # collects and uploads profiles. Best done as early as possible.
#     try:
#         curr_file = Path(__file__)
#         service_account_file = get_config_val('gcp.service_account_file')
#         service_account_file = curr_file.parent.parent.parent.joinpath(
#             'ggt/configs/{}'.format(service_account_file))
#         client = google.cloud.logging.Client.from_service_account_json(
#             service_account_file)
#
#         googlecloudprofiler.start(
#             service=get_config_val('app_name'),
#             service_version=get_config_val('app_version'),
#
#             # It defaults to 0 (error) if not set.
#             verbose=get_config_val('gcp.cloud_logger_log_level'),
#
#             # project_id must be set if not running on GCP.
#             project_id=get_config_val('gcp.project_id'),
#         )
#
#     except (ValueError, NotImplementedError) as exc:
#         logging.error(exc)
#

def x_response(res, allow=True, reason_code=None):
    try:
        if allow and res:
            if is_failure_response_with_reason(res):
                return failure_response(
                    reason_code=res[c.REASON_CODE],
                    kv=res
                )
            else:
                return success_response(res)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            res=res,
            function=whoami(),
            error=err
        )
    return failure_response(reason_code=reason_code)


def y_response(res, allow=False, reason_code=None):
    try:
        if allow or res:
            return success_response_array(res)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            res=res,
            function=whoami(),
            error=err
        )
    reason_code = reason_code if reason_code else ''
    return failure_response(reason_code=reason_code)


def success_response(kv=None):
    if kv is None or kv is True:
        kv = {}
    kv[c.STATUS] = c.SUCCESS
    return kv


def is_failure_response_with_reason(kv=None):
    try:
        if kv is None or kv is True:
            return False
        else:
            if c.REASON_CODE in kv.keys():
                return True

    except Exception as err:
        print('Error @is_failure_response_with_reason')

    return False


def success_response_array(kv=None):
    if kv is None or kv is True:
        kv = []
    res = {}
    res[c.STATUS] = c.SUCCESS
    res['results'] = kv
    return res


def failure_response(reason_code='', kv=None):
    if kv is None:
        kv = {}
    kv[c.STATUS] = c.FAILED
    kv[c.REASON_CODE] = reason_code
    return kv


def is_admin(user: User):
    return (user and user.roles) and (get_config_val('app.roles.admin') in ujson.loads(user.roles))


def is_care_provider(user: User):
    return (user and user.roles) and (get_config_val('app.roles.care_provider') in ujson.loads(user.roles))


def is_clinical_provider(user: User):
    return (user and user.roles) and (get_config_val('app.roles.clinical_provider') in ujson.loads(user.roles))


def is_site_admin(user: User):
    return (user and user.roles) and (get_config_val('app.roles.site_admin') in ujson.loads(user.roles))


def is_contact_center(user: User):
    return (user and user.roles) and (get_config_val('app.roles.contact_center') in ujson.loads(user.roles))


def get_random_password():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@£$%^&*().,?0123456789'
    password = ''
    for c in range(20):
        password += random.choice(chars)
    return password


def get_sqs_queue_url(schedule_id):
    if get_config_val('env') != 'PROD':
        return get_config_val('aws.sqs_url')
    else:
        r = int(schedule_id) % int(get_config_val('aws.queue_count'))
        return get_config_val('aws.sqs_url').format(r)


def get_ggv_tokens(number):
    tokens = []
    secret = get_config_val('security.ggv_secret')
    start_time = datetime.now()
    end_time = start_time + timedelta(days=20)
    for x in range(0, number):
        uu_id = generate_token()
        encoded_jwt = jwt.encode({
            "token": uu_id,
            "exp": end_time,
            "type": "single"
        }, secret, algorithm="HS256")
        tokens.append(encoded_jwt)
    return tokens


def get_ggv_tokens_v2(req):
    tokens = []
    secret = get_config_val('security.ggv_secret')
    start_time = datetime.now()
    token_type = req.type
    number = req.number
    valid_days = req.valid_days
    end_time = start_time + timedelta(days=valid_days)
    for x in range(0, number):
        uu_id = generate_token()
        encoded_jwt = jwt.encode({
            "token": uu_id,
            "exp": end_time,
            "type": token_type
        }, secret, algorithm="HS256")
        tokens.append(encoded_jwt)
    return tokens


def get_user_token_from_jwt(token):
    secret = get_config_val('security.ggv_secret')
    try:
        res = jwt.decode(token, secret, algorithms=["HS256"])
        token_type = None
        if 'type' in res.keys():
            token_type = res['type']
        return res['token'], token_type
    except Exception as err:
        log_generic(
            err=err,
            function=whoami()
        )
        return None, None


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


def get_translated_message(message_id: str):
    lang_configs = load_languages()
    message_in_langs = lang_configs[message_id] if message_id in lang_configs else lang_configs['lorem_ipsum']

    # Define inner function to get the message in specified language such as en, es, ...
    def get_language(lang):
        if lang is None:
            return message_in_langs['en']
        # If specified language is not there, return the default - en
        return message_in_langs[lang] if lang in message_in_langs else message_in_langs['en']
    return get_language  # Return the inner function so that caller can do get_translated_message('id')('es')


def is_international(phone_number):
    country_code = phone_number[0:len(phone_number) - 10]
    if country_code == '+1':
        return False
    else:
        return True

