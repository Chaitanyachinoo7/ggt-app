from fastapi import (
    APIRouter,
    Security
)

from ggt.lib.auth import authorize_user
from ggt.models.data_models.data_types import PermissionsEnum as p, CreateAuth0User, DeleteAuth0User, UpdateAuth0User, \
    CreateNewOrganization, ListOrgRequests, ProcessOrgRequests, FilterUser, UpdateAuth0UserInfo, UpdateAuth0UserState
from ggt.models.workflow_models.management_work_flow import create_user, delete_user, update_user_role, user_profile, \
    create_new_organisation_request, list_org_requests, process_org_request, list_user, update_user, update_user_state

router = APIRouter()


########################################
# Only for GGT Admins                  #
########################################
@router.post("/list_org_requests", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_list_org_requests(req: ListOrgRequests):
    return list_org_requests(req)


@router.post("/process_org_request")
async def api_process_org_request(req: ProcessOrgRequests, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return process_org_request(req, user)

########################################


@router.post("/create_new_organisation_request", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_create_new_organisation_request(req: CreateNewOrganization):
    return create_new_organisation_request(req)


@router.post("/create_user")
async def api_create_user(req: CreateAuth0User, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return create_user(req, user)


@router.post("/update_user")
async def api_update_user(req: UpdateAuth0UserInfo, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return update_user(req)


@router.post("/update_user_state")
async def api_update_user_state(req: UpdateAuth0UserState, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return update_user_state(req)


@router.post("/delete_user", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_delete_user(req: DeleteAuth0User):
    return delete_user(req)


@router.post("/update_user_role", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_update_user_role(req: UpdateAuth0User):
    return update_user_role(req)


@router.get("/user_profile")
async def api_user_profile(user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return user_profile(user)


@router.post("/list_users")
async def api_list_users(req: FilterUser, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return list_user(req, user)

#
# @router.post("/update_org_owner", dependencies=[Security(authorize_user, scopes=['ANONYMOUS'])])
# async def api_update_org_owner(req: UpdateOwner):
#     return await update_org_owner(req)
#
#
#
#

