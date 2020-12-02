from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Response,
    status,
    Security
)

from ggt.lib.auth import (
    verify_google_idtoken,
    authorize_user
)
import ggt.lib.constants as c

from ggt.models.data_models.data_types import (
    PortalUserRoleRequest,
    PortalCcPatientLookupRequest,
    PortalGeneralSearchRequest,
    PortalLocationSearchRequest,
    ScheduleGenerationRule,
    GgtDbLocation,
    GgtUpdateLocation,
    LocationToGroupMap,
    LocationToServiceMap,
    GgtThirdPartyDbGroup,
    GgtThirdPartyDbUpdateGroup,
    PermissionsEnum as p
)
from ggt.models.workflow_models.admin_flow import (
    admin_get_all_test_results
)
from ggt.models.workflow_models.contact_center_flow import (
    cc_search_details_by_name_and_dob
)
from ggt.models.workflow_models.portal_general_flow import (
    portal_get_user_role
)
from ggt.models.workflow_models.test_site_admin_flow import (
    site_admin_general_search,
    generate_schedule,
    generate_all_schedules,
    site_admin_location_search,
    add_schedule_generation_rule,
    update_schedule_generation_rule,
    delete_schedule_generation_rule,
    get_schedule_generation_rules,
    delete_schedule,
    create_location,
    get_all_groups,
    update_location,
    assign_group,
    remove_group,
    assign_service,
    remove_service,
    get_all_services,
    get_locations,
    create_group,
    update_group
)

router = APIRouter()


# TODO review after Auth0 implementation
@router.post("/get_user_role")
async def api_get_user_role(portal_user_role_request: PortalUserRoleRequest,
                            request: Request,
                            response: Response):
    if verify_google_idtoken(request.headers['Authorization']):
        return portal_get_user_role(portal_user_role_request.email)
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }


@router.post("/site-admin/create_location", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_create_location(location: GgtDbLocation):
    return await create_location(location)


@router.post("/site-admin/create_group", dependencies=[Security(authorize_user, scopes=[p.CREATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbGroup):
    return await create_group(group)


@router.post("/site-admin/update_group", dependencies=[Security(authorize_user, scopes=[p.UPDATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbUpdateGroup):
    return await update_group(group)


@router.post("/site_admin/location/assign_group", dependencies=[Security(authorize_user, scopes=[p.ASSIGN_GROUP])])
async def api_assign_group(req: LocationToGroupMap):
    return await assign_group(req)


@router.post("/site_admin/location/remove_service",
             dependencies=[Security(authorize_user, scopes=[p.REMOVE_SERVICE])])
async def api_remove_service(req: LocationToServiceMap):
    return await remove_service(req)


@router.post("/site_admin/location/assign_service",
             dependencies=[Security(authorize_user, scopes=[p.ASSIGN_SERVICE])])
async def api_assign_service(req: LocationToServiceMap):
    return await assign_service(req)


@router.post("/site_admin/location/remove_groups", dependencies=[Security(authorize_user, scopes=[p.REMOVE_GROUPS])])
async def api_remove_group(req: LocationToGroupMap):
    return await remove_group(req)


@router.get("/site_admin/location/get_locations", dependencies=[Security(authorize_user, scopes=[p.GET_LOCATIONS])])
async def api_get_locations():
    return await get_locations()


@router.post("/site-admin/update_location", dependencies=[Security(authorize_user, scopes=[p.UPDATE_LOCATION])])
async def api_update_location(location: GgtUpdateLocation):
    return await update_location(location)


@router.get("/site-admin/get_all_groups", dependencies=[Security(authorize_user, scopes=[p.GET_ALL_GROUPS])])
async def api_get_all_groups():
    return await get_all_groups()


@router.get("/site-admin/get_all_services", dependencies=[Security(authorize_user, scopes=[p.GET_ALL_SERVICES])])
async def api_get_all_services():
    return await get_all_services()


@router.post("/site-admin/general_search", dependencies=[Security(authorize_user, scopes=[p.GENERAL_SEARCH])])
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest):
    return await site_admin_general_search(
        portal_general_search_request.first_name,
        portal_general_search_request.middle_name,
        portal_general_search_request.last_name,
        portal_general_search_request.dob,
        portal_general_search_request.phone_number,
        portal_general_search_request.email,
        portal_general_search_request.appointment_id,
        portal_general_search_request.group_code,
        portal_general_search_request.appointment_date,
        portal_general_search_request.location_id,
        portal_general_search_request.sort_field,
        portal_general_search_request.sort_type
    )


@router.get("/site-admin/generate_schedule/{location_id}", dependencies=[Security(authorize_user, scopes=[p.GENERATE_SCHEDULE])])
async def api_generate_schedule(location_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_schedule, location_id)
    return {
        c.STATUS: c.SUCCESS,
        c.DESCRIPTION: c.BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/site-admin/generate_all_schedules", dependencies=[Security(authorize_user, scopes=[p.GENERATE_ALL_SCHEDULES])])
async def api_generate_all_schedules(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_all_schedules)
    return {
        c.STATUS: c.SUCCESS,
        c.DESCRIPTION: c.BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/site-admin/location_search", dependencies=[Security(authorize_user, scopes=[p.LOCATION_SEARCH])])
async def api_site_admin_location_search(portal_location_search: PortalLocationSearchRequest):
    return await site_admin_location_search(
        portal_location_search.account,
        portal_location_search.group_code,
        portal_location_search.site_code
    )


@router.post("/site-admin/add_schedule_generation_rule",
             dependencies=[Security(authorize_user, scopes=[p.ADD_SCHEDULE_GENERATION_RULE])])
async def api_add_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return await add_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/edit_schedule_generation_rule",
             dependencies=[Security(authorize_user, scopes=[p.EDIT_SCHEDULE_GENERATION_RULE])])
async def api_update_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return await update_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/delete_schedule_generation_rule/{id}",
             dependencies=[Security(authorize_user, scopes=[p.DELETE_SCHEDULE_GENERATION_RULE])])
async def api_delete_schedule_generation_rule(id: str):
    return await delete_schedule_generation_rule(id)


@router.get("/site-admin/delete_schedule/{location_id}",
            dependencies=[Security(authorize_user, scopes=[p.DELETE_SCHEDULE])])
async def api_delete_schedule(location_id: str):
    return await delete_schedule(location_id)


@router.get("/site-admin/get_schedule_generation_rules/{location_id}",
            dependencies=[Security(authorize_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_delete_schedule_generation_rules(location_id: str):
    return await get_schedule_generation_rules(location_id)


@router.post("/contact-center/patient_lookup", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
async def api_cc_patient_lookup(portal_cc_patient_lookup_request: PortalCcPatientLookupRequest):
    return await cc_search_details_by_name_and_dob(
        portal_cc_patient_lookup_request.last_name,
        portal_cc_patient_lookup_request.dob
    )

'''
@router.post("/admin/get_all_test_results", dependencies=[Security(authorize_user, scopes=[p.GET_ALL_TEST_RESULTS])])
async def api_admin_get_all_test_results():
    return await admin_get_all_test_results()
'''