from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Response,
    status,
    Depends, HTTPException)

from ggt.lib.auth import (
    verify_google_idtoken,
    get_current_user)
from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    AUTH_FAILED_MESSAGE
)
from ggt.lib.utils import is_site_admin, is_admin, is_care_provider
from ggt.models.data_models.data_types import (
    PortalUserRoleRequest,
    PortalCcPatientLookupRequest,
    PortalGeneralSearchRequest,
    PortalLocationSearchRequest,
    ScheduleGenerationRule,
    User, GgtLocation, GgtDbLocation, GgtUpdateLocation, LocationToGroupMap, LocationToServiceMap)
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
    get_all_services, get_locations)

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


@router.post("/site-admin/create_location")
async def api_create_location(location: GgtDbLocation, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return create_location(location)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site_admin/location/assign_group")
async def api_assign_group(req: LocationToGroupMap, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return assign_group(req)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site_admin/location/remove_service")
async def api_remove_service(req: LocationToServiceMap, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return remove_service(req)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site_admin/location/assign_service")
async def api_assign_service(req: LocationToServiceMap, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return assign_service(req)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site_admin/location/remove_groups")
async def api_remove_group(req: LocationToGroupMap, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return remove_group(req)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/site_admin/location/get_locations")
async def api_get_locations(user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return get_locations()
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site-admin/update_location")
async def api_update_location(location: GgtUpdateLocation, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return update_location(location)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/site-admin/get_all_groups")
async def api_get_all_groups(user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return get_all_groups()
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/site-admin/get_all_services")
async def api_get_all_services(user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return get_all_services()
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )

'''
@router.post("/site-admin/general_search")
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest,
                                        user: User = Depends(get_current_user)):
    if is_site_admin(user):
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
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )
'''
@router.post("/site-admin/general_search")
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest,
                                        user: User = Depends(get_current_user)):
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


@router.get("/site-admin/generate_schedule/{location_id}")
async def api_generate_schedule(location_id: str, background_tasks: BackgroundTasks,
                                user: User = Depends(get_current_user)):
    if is_site_admin(user):
        background_tasks.add_task(generate_schedule, location_id)
        return {
            STATUS: SUCCESS,
            "description": "Background Task Initiated"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site-admin/generate_all_schedules")
async def api_generate_all_schedules(background_tasks: BackgroundTasks,
                                     user: User = Depends(get_current_user)):
    if is_site_admin(user):
        background_tasks.add_task(generate_all_schedules)
        return {
            STATUS: SUCCESS,
            "description": "Background Task Initiated"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site-admin/location_search")
async def api_site_admin_location_search(portal_location_search: PortalLocationSearchRequest,
                                         user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return site_admin_location_search(
            portal_location_search.account,
            portal_location_search.group_code,
            portal_location_search.site_code
        )
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )



@router.post("/site-admin/add_schedule_generation_rule")
async def api_add_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule,
                                           user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return add_schedule_generation_rule(schedule_generation_rule_request)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site-admin/edit_schedule_generation_rule")
async def api_update_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule,
                                              user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return update_schedule_generation_rule(schedule_generation_rule_request)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/site-admin/delete_schedule_generation_rule/{id}")
async def api_delete_schedule_generation_rule(id: str, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return delete_schedule_generation_rule(id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/site-admin/delete_schedule/{location_id}")
async def api_delete_schedule(location_id: str, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return delete_schedule(location_id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/site-admin/get_schedule_generation_rules/{location_id}")
async def api_delete_schedule_generation_rules(location_id: str, user: User = Depends(get_current_user)):
    if is_site_admin(user):
        return get_schedule_generation_rules(location_id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/contact-center/patient_lookup")
async def api_cc_patient_lookup(portal_cc_patient_lookup_request: PortalCcPatientLookupRequest,
                                user: User = Depends(get_current_user)):
    if is_site_admin(user) or is_care_provider(user):
        return cc_search_details_by_name_and_dob(
            portal_cc_patient_lookup_request.last_name,
            portal_cc_patient_lookup_request.dob
        )
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
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


@router.post("/admin/get_all_test_results")
async def api_admin_get_all_test_results(user: User = Depends(get_current_user)):
    if is_admin(user):
        return admin_get_all_test_results()
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )
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
