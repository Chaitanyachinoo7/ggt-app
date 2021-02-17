from ggt.lib.adapters.auth0_adapter import create_user_in_auth0, delete_user_in_auth0, get_role_ids, remove_roles, \
    assign_roles, get_user_in_auth0, create_password_change_ticket, update_user_in_auth0, get_organization_id
from ggt.lib.adapters.auth0_config import META_KEY, ORGANIZATION_KEY
from ggt.lib.constants import ERROR
from ggt.lib.management_utils import send_new_account_creation_email, send_org_reject_email, \
    send_new_account_registration_request_email
from ggt.lib.utils import log_generic, whoami, get_ggv_tokens
from ggt.models.data_models.data_types import CreateAuth0User, UserRolesEnum, DbOrgRequestStatusEnum
from ggt.models.data_models.management import create_new_organization_request, list_org_requests, process_org_request, \
    get_org_request_user, create_new_organization, create_new_user, delete_user, update_user_role, get_user_by_ext_id, \
    list_user, update_user, update_user_status, list_organizations, change_org_status


def bp_create_new_organization_request(req):
    try:
        status = create_new_organization_request(req)
        if status:
            send_new_account_registration_request_email(req.given_name, req.email)
        return status
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_list_org_requests(req):
    try:
        return list_org_requests(req)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_process_org_request(req, user):
    try:
        if process_org_request(req, user) is not None:
            res = get_org_request_user(req.id)

            if req.status == DbOrgRequestStatusEnum.accepted:
                if res is not None and len(res) > 0:
                    data = res
                    _user = CreateAuth0User(
                        organization_id=req.id,
                        role=[UserRolesEnum.org_admin],
                        email=data['email'],
                        given_name=data['given_name'],
                        family_name=data['family_name'],
                        name=data['name'],
                        nickname=data['nick_name'],
                    )
                    auth_user = create_user_in_auth0(_user, req.id)
                    if auth_user:
                        create_new_organization(data, auth_user['id'])
                        _x = get_user_in_auth0(auth_user['id']).json()
                        create_new_user(_x, [UserRolesEnum.org_admin])
                        send_new_account_creation_email(_x['given_name'], _x['email'], auth_user['password'])
                        return {"auth_user": auth_user, "org_id": req.id}
            if req.status == DbOrgRequestStatusEnum.rejected:
                if res is not None and len(res) > 0:
                    data = res
                    send_org_reject_email(data['given_name'], data['email'])
                return {"status": "rejected"}
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_create_user(user, is_org_owner=False, owner=None):
    try:
        if is_org_owner:
            organization_id = user.organization_id
        else:
            organization_id = get_organization_id(owner)
        if organization_id is None:
            return None
        auth_user = create_user_in_auth0(user, organization_id)
        _user = get_user_in_auth0(auth_user['id']).json()
        if create_new_user(_user, user.role) is not None:
            send_new_account_creation_email(_user['given_name'], _user['email'], auth_user['password'])
            return _user
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_update_user(user):
    try:
        body = {
            "email": user.email,
            "given_name": user.given_name,
            "family_name": user.family_name,
            "name": user.name,
            "nickname": user.nickname,
        }
        auth_user = update_user_in_auth0(body, user.ext_id)
        if update_user(user) is not None:
            return auth_user
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_update_user_state(user):
    try:
        body = {
            "blocked": not user.is_active
        }
        auth_user = update_user_in_auth0(body, user.ext_id)
        if update_user_status(user) is not None:
            return auth_user
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_delete_user(user):
    try:
        if delete_user_in_auth0(user) is None:
            return None
        return delete_user(user.ext_user_id)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_update_user_role(user):
    try:
        current_role_ids = get_role_ids(user.current_role)
        new_role_ids = get_role_ids(user.new_role)
        user_id = user.ext_user_id
        if remove_roles(user_id, current_role_ids) is None:
            return None
        if assign_roles(user_id, new_role_ids) is None:
            return None
        return update_user_role(user_id, user.new_role)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_user_profile(user):
    try:
        return get_user_by_ext_id(user['sub'])
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_list_user(req, user):
    try:
        return list_user(req, user)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_list_organizations(req, user):
    try:
        return list_organizations(req, user)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_change_org_status(req, user):
    try:
        return change_org_status(req, user)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_password_change_ticket(req, user):
    try:
        return create_password_change_ticket(req, user)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def bp_get_ggv_tokens(number, user):
    try:
        return get_ggv_tokens(number)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None
