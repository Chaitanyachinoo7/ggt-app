from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.data_models.data_types import (
    ValidateOtpRequest,
    VerifyPhoneRequest,
    FinalizeRegistrationRequest,
    FinalizePaymentRequest,
    LookupAppointmentRequest,
    VerifyExistingPatientRequest,
    PermissionsEnum as p
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
    get_all_available_locations_and_times
)

# TODO: [GGT-193] Move this to a dedicated API
from ggt.models.workflow_models.test_site_admin_flow import (
    site_admin_general_search
)


router = APIRouter()


@router.get("/get_screen_flow_seq/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_screen_flow_seq(group_code: str):
    return await get_screen_flow_seq(group_code)


@router.post("/verify_phone", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_verify_phone(req: VerifyPhoneRequest):
    return await initiate_verification_flow(req.phone_number)


@router.post("/validate_otp", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_validate_otp(req: ValidateOtpRequest):
    return await validate_phone_number(
        req.phone_number,
        req.otp
    )


@router.get("/get_available_dates/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_dates(group_code: str):
    return await get_schedule_dates_available(group_code)


@router.get("/get_available_locations/{group_code}/{date}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_locations(group_code: str, date: str):
    return await get_schedule_locations_available(date, group_code)


@router.get("/get_locations_near_me/{lat}/{lng}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{date}/{lat}/{lng}/{radius}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_locations(lat: float, lng: float, radius: int = None, group_code: str = None, date: str = None):
    # TODO: [GGT-194] temp fix until map zoom levels are in place
    radius = 100000
    return await get_schedule_locations_available_near_lat_lng(date, group_code, lat, lng, radius)


@router.get("/get_available_times/{location_id}/{date}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times(location_id: str, date: str):
    return await get_schedule_times_available(
        location_id,
        date
    )


@router.get("/get_available_times/{location_id}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times_for_today(location_id: str):
    return await get_schedule_times_available(location_id)


@router.get("/get_locations", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations/{group_code}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_all_available_locations_and_times(group_code: str = None):
    return await get_all_available_locations_and_times(group_code)


@router.post("/finalize_registration", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_registration(finalize_registration_request: FinalizeRegistrationRequest):
    return await finalize_registration(finalize_registration_request)


@router.post("/finalize_payment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_finalize_payment(finalize_payment_request: FinalizePaymentRequest):
    return await finalize_payment(finalize_payment_request)


@router.post("/lookup_appointment", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_appointment(req: LookupAppointmentRequest):
    return await lookup_appointment(
        req.appointment_id,
        req.dob
    )


@router.get("/appointment/result/{token}/{dob}", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_lookup_test_result(token: str, dob: str):
    return await lookup_test_result(
        token,
        dob
    )


@router.post("/verify_existing_patient")
async def api_verify_existing_patient(req: VerifyExistingPatientRequest):
    return await verify_existing_patient(
        req.phone_number,
        req.dob
    )


@router.get("/lookup_patient/{phone_number}")
async def api_verify_existing_patient(phone_number: str):
    return await verify_existing_patient(
        phone_number,
        None
    )


@router.get("/lookup_appointments_by_phone/{phone_number}/{dob}")
async def api_lookup_appointments_by_phone(phone_number: str, dob: str):
    return await site_admin_general_search(
        '',
        '',
        '',
        dob,
        phone_number,
        '',
        '',
        '',
        '',
        ''
    )
