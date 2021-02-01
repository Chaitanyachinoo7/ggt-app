import requests
import json

from ggt.lib.adapters.auth0_config import AUTH_URL, AUTH0_MANAGEMENT_CLIENT_ID, AUTH0_MANAGEMENT_CLIENT_SECRET, \
    AUTH0_MANAGEMENT_AUDIENCE, AUTH0_MANAGEMENT_GRANT_TYPE, AUTH0_USER_MANAGEMENT_API, AUTH0_CONNECTION, \
    AUTH0_GET_ROLES_API, AUTH0_ASSIGN_ROLES_API, AUTH0_USER_UPDATE_API, AUTH0_PASSWORD_RESET, META_KEY, ORGANIZATION_KEY
from ggt.lib.constants import ERROR
from ggt.lib.utils import log_generic, whoami, get_random_password


def get_management_api_req_headers():
    body = {
        'client_id': AUTH0_MANAGEMENT_CLIENT_ID,
        'client_secret': AUTH0_MANAGEMENT_CLIENT_SECRET,
        'audience': AUTH0_MANAGEMENT_AUDIENCE,
        'grant_type': AUTH0_MANAGEMENT_GRANT_TYPE
    }
    auth_response = requests.post(AUTH_URL, data=body)
    auth = "Bearer {}".format(auth_response.json()['access_token'])
    return {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}


def create_user_in_auth0(user, organization_id):
    try:
        headers = get_management_api_req_headers()
        password = get_random_password()
        body = {
            "email": user.email,
            "blocked": user.blocked,
            "email_verified": user.email_verified,
            "given_name": user.given_name,
            "family_name": user.family_name,
            "name": user.name,
            "nickname": user.nickname,
            "connection": AUTH0_CONNECTION,
            "password": password,
            "user_metadata": {
                "organization": organization_id
            }
        }
        body = json.dumps(body)
        r = requests.post(AUTH0_USER_MANAGEMENT_API, data=body, headers=headers)
        _user = r.json()
        keys = _user.keys()
        if 'created_at' not in keys:
            return None
        role_ids = []

        for role in user.role:
            role_id = get_role_id(role)
            role_ids.append(role_id)
        user_id = _user['identities'][0]['provider'] + '|' + _user['identities'][0]['user_id']
        assign_roles(user_id, role_ids)
        return {'id': user_id, 'password': password}
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_user_in_auth0(body, ext_id):
    try:
        headers = get_management_api_req_headers()
        body = json.dumps(body)
        update_api = AUTH0_USER_UPDATE_API.format(ext_id)
        r = requests.patch(update_api, data=body, headers=headers)
        _user = r.json()
        return {'user': _user}
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def delete_user_in_auth0(user):
    try:
        headers = get_management_api_req_headers()
        delete_user_uri = AUTH0_USER_UPDATE_API.format(user.ext_user_id)
        requests.delete(delete_user_uri, headers=headers)
        return True
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_user_in_auth0(id):
    try:
        headers = get_management_api_req_headers()
        delete_user_uri = AUTH0_USER_UPDATE_API.format(id)
        return requests.get(delete_user_uri, headers=headers)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_role_id(role):
    try:
        headers = get_management_api_req_headers()
        r = requests.get(AUTH0_GET_ROLES_API, headers=headers)
        roles = r.json()
        for _role in roles:
            if _role['name'] == role:
                return _role['id']
        return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_role_ids(role_name_list):
    try:
        headers = get_management_api_req_headers()
        r = requests.get(AUTH0_GET_ROLES_API, headers=headers)
        roles = r.json()
        ids = []
        for name in role_name_list:
            for _role in roles:
                if _role['name'] == name:
                    ids.append(_role['id'])
        return ids
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def assign_roles(user_id, role_ids):
    try:
        headers = get_management_api_req_headers()
        assign_url = AUTH0_ASSIGN_ROLES_API.format(user_id)
        body = {
            'roles': role_ids
        }
        body = json.dumps(body)
        r = requests.post(assign_url, data=body, headers=headers)
        if r.status_code == 204:
            return True
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def remove_roles(user_id, role_ids):
    try:
        headers = get_management_api_req_headers()
        assign_url = AUTH0_ASSIGN_ROLES_API.format(user_id)
        body = {
            'roles': role_ids
        }
        body = json.dumps(body)
        r = requests.delete(assign_url, data=body, headers=headers)
        if r.status_code == 204:
            return True
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_password_change_ticket(req, user):
    try:
        headers = get_management_api_req_headers()
        body = {
            "result_url": req.headers['origin'],
            "user_id": user['sub'],
            "ttl_sec": 2000,
            "mark_email_as_verified": False,
            "includeEmailInRedirect": False
        }
        body = json.dumps(body)
        r = requests.post(AUTH0_PASSWORD_RESET, data=body, headers=headers)
        return r.json()
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_organization_id(user):
    if user is None:
        return None
    # TODO: Uncomment 1st line to get organization id, the existing code is a temp fix
    # organization_id = user[META_KEY][ORGANIZATION_KEY] if user[META_KEY] else None
    organization_id = user[META_KEY][ORGANIZATION_KEY] if user[META_KEY] else 1
    return organization_id
