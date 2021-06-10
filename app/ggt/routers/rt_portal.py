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
    PermissionsEnum as p,
    PortalAdminGetF11Request,
    PortalAdminGetVaccineConsentFormRequest,
    PortalVaxWaitlistSearchRequest,
    PortalVaxRegisteredWaitAroundLocationRequest, VaxCertificate, LookupCertificateRequest, UpdatePatientInfoCert,
    UpdateCertInfo, UpdateCertImage, VerifyCertificateRequest, LookupUnverifiedCertificateRequest,
    DeleteCertificateRequest, VaxYesActivity
)
from ggt.models.workflow_models.admin_flow import (
    admin_get_all_test_results
)
from ggt.models.workflow_models.contact_center_flow import (
    cc_search_details_by_name_and_dob
)
from ggt.models.workflow_models.patient_test_scheduling_flow import get_vax_certificate
from ggt.models.workflow_models.portal_general_flow import (
    portal_get_user_role
)
from ggt.models.workflow_models.clinical_test_site_admin_flow import (
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
    update_group, get_states,
    site_admin_get_f11,
    site_admin_get_consent_forms,
    site_admin_vax_waitlist_search,
    site_admin_vax_registered_waitlist_around_location, add_vax_certificate, lookup_certificate,
    update_patient_ifo_cert, update_cert_info, update_cert_image, delete_certificate,
    verify_certificate, lookup_unverified_certificate, get_certificate_stats, get_ocr, reject_certificate,
    vax_yes_activity
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


@router.post("/site-admin/create_location")
async def api_create_location(location: GgtDbLocation, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return create_location(location, user)


@router.get("/site-admin/get_states", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_get_states():
    return get_states()


@router.post("/site-admin/create_group", dependencies=[Security(authorize_user, scopes=[p.CREATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbGroup):
    return create_group(group)


@router.post("/site-admin/update_group", dependencies=[Security(authorize_user, scopes=[p.UPDATE_GROUP])])
async def api_create_group(group: GgtThirdPartyDbUpdateGroup):
    return update_group(group)


@router.post("/site_admin/location/assign_group", dependencies=[Security(authorize_user, scopes=[p.ASSIGN_GROUP])])
async def api_assign_group(req: LocationToGroupMap):
    return assign_group(req)


@router.post("/site_admin/location/remove_service",
             dependencies=[Security(authorize_user, scopes=[p.REMOVE_SERVICE])])
async def api_remove_service(req: LocationToServiceMap):
    return remove_service(req)


@router.post("/site_admin/location/assign_service",
             dependencies=[Security(authorize_user, scopes=[p.ASSIGN_SERVICE])])
async def api_assign_service(req: LocationToServiceMap):
    return assign_service(req)


@router.post("/site_admin/location/remove_groups", dependencies=[Security(authorize_user, scopes=[p.REMOVE_GROUPS])])
async def api_remove_group(req: LocationToGroupMap):
    return remove_group(req)


@router.get("/site_admin/location/get_locations")
async def api_get_locations(user=Security(authorize_user, scopes=[p.GET_LOCATIONS])):
    return get_locations(user)


@router.post("/site-admin/update_location")
async def api_update_location(location: GgtUpdateLocation, user=Security(authorize_user, scopes=[p.UPDATE_LOCATION])):
    return update_location(location, user)


@router.get("/site-admin/get_all_groups")
async def api_get_all_groups(user=Security(authorize_user, scopes=[p.GET_ALL_GROUPS])):
    return get_all_groups(user)


@router.get("/site-admin/get_all_services", dependencies=[Security(authorize_user, scopes=[p.GET_ALL_SERVICES])])
async def api_get_all_services():
    return get_all_services()


@router.post("/site-admin/general_search")
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest,
                                        user=Security(authorize_user, scopes=[p.GENERAL_SEARCH])):
    return site_admin_general_search(
        user,
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
        portal_general_search_request.vial_id,
        portal_general_search_request.sort_field,
        portal_general_search_request.sort_type
    )


@router.get("/site-admin/get_appointment/{appointment_id}")
async def api_site_admin_general_search(appointment_id: int,
                                        user=Security(authorize_user, scopes=[p.GENERAL_SEARCH])):
    return site_admin_general_search(
        user,
        "",
        "",
        "",
        "",
        "",
        "",
        appointment_id,
        "",
        "",
        ""
    )


@router.post("/site-admin/m_to_m/general_search")
async def api_site_admin_general_search(portal_general_search_request: PortalGeneralSearchRequest,
                                        user=Security(authorize_user, scopes=[p.GENERAL_SEARCH])):
    return site_admin_general_search(
        user,
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
        portal_general_search_request.vial_id,
        portal_general_search_request.sort_field,
        portal_general_search_request.sort_type,
        is_patient=True
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


@router.post("/site-admin/location_search")
async def api_site_admin_location_search(portal_location_search: PortalLocationSearchRequest, user=Security(authorize_user, scopes=[p.LOCATION_SEARCH])):
    return site_admin_location_search(
        portal_location_search.account,
        portal_location_search.group_code,
        portal_location_search.site_code,
        portal_location_search.location_name,
        portal_location_search.st,
        user
    )


@router.get("/site-admin/get_location/{location_id}")
async def api_site_admin_location_search(location_id: int, user=Security(authorize_user, scopes=[p.LOCATION_SEARCH])):
    return site_admin_location_search(
        '',
        '',
        '',
        '',
        '',
        user,
        location_id=location_id
    )


@router.post("/site-admin/add_schedule_generation_rule",
             dependencies=[Security(authorize_user, scopes=[p.ADD_SCHEDULE_GENERATION_RULE])])
async def api_add_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return add_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/edit_schedule_generation_rule",
             dependencies=[Security(authorize_user, scopes=[p.EDIT_SCHEDULE_GENERATION_RULE])])
async def api_update_schedule_generation_rule(schedule_generation_rule_request: ScheduleGenerationRule):
    return update_schedule_generation_rule(schedule_generation_rule_request)


@router.post("/site-admin/delete_schedule_generation_rule/{id}",
             dependencies=[Security(authorize_user, scopes=[p.DELETE_SCHEDULE_GENERATION_RULE])])
async def api_delete_schedule_generation_rule(id: str):
    return delete_schedule_generation_rule(id)


@router.get("/site-admin/delete_schedule/{location_id}",
            dependencies=[Security(authorize_user, scopes=[p.DELETE_SCHEDULE])])
async def api_delete_schedule(location_id: str):
    return delete_schedule(location_id)


@router.get("/site-admin/get_schedule_generation_rules/{location_id}",
            dependencies=[Security(authorize_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_delete_schedule_generation_rules(location_id: str):
    return get_schedule_generation_rules(location_id)


@router.post("/contact-center/patient_lookup", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
async def api_cc_patient_lookup(portal_cc_patient_lookup_request: PortalCcPatientLookupRequest):
    return cc_search_details_by_name_and_dob(
        portal_cc_patient_lookup_request.last_name,
        portal_cc_patient_lookup_request.dob
    )


@router.post("/site-admin/lookup_certificate")
async def api_lookup_certificate(req: LookupCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP])):
    return lookup_certificate(
        req.first_name,
        req.last_name,
        req.dob,
        req.phone_number,
        user['sub']
    )


@router.post("/site-admin/lookup_unverified_certificate")
async def api_lookup_unverified_certificate(req: LookupUnverifiedCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP])):
    return lookup_unverified_certificate(
        req.first_name,
        req.last_name,
        req.dob,
        req.phone_number,
        req.limit,
        req.offset,
        user['sub'],
        1
    )


@router.post("/site-admin/lookup_unverified_certificate_v2")
async def api_lookup_unverified_certificate_v2(req: LookupUnverifiedCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])):
    return lookup_unverified_certificate(
        req.first_name,
        req.last_name,
        req.dob,
        req.phone_number,
        req.limit,
        req.offset,
        user['sub'],
        2
    )


@router.post("/site-admin/update_patient_info_cert")
async def api_update_patient_ifo_cert(req: UpdatePatientInfoCert, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])):
    return update_patient_ifo_cert(
        req.id,
        req.first_name,
        req.last_name,
        req.dob,
        req.phone_number,
        user
    )


@router.post("/site-admin/delete_certificate")
async def api_delete_certificate(req: DeleteCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP])):
    return delete_certificate(req.cert_id, req.notify_customer, user)


