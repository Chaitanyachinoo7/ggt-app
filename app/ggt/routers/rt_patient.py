from fastapi import APIRouter, Security

from ggt.lib.auth import authorise_user
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
from ggt.tasks.reminder_sms import (
    task_process_sms_reminders
)

###TODO: Temp
from ggt.models.workflow_models.test_site_admin_flow import (
    site_admin_general_search
)


router = APIRouter()


@router.get("/get_screen_flow_seq/{group_code}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_screen_flow_seq(group_code: str):
    return get_screen_flow_seq(group_code)


@router.post("/verify_phone", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_verify_phone(req: VerifyPhoneRequest):
    return initiate_verification_flow(req.phone_number)


@router.post("/validate_otp", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_validate_otp(req: ValidateOtpRequest):
    return validate_phone_number(
        req.phone_number,
        req.otp
    )


@router.get("/get_available_dates/{group_code}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_available_dates(group_code: str):
    return get_schedule_dates_available(group_code)


@router.get("/get_available_locations/{group_code}/{date}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_available_locations(group_code: str, date: str):
    return get_schedule_locations_available(date, group_code)


# TODO: Radial Search
@router.get("/get_locations_near_me/{lat}/{lng}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{lat}/{lng}/{radius}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{lat}/{lng}/{radius}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations_near_me/{group_code}/{date}/{lat}/{lng}/{radius}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_available_locations(lat: float, lng: float, radius: int = None, group_code: str = None, date: str = None):
    return get_schedule_locations_available_near_lat_lng(date, group_code, lat, lng, radius)


@router.get("/get_available_times/{location_id}/{date}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times(location_id: str, date: str):
    return get_schedule_times_available(
        location_id,
        date
    )


@router.get("/get_available_times/{location_id}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_available_times_for_today(location_id: str):
    return get_schedule_times_available(location_id)


@router.get("/get_locations", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
@router.get("/get_locations/{group_code}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_get_all_available_locations_and_times(group_code: str = None):
    return get_all_available_locations_and_times(group_code)


@router.post("/finalize_registration", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_finalize_registration(finalize_registration_request: FinalizeRegistrationRequest):
    return finalize_registration(finalize_registration_request)


@router.post("/finalize_payment", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_finalize_payment(finalize_payment_request: FinalizePaymentRequest):
    return finalize_payment(finalize_payment_request)


@router.post("/lookup_appointment", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_lookup_appointment(req: LookupAppointmentRequest):
    return lookup_appointment(
        req.appointment_id,
        req.dob
    )


@router.get("/appointment/result/{token}/{dob}", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def api_lookup_test_result(token: str, dob: str):
    return lookup_test_result(
        token,
        dob
    )


@router.get("/appointment/reminders", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
def reminder_sms():
    return task_process_sms_reminders()


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


@router.get("/lookup_appointments_by_phone/{phone_number}/{dob}")
async def api_lookup_appointments_by_phone(phone_number: str, dob: str):
    return site_admin_general_search(
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
