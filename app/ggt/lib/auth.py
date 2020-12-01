import json
import os
import urllib.request as urllib2

from fastapi import Depends, Request, HTTPException
from fastapi.security import SecurityScopes
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import jwt, JWTError

import ggt.lib.constants as c

from ggt.lib.oath2_wrapper import GgtOAuth2PasswordBearer

from ggt.lib.utils import (
    log_generic,
    whoami,
    get_config_val
)

from ggt.models.data_models.data_types import (
    User,
    AuthError,
    PermissionsEnum as p)

# TODO: [GGT-81] read from config/DB
CLIENT_ID = "269165607649-ejpvn7ar1llub2e8tr6ur4ad2p1srucf.apps.googleusercontent.com"
# TODO: [GGT-82] read from config/DB as a single value of "tokenUrl" e.g. GgtOAuth2PasswordBearer(tokenUrl=get_config_val('vendors.auth0.auth0_domain'))
oauth2_scheme = GgtOAuth2PasswordBearer(tokenUrl="https://" + get_config_val('vendors.auth0.auth0_domain') +
                                        "/oauth/token")


# TODO: [GGT-84] read from config/DB
def verify_google_idtoken(token):
    try:
        decoded_token = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)

        if(decoded_token['email'].split('@')[1] == "wellpay.com" or
           decoded_token['email'].split('@')[1] == "wellhealth.studio" or
           decoded_token['email'].split('@')[1] == "hrmdmanagement.com" or
           decoded_token['email'].split('@')[1] == "flowermoundpain.co"):
            return True
        else:
            return False

    except Exception as err:
        log_generic(
            type=c.ERROR,
            token=token,
            function=whoami(),
            error=err
        )
        return False


def get_value(user, key):
    if key in user.keys():
        return str(user[key])
    else:
        return ""


async def get_rsa_key(token):
    if 'RSA_KEY' in os.environ:
        return json.loads(os.environ.get('RSA_KEY'))

    else:
        rsa_key = await get_rsa_key_auth0(token)
        return rsa_key

# TODO: [GGT-83] read from config/DB as already concatinated value of tokenUrl or use a function that generates these auth0 urls


async def get_rsa_key_auth0(token):
    jsonurl = urllib2.urlopen(
        "https://" + get_config_val('vendors.auth0.auth0_domain') + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    try:
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
                _rsa_key = json.dumps(rsa_key)
                os.environ['RSA_KEY'] = _rsa_key

        return rsa_key

    except JWTError:
        raise AuthError({
            "code": "invalid_header",
            c.DESCRIPTION: "Unable to find appropriate key"
        }, 401)


async def authorize_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if (get_config_val('env') == 'DEV'):  # Allow auth override for dev
        return True
    try:
        scopes = security_scopes.scopes
        if p.ANONYMOUS in scopes:
            return True
        elif token is not None:
            auth = await authorize(scopes, token)
            return auth
        else:
            raise HTTPException(status_code=401, detail=c.AUTH_FAILED_MESSAGE)

    except AuthError as err:
        print(err)
        return None


async def authorize(scopes, token):
    """Determines if the Access Token is valid
    """
    rsa_key = await get_rsa_key(token)
    if rsa_key:
        try:
            user = jwt.decode(
                token,
                rsa_key,
                algorithms=get_config_val('vendors.auth0.algorithms'),
                audience=get_config_val('vendors.auth0.api_audience'),
                issuer="https://" +
                       get_config_val('vendors.auth0.auth0_domain') + "/"
            )

            if len(list(set(user['permissions']).intersection(scopes))) > 0:
                return True
            else:
                raise HTTPException(
                    status_code=401, detail=c.AUTH_FAILED_MESSAGE)
        except jwt.ExpiredSignatureError:
            await get_rsa_key_auth0(token)
            raise HTTPException(status_code=401, detail=c.AUTH_FAILED_MESSAGE)
        except jwt.JWTClaimsError:
            await get_rsa_key_auth0(token)
            raise HTTPException(status_code=401, detail=c.AUTH_FAILED_MESSAGE)
        except Exception:
            await get_rsa_key_auth0(token)
            raise HTTPException(status_code=401, detail=c.AUTH_FAILED_MESSAGE)
    await get_rsa_key_auth0(token)
    raise HTTPException(status_code=401, detail=c.AUTH_FAILED_MESSAGE)
