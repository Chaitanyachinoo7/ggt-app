from fastapi import APIRouter, Security

from cachetools import cached, LRUCache, TTLCache

from ggt.lib.auth import authorize_user
from ggt.models.data_models.data_types import (
    ValidateOtpRequest,
    VerifyPhoneRequest,
    FinalizeRegistrationRequest,
    FinalizePaymentRequest,
    LookupAppointmentRequest,
    VerifyExistingPatientRequest,
    PermissionsEnum as p,
    InsuranceEligibilityRequest,
    InsurancePayersListRequest, SecondAvailableDate, FinalizeGGVRegistrationRequest, FinalizeGGVPreRegistrationRequest,
    PatientAppointmentLookup, VerificationToken, UpdateFirstAppointment, SecondSlotReschedule, UpdateSecondAppointment,
    LookupGGVCertificateRequest, LookupGGVWalletPassRequest, LookupGGVAddVaxCertRequest, PassVerificationRequest,
    UpdateAndroidPassRequest
)

from ggt.models.workflow_models.patient_portal_flow import (
    verify_existing_patient
)

from ggt.models.workflow_models.patient_test_scheduling_flow import (
    get_screen_flow_seq,
    initiate_verification_flow,
    validate_phone_number,
    finalize_registration,
    finalize_payment,
    get_schedule_dates_available,
    get_schedule_times_available,
    get_schedule_locations_available,
    get_schedule_locations_available_near_lat_lng,
    lookup_appointment,
    lookup_test_result,
    get_all_available_locations_and_times,
    insurance_eligibility, get_ggv_schedule_locations_available,
    insurance_search_payer, get_ggv_screen_flow_seq, get_second_shot_available_times, ggv_finalize_registration,
    get_ggv_schedule_times_available, ggv_finalize_pre_registration, cache_test, verify_verification_token,
    reschedule_first_appointment, get_second_slot_reschedule_dates, reschedule_second_appointment,
    get_ggv_schedule_dates_available, lookup_certificate, get_vax_certificate, get_wallet_pass, call_non_sms_phone, get_add_vax_certificate,
    pass_verification, update_android_pass
)

# TODO: [GGT-193] Move this to a dedicated API
from ggt.models.workflow_models.clinical_test_site_admin_flow import (
    site_admin_general_search, get_all_services, get_all_services_patient
)


router = APIRouter()