@router.post("/site-admin/reject_certificate")
async def api_reject_certificate(req: DeleteCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])):
    return reject_certificate(req.cert_id, req.notify_customer, user)


@router.post("/site-admin/update_cert_info")
async def api_update_cert_info(req: UpdateCertInfo, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])):
    return update_cert_info(
        req.id,
        req.service_code,
        req.lot_no,
        req.vax_date,
        user['sub']
    )


@router.post("/site-admin/update_cert_image")
async def api_update_cert_image(req: UpdateCertImage, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP])):
    return update_cert_image(
        req.patient_id,
        req.cert_id,
        req.image,
        user['sub']
    )


@router.post("/site-admin/generate_vaccine_forms_brownwood", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
def generate_vaccine_forms_brownwood(portal_admin_get_f11_request: PortalAdminGetF11Request):
    return site_admin_get_f11(portal_admin_get_f11_request.appointment_ids)

'''
@router.post("/admin/get_all_test_results", dependencies=[Security(authorize_user, scopes=[p.GET_ALL_TEST_RESULTS])])
async def api_admin_get_all_test_results():
    return admin_get_all_test_results()
'''


@router.post("/site-admin/vax_waitlist_search", dependencies=[Security(authorize_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_site_admin_vax_waitlist_search(portal_vax_waitlist_search: PortalVaxWaitlistSearchRequest):
    return site_admin_vax_waitlist_search(portal_vax_waitlist_search)


@router.post("/site-admin/get_vax_registered_waitlist_around_location", dependencies=[Security(authorize_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_site_admin_vax_registered_waitlist_around_location(vax_registered_waitlist_around_location_request: PortalVaxRegisteredWaitAroundLocationRequest):
    return site_admin_vax_registered_waitlist_around_location(vax_registered_waitlist_around_location_request)


@router.post("/site-admin/add-vax-certificate", dependencies=[Security(authorize_user, scopes=[p.GET_SCHEDULE_GENERATION_RULES])])
async def api_add_vax_certificate(vax_certificate: VaxCertificate):
    return add_vax_certificate(vax_certificate)


@router.get("/vax_certificate/{patient_id}/{certificate_id}", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
def api_get_vax_certificate(patient_id: str, certificate_id: str):
    return get_vax_certificate(patient_id, certificate_id, pass_through=True)


@router.post("/site-admin/verify_certificate")
async def api_verify_certificate(req: VerifyCertificateRequest, user=Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])):
    return verify_certificate(
        req.cert_id,
        req.verification_level,
        user
    )


@router.get("/site-admin/get_certificate_stats", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP, 'external_verify'])])
async def api_get_certificate_stats():
    return get_certificate_stats()


@router.get("/site-admin/ocr", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
async def api_get_ocr(patient_id, cert_id):
    return get_ocr(patient_id, cert_id)


@router.post("/site-admin/vax_yes_activity", dependencies=[Security(authorize_user, scopes=[p.PATIENT_LOOKUP])])
async def api_vax_yes_activity(req: VaxYesActivity):
    return vax_yes_activity(req.certificate_id, req.phone_number)