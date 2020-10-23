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

from ggt.models.data_models.data_types import (
    User,
    AuthError
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

# TODO: Enahance logging context with user session and client device/ip info etc.


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


async def requires_auth(token):
    """Determines if the Access Token is valid
    """
    ####################################################
    # Trying to call this API async, but doesn't work  #
    # Recommend to use redis to store this value       #
    ####################################################
    jsonurl = urllib2.urlopen(
        "https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")

    ####################################################
    # Here the api call originally sync                #
    ####################################################
    # jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")

    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

    if rsa_key:
        try:
            user = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/"
            )
            ###########################################
            print(user)  # Remove this debug log TODO #
            ###########################################

            return User(iss=str(user['iss']), sub=str(user['sub']),
                        aud=str(user['aud']), iat=str(user['iat']),
                        euserp=str(user['exp']), azp=str(user['azp']),
                        scope=str(user['scope']), roles=json.dumps(user['http://roles.ggt/roles']))
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                             "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                             "description":
                             "incorrect claims,"
                             "please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Unable to parse authentication"
                                 " token."}, 401)

    raise AuthError({"code": "invalid_header",
                     "description": "Unable to find appropriate key"}, 401)












'''
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
'''
