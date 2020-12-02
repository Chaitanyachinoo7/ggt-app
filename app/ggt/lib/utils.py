import ujson
import logging
import sys
import uuid
from datetime import datetime
from pprint import pformat
from pathlib import Path

import phonenumbers
import pyotp

import google.cloud.logging
#import googlecloudprofiler

from ggt.configs.config_loader import cfg
import ggt.lib.constants as c


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


def log_generic(**kwargs):
    for key in kwargs.keys():
        globals()[key] = kwargs[key]

    if kwargs is not None and 'type' in kwargs:
        kwargs['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if kwargs['type'] == c.ERROR in kwargs:
            kwargs['.'] = '⛔️⛔️⛔️'
            logging.error(pformat(kwargs))
        elif kwargs['type'] == c.WARNING in kwargs:
            kwargs['.'] = '⚠️'
            logging.warning(pformat(kwargs))
        elif kwargs['type'] == c.INFO in kwargs:
            kwargs['.'] = 'ℹ️'
            logging.info(pformat(kwargs))
        else:
            logging.debug(pformat(kwargs))
    
    else:
        logging.warning('Empty log value')


def app_init():        
    if get_config_val('gcp.enable_cloud_logger'):
        init_cloud_logger()

    #if get_config_val('gcp.enable_cloud_profiler'):
    #    init_cloud_profiler()


def init_cloud_logger():
    '''
    This will override default behavior of the python logger and stream logs to GCP
    '''
    curr_file = Path(__file__)
    service_account_file = get_config_val('gcp.service_account_file')
    service_account_file = curr_file.parent.parent.parent.joinpath('ggt/configs/{}'.format(service_account_file))
    client = google.cloud.logging.Client.from_service_account_json(service_account_file)

    client.get_default_handler()
    client.setup_logging()


def init_cloud_profiler():
    # TODO: Untested/Doesn't work
    # Profiler initialization. It starts a daemon thread which continuously
    # collects and uploads profiles. Best done as early as possible.
    try:
        curr_file = Path(__file__)
        service_account_file = get_config_val('gcp.service_account_file')
        service_account_file = curr_file.parent.parent.parent.joinpath('ggt/configs/{}'.format(service_account_file))
        client = google.cloud.logging.Client.from_service_account_json(service_account_file)

        googlecloudprofiler.start(
            service=get_config_val('app_name'),
            service_version=get_config_val('app_version'),

            # It defaults to 0 (error) if not set.
            verbose=get_config_val('gcp.cloud_logger_log_level'),

            # project_id must be set if not running on GCP.
            project_id=get_config_val('gcp.project_id'),
        )

    except (ValueError, NotImplementedError) as exc:
        logging.error(exc)


def x_response(res, allow=True):
    try:
        if allow and res:
            return success_response(res)

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR,
            res=res,
            function=whoami(),
            error=err
        )
    return failure_response()


def success_response(kv=None):
    if kv is None or kv is True:
        kv = {}
    kv[c.STATUS] = c.SUCCESS
    return kv


def success_response_array(kv=None):
    if kv is None or kv is True:
        kv = {}
    res = {}
    res[c.STATUS] = c.SUCCESS
    res['results'] = kv
    return res


def failure_response(kv=None):
    if kv is None:
        kv = {}
    kv[c.STATUS] = c.FAILED
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