@router.get("/ggv/get_screen_flow_seq/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_get_screen_flow_seq(group_code: str):
    return get_ggv_screen_flow_seq(group_code)


@router.get("/ggv/get_available_locations/{group_code}/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_get_available_locations(group_code: str, lat: float, lng: float, radius: int):
    return get_ggv_schedule_locations_available(group_code, lat, lng, radius)


@router.post("/ggv/get_second_shot_available_times", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_second_shot_available_times(req: SecondAvailableDate):
    return get_second_shot_available_times(req)


@router.get("/ggv/get_available_times/{location_id}/{date}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_get_available_times_for_today(location_id: str, date: str):
    return get_ggv_schedule_times_available(
        location_id,
        date
    )


@router.post("/ggv/get_second_slot_reschedule_dates", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_second_slot_reschedule_dates(req: SecondSlotReschedule):
    return get_second_slot_reschedule_dates(
        req.location_id,
        req.first_appointment_date
    )


@router.post("/ggv/finalize_registration", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_finalize_registration(finalize_registration_request: FinalizeGGVRegistrationRequest):
    return ggv_finalize_registration(finalize_registration_request)


@router.post("/ggv/finalize_pre_registration", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_finalize_pre_registration(finalize_registration_request: FinalizeGGVPreRegistrationRequest):
    return ggv_finalize_pre_registration(finalize_registration_request)


@router.get("/get_screen_flow_seq/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_screen_flow_seq(group_code: str):
    return get_screen_flow_seq(group_code)


@router.get("/get_screen_flow_seq/{group_code}/{country_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_screen_flow_seq_with_country_code(group_code: str, country_code: str):
    return get_screen_flow_seq(group_code, country_code)


@router.post("/verify_phone", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_verify_phone(req: VerifyPhoneRequest):
    return initiate_verification_flow(req.phone_number, req.has_sms)


@router.post("/ggv/reschedule_first_appointment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_reschedule_first_appointment(req: UpdateFirstAppointment):
    return reschedule_first_appointment(req)


@router.post("/ggv/reschedule_second_appointment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_reschedule_second_appointment(req: UpdateSecondAppointment):
    return reschedule_second_appointment(req)


@router.post("/validate_otp", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_validate_otp(req: ValidateOtpRequest):
    return validate_phone_number(
        req.phone_number,
        req.otp
    )


@router.get("/get_available_dates/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_dates(group_code: str):
    return get_schedule_dates_available(group_code)


@router.get("/ggv/get_available_dates/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_ggv_get_available_dates(group_code: str):
    return get_ggv_schedule_dates_available(group_code)


@router.get("/get_available_locations/{group_code}/{date}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_locations(group_code: str, date: str):
    return get_schedule_locations_available(date, group_code)


@router.get("/get_locations_near_me/{lat}/{lng}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{date}/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@cached(cache=TTLCache(maxsize=1024, ttl=180))
def api_get_available_locations(lat: float, lng: float, radius: int = None, group_code: str = None, date: str = None):
    # TODO: [GGT-194] temp fix until map zoom levels are in place
    radius = 100000
    return get_schedule_locations_available_near_lat_lng(date, group_code, lat, lng, radius)


@router.get("/get_available_times/{location_id}/{date}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times(location_id: str, date: str):
    return get_schedule_times_available(
        location_id,
        date
    )


@router.get("/get_available_times/{location_id}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times_for_today(location_id: str):
    return get_schedule_times_available(location_id)


@router.get("/get_locations", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_all_available_locations_and_times(group_code: str = None):
    return get_all_available_locations_and_times(group_code)


@router.post("/finalize_registration", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_registration(finalize_registration_request: FinalizeRegistrationRequest):
    return finalize_registration(finalize_registration_request)


@router.post("/finalize_payment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_payment(finalize_payment_request: FinalizePaymentRequest):
    return finalize_payment(finalize_payment_request)


@router.post("/lookup_appointment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_appointment(req: LookupAppointmentRequest):
    return lookup_appointment(
        req.appointment_id,
        req.dob
    )


@router.post("/ggv/lookup_certificate", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_certificate(req: LookupGGVCertificateRequest):
    return lookup_certificate(
        req.phone_number,
        req.dob,
        req.first_name,
        req.last_name,
        req.token
    )


@router.get("/get_all_services", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_all_services():
    return get_all_services_patient()


@router.get("/appointment/result/{token}/{dob}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_test_result(token: str, dob: str):
    return lookup_test_result(
        token,
        dob
    )


@router.post("/verify_existing_patient")
async def api_verify_existing_patient(req: VerifyExistingPatientRequest):
    return verify_existing_patient(
        req.phone_number,
        req.dob
    )


@router.get("/lookup_patient/{phone_number}")
async def api_verify_existing_patient(phone_number: str):
    return verify_existing_patient(
        phone_number,
        None
    )

#TODO: Calling this API is dangerous, create dedicated much more restricted API that is geared towards a single user.
#Validate user token and restrict access to a single patient by comparing other elements in the result
@router.get("/lookup_appointments_by_phone/{phone_number}/{dob}")
async def api_lookup_appointments_by_phone(phone_number: str, dob: str):
    return {
       'status': 'failed'
    }
    # return site_admin_general_search(
    #     '',
    #     '',
    #     '',
    #     dob,
    #     phone_number,
    #     '',
    #     '',
    #     '',
    #     '',
    #     ''
    # )


@router.post("/get_appointments_by_phone")
async def api_get_appointments_by_phone(req: PatientAppointmentLookup):
    return site_admin_general_search(
        None,
        req.first_name,
        '',
        req.last_name,
        req.dob,
        req.phone_number,
        '',
        '',
        '',
        '',
        '',
        group_vax_results=True,
        token=req.token,
        is_patient=True
    )


@router.post("/insurance_eligibility")
def api_insurance_eligibility(req: InsuranceEligibilityRequest):
    return insurance_eligibility(req)


@router.post("/search_payers_list")
def api_insurance_search_payer(req: InsurancePayersListRequest):
    return insurance_search_payer(req)


@router.get("/cache_test/{t_id}")
def api_cache_test(t_id: int):
    return cache_test(t_id)


@router.post("/verify_verification_token")
def api_verify_verification_token(toke_verification_request: VerificationToken):
    return verify_verification_token(toke_verification_request)


@router.get("/vax_certificate/{patient_id}/{certificate_id}")
def api_get_vax_certificate(patient_id: str, certificate_id: str):
    return get_vax_certificate(patient_id, certificate_id)


@router.post("/vax_wallet_pass")
def api_wallet_pass(req: LookupGGVWalletPassRequest):
    return get_wallet_pass(req)


@router.post("/call_non_sms_phone")
def api_call_non_sms_phone(phone_number):
    return call_non_sms_phone(phone_number)


@router.post("/add_vax_certificate")
def api_add_vax_certificate(req: LookupGGVAddVaxCertRequest):
    return get_add_vax_certificate(req)

@router.post("/pass_verification/")
def api_pass_verification(pass_verification_request: PassVerificationRequest):
    return pass_verification(pass_verification_request)

# @router.post("/update_android_pass/")
# def api_update_android_pass(update_android_pass_request: UpdateAndroidPassRequest):
#     return update_android_pass(update_android_pass_request)