from fastapi import APIRouter, Request
from typing import Optional

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.models.data_models.data_types import (
    ValidateOtpRequest,
    VerifyPhoneRequest,
    FinalizeRegistrationRequest,
    FinalizePaymentRequest,
    LookupAppointmentRequest,
    VerifyExistingPatientRequest
)

from ggt.models.workflow_models.patient_portal_flow import (
    verify_existing_patient
)


from ggt.tasks.reminder_sms import(
    task_process_sms_reminders
)

router = APIRouter()


@router.get("/get_screen_flow_seq/{group_code}")
async def api_get_screen_flow_seq(request: Request, group_code: str):
    return get_screen_flow_seq(group_code)


@router.post("/verify_phone")
async def api_verify_phone(req: VerifyPhoneRequest):
    return initiate_verification_flow(req.phone_number)


@router.post("/validate_otp")
async def api_validate_otp(req: ValidateOtpRequest):
    return validate_phone_number(
        req.phone_number,
        req.otp
    )


@router.get("/get_available_dates/{group_code}")
async def api_get_available_dates(request: Request, group_code: str):
    return get_schedule_dates_available(group_code)


@router.get("/get_available_locations/{group_code}/{date}")
async def api_get_available_locations(request: Request, group_code: str, date: str):
    return get_schedule_locations_available(
        date,
        group_code
    )


# TODO: Radial Search
@router.get("/get_locations_near_me/{lat}/{lng}")
@router.get("/get_locations_near_me/{lat}/{lng}/{radius}")
@router.get("/get_locations_near_me/{group_code}/{date}/{lat}/{lng}/{radius}")
async def api_get_available_locations(request: Request, lat: float, lng: float, radius: int = None, group_code: str = None, date: str = None):
    return get_schedule_locations_available_near_lat_lng(
        date,
        group_code,
        lat,
        lng,
        radius
    )


@router.get("/get_available_times/{location_id}/{date}")
async def api_get_available_times(location_id: str, date: str):
    return get_schedule_times_available(
        location_id,
        date
    )


@router.get("/get_available_times/{location_id}")
async def api_get_available_times_for_today(location_id: str):
    return get_schedule_times_available(location_id)


@router.get("/get_locations")
@router.get("/get_locations/{group_code}")
async def api_get_all_available_locations_and_times(group_code: str = None):
    return get_all_available_locations_and_times(group_code)


@router.post("/finalize_registration")
async def api_finalize_registration(req: FinalizeRegistrationRequest):
    return finalize_registration(req)


@router.post("/finalize_payment")
async def api_finalize_payment(req: FinalizePaymentRequest):
    return finalize_payment(req)


@router.post("/lookup_appointment")
async def api_lookup_appointment(req: LookupAppointmentRequest):
    return lookup_appointment(
        req.appointment_id,
        req.dob
    )

'''
@router.get("/lookup_appointment/{appointment_id}/{dob}")
async def api_lookup_appointment(appointment_id: str, dob: str):
    return lookup_appointment(appointment_id, dob)
'''


@router.get("/appointment/result/{token}/{dob}")
async def api_lookup_test_result(token: str, dob: str):
    return lookup_test_result(
        token,
        dob
    )


@router.get("/appointment/reminders")
async def api_reminder_sms():
    return task_process_sms_reminders()


@router.post("/verify_existing_patient")
async def api_verify_existing_patient(req: VerifyExistingPatientRequest):
    return verify_existing_patient(
        req.phone_number,
        req.dob
    )
