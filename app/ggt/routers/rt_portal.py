from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Response,
    status,
    Security)

from ggt.lib.auth import (
    verify_google_idtoken,
    authorise_user)
from ggt.lib.constants import (
    STATUS,
    SUCCESS
)
from ggt.models.data_models.data_types import (
    PortalUserRoleRequest,
    PortalCcPatientLookupRequest,
    PortalGeneralSearchRequest,
    PortalLocationSearchRequest,
    ScheduleGenerationRule,
    GgtDbLocation, GgtUpdateLocation, LocationToGroupMap, LocationToServiceMap, GgtThirdPartyDbGroup,
    GgtThirdPartyDbUpdateGroup, PermissionsEnum as p)
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
    create_location, get_all_groups, update_location, assign_group, remove_group, assign_service, remove_service,
    get_all_services, get_locations, create_group, update_group)

router = APIRouter()


# TODO review after Auth0 implementation
@router.post("/get_user_role")
async def api_get_user_role(portal_user_role_request: PortalUserRoleRequest,
                            request: Request, response: Response):
    if verify_google_idtoken(request.headers['Authorization']):
        return portal_get_user_role(portal_user_role_request.email)
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }


@router.post("/site-admin/create_location", dependencies=[Security(authorise_user, scopes=[p.CREATE_LOCATION])])
async def api_create_location(location: GgtDbLocation):
    return create_location(location)


@router.post("/site-admin/create_group", dependencies=[Security(authorise_user, scopes=[p.CREATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbGroup):
    return create_group(group)


@router.post("/site-admin/update_group", dependencies=[Security(authorise_user, scopes=[p.UPDATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbUpdateGroup):
    return update_group(group)


@router.post("/site_admin/location/assign_group", dependencies=[Security(authorise_user, scopes=[p.ASSIGN_GROUP])])
async def api_assign_group(req: LocationToGroupMap):
    return assign_group(req)


@router.post("/site_admin/location/remove_service",
             dependencies=[Security(authorise_user, scopes=[p.REMOVE_SERVICE])])
async def api_remove_service(req: LocationToServiceMap):
    return remove_service(req)


@router.post("/site_admin/location/assign_service",
             dependencies=[Security(authorise_user, scopes=[p.ASSIGN_SERVICE])])
async def api_assign_service(req: LocationToServiceMap):
    return assign_service(req)


@router.post("/site_admin/location/remove_groups", dependencies=[Security(authorise_user, scopes=[p.REMOVE_GROUPS])])
async def api_remove_group(req: LocationToGroupMap):
    return remove_group(req)


@router.get("/site_admin/location/get_locations", dependencies=[Security(authorise_user, scopes=[p.GET_LOCATIONS])])
async def api_get_locations():
    return get_locations()


@router.post("/site-admin/update_location", dependencies=[Security(authorise_user, scopes=[p.UPDATE_LOCATION])])
async def api_update_location(location: GgtUpdateLocation):
    return update_location(location)


@router.get("/site-admin/get_all_groups", dependencies=[Security(authorise_user, scopes=[p.GET_ALL_GROUPS])])
async def api_get_all_groups():
    return get_all_groups()


@router.get("/site-admin/get_all_services", dependencies=[Security(authorise_user, scopes=[p.GET_ALL_SERVICES])])
async def api_get_all_services():
    return get_all_services()


@router.post("/site-admin/general_search", dependencies=[Security(authorise_user, scopes=[p.GENERAL_SEARCH])])
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest):
    return site_admin_general_search(
        portal_general_search_request.auth_token,
        portal_general_search_request.first_name,
        portal_general_search_request.middle_name,
        portal_general_search_request.last_name,
        portal_general_search_request.dob,
        portal_general_search_request.phone_number,
        portal_general_search_request.email,
        portal_general_search_request.appointment_id,
        portal_general_search_request.group_code,
        portal_general_search_request.appointment_date,
        portal_general_search_request.location_id
    )


@router.get("/site-admin/generate_schedule/{location_id}",
            dependencies=[Security(authorise_user, scopes=[p.GENERATE_SCHEDULE])])
async def api_generate_schedule(location_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_schedule, location_id)
    return {
        STATUS: SUCCESS,
        "description": "Background Task Initiated"
    }


@router.post("/site-admin/generate_all_schedules",
             dependencies=[Security(authorise_user, scopes=[p.GENERATE_ALL_SCHEDULES])])
async def api_generate_all_schedules(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_all_schedules)
    return {
        STATUS: SUCCESS,
        "description": "Background Task Initiated"
    }


@router.post("/site-admin/location_search", dependencies=[Security(authorise_user, scopes=[p.LOCATION_SEARCH])])
async def api_site_admin_location_search(portal_location_search: PortalLocationSearchRequest):
    return site_admin_location_search(
        portal_location_search.account,
        portal_location_search.group_code,
        portal_location_search.site_code
    )


@router.post("/site-admin/add_schedule_generation_rule",
             dependencies=[Security(authorise_user, scopes=[p.ADD_SCHEDULE_GENERATION_RULE])])
async def api_add_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return add_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/edit_schedule_generation_rule",
             dependencies=[Security(authorise_user, scopes=[p.EDIT_SCHEDULE_GENERATION_RULE])])
async def api_update_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return update_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/delete_schedule_generation_rule/{id}",
             dependencies=[Security(authorise_user, scopes=[p.DELETE_SCHEDULE_GENERATION_RULE])])
async def api_delete_schedule_generation_rule(id: str):
    return delete_schedule_generation_rule(id)


@router.get("/site-admin/delete_schedule/{location_id}",
            dependencies=[Security(authorise_user, scopes=[p.DELETE_SCHEDULE])])
async def api_delete_schedule(location_id: str):
    return delete_schedule(location_id)


@router.get("/site-admin/get_schedule_generation_rules/{location_id}",
            dependencies=[Security(authorise_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_delete_schedule_generation_rules(location_id: str):
    return get_schedule_generation_rules(location_id)


@router.post("/contact-center/patient_lookup", dependencies=[Security(authorise_user, scopes=[p.PATIENT_LOOKUP])])
async def api_cc_patient_lookup(portal_cc_patient_lookup_request: PortalCcPatientLookupRequest):
    return cc_search_details_by_name_and_dob(
        portal_cc_patient_lookup_request.last_name,
        portal_cc_patient_lookup_request.dob
    )

    '''
    if(verify_google_idtoken(request.headers['Authorization'])):
        return cc_search_details_by_name_and_dob(
            portal_cc_patient_lookup_request.last_name, 
            portal_cc_patient_lookup_request.dob
        )
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }
    '''


@router.post("/admin/get_all_test_results", dependencies=[Security(authorise_user, scopes=[p.GET_ALL_TEST_RESULTS])])
async def api_admin_get_all_test_results():
    return admin_get_all_test_results()

    '''
    if(verify_google_idtoken(request.headers['Authorization'])):
        return admin_get_all_test_results()
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }
    '''


'''    ProviderPatientCodeRequest,

    ProviderGetMonthlyCalendarRequest,

'''
'''
    provider_get_monthly_calendar,
    provider_positive_result_followup,
    provider_get_user_role,
    provider_get_test_results


'''

'''
@router.post("/login")
async def api_cc_login(cc_login_request: CcLoginRequest):
    return cc_login(
        cc_login_request.token)


@router.post("/patient_search")
async def api_cc_patient_search(cc_patient_search_request: CcPatientSearchRequest):
    return cc_patient_search(
        cc_patient_search_request.auth_token,
        cc_patient_search_request.last_name,
        cc_patient_search_request.dob)


@router.post("/view_test_details")
async def api_cc_view_test_details(cc_test_lookup_request: CcTestLookupRequest):
    return cc_view_test_details(
        cc_test_lookup_request.auth_token,
        cc_test_lookup_request.test_id
    )



@router.post("/sendsms")
async def api_cc_send_sms(patient_lookup_request: CcPatientLookupRequest):
    try:
        search_result = cc_patient_lookup(
            patient_lookup_request.last_name, patient_lookup_request.dob
        )
        print(search_result)
        if search_result['status'] == SUCCESS and search_result['results'][0]['test_result'] == "neg":
            send_sms("+14372309014", "Hi There")
            return {STATUS: SUCCESS}
        else:
            return {STATUS: "failure"}
    except Exception as err:
        print(err)
'''
'''
@router.post("/get_monthly_calendar")
async def api_provider_get_monthly_calendar(provider_get_monthly_calendar_request: ProviderGetMonthlyCalendarRequest,
                                            request: Request, response: Response
                                            ):
    try:
        if(verify_google_idtoken(request.headers['Authorization'])):
            print(provider_get_monthly_calendar_request)
            return provider_get_monthly_calendar(
                provider_get_monthly_calendar_request.auth_token,
                provider_get_monthly_calendar_request.date,
                provider_get_monthly_calendar_request.location_id)
        else:
            return {
                response.status_code: status.HTTP_401_UNAUTHORIZED
            }
    except Exception as err:
        print(err)


@router.get("/positive_result_followup")
async def api_provider_positive_result_followup():
    return provider_positive_result_followup()




@router.post("/get_admin_test_results")
async def get_test_results(request: Request, response: Response):
    if(verify_google_idtoken(request.headers['Authorization'])):
        return provider_get_test_results(
        )
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }
'''
