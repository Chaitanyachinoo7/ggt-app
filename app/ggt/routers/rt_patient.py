#from ggt.lib.utils import (log_generic)
#from datetime import date

from fastapi import APIRouter, Request
from typing import Optional

from ggt.models.data_models.data_types import (
    ValidateOtpRequest,
    VerifyPhoneRequest,
    FinalizeRegistrationRequest,
    FinalizePaymentRequest,
    LookupAppointmentRequest
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
    lookup_appointment,
    lookup_test_result,
    get_all_available_locations_and_times
)

from ggt.tasks.reminder_sms import(
    task_process_sms_reminders
)


router = APIRouter()


@router.get("/get_screen_flow_seq/{group_code}")
async def api_get_screen_flow_seq(request: Request, group_code: str):
    return get_screen_flow_seq(group_code)


@router.post("/verify_phone")
async def api_verify_phone(verify_phone_request: VerifyPhoneRequest):
    return initiate_verification_flow(
        verify_phone_request.phone_number)


@router.post("/validate_otp")
async def api_validate_otp(validate_otp_request: ValidateOtpRequest):
    return validate_phone_number(
        validate_otp_request.phone_number,
        validate_otp_request.otp)


# TODO: Deprecate soon
'''
@router.get("/get_available_dates")
async def xxxx_api_get_available_dates(request: Request):
    return get_schedule_dates_available()
'''


@router.get("/get_available_dates/{group_code}")
async def api_get_available_dates(request: Request, group_code: str):
    return get_schedule_dates_available(group_code)


@router.get("/get_available_locations/{group_code}/{date}")
async def api_get_available_locations(request: Request, group_code: str, date: str):
    # TODO: Look for _DEFAULT_ group code for regular
    return get_schedule_locations_available(date, group_code)


@router.get("/get_available_times/{location_id}/{date}")
async def api_get_available_times(location_id: str, date: str):
    return get_schedule_times_available(location_id, date)


@router.get("/get_available_times/{location_id}")
async def api_get_available_times_for_today(location_id: str):
    return get_schedule_times_available(location_id)


@router.get("/get_locations")
@router.get("/get_locations/{group_code}")
async def api_get_all_available_locations_and_times(group_code: str = None):
    return get_all_available_locations_and_times(group_code)


@router.post("/finalize_registration")
async def api_finalize_registration(finalize_registration_request: FinalizeRegistrationRequest):
    return finalize_registration(finalize_registration_request)


@router.post("/finalize_payment")
async def api_finalize_payment(finalize_payment_request: FinalizePaymentRequest):
    return finalize_payment(finalize_payment_request)


@router.post("/lookup_appointment")
async def api_lookup_appointment(lookup_appointment_request: LookupAppointmentRequest):
    return lookup_appointment(lookup_appointment_request.appointment_id, lookup_appointment_request.dob)

'''
@router.get("/lookup_appointment/{appointment_id}/{dob}")
async def api_lookup_appointment(appointment_id: str, dob: str):
    return lookup_appointment(appointment_id, dob)
'''

@router.get("/appointment/result/{token}/{dob}")
async def api_lookup_test_result(token: str, dob: str):
    return lookup_test_result(token, dob)

@router.get("/appointment/reminders")
def reminder_sms():
    return task_process_sms_reminders()