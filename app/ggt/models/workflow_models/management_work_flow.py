from starlette.responses import StreamingResponse

from ggt.lib.utils import y_response, x_response
from ggt.models.process_models.bp_management import bp_create_user, bp_delete_user, bp_update_user_role, \
    bp_create_new_organisation_request, bp_list_org_requests, bp_process_org_request, bp_user_profile, bp_list_user


def create_new_organisation_request(req):
    return y_response(
        bp_create_new_organisation_request(req)
    )


def list_org_requests(req):
    return y_response(
        bp_list_org_requests(req)
    )


def process_org_request(req, user):
    return y_response(
        bp_process_org_request(req, user)
    )


def create_user(user, owner):
    return y_response(
        bp_create_user(user, owner=owner)
    )


def delete_user(user):
    return x_response(
        bp_delete_user(user)
    )


def user_profile(user):
    return y_response(
         bp_user_profile(user)
    )


def update_user_role(user):
    return y_response(
        bp_update_user_role(user)
    )


def list_user(req, user):
    return y_response(
        bp_list_user(req, user)
    )