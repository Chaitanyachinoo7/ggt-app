from fastapi import APIRouter, Request

from ggt.models.data_models.data_types import (
    ProviderLoginRequest, 
    ProviderPatientCodeRequest, 
    ProviderUpdateAppointmentRequest, 
    ProviderLookupAppointmentRequest,
    ProviderGetMonthlyCalendarRequest
)

from ggt.models.workflow_models.provider_field_testing_flow import (
    provider_login, 
    provider_get_testing_locations, 
    provider_lookup_appointment, 
    provider_update_appointment,
    provider_get_monthly_calendar
)

router = APIRouter()


@router.post("/login")
async def api_provider_login(provider_login_request: ProviderLoginRequest):
    return provider_login(
            provider_login_request.token)


@router.get("/testing_locations/{auth_token}")
async def api_provider_get_testing_locations(request: Request, auth_token: str):
    return provider_get_testing_locations(
            auth_token)


@router.post("/lookup_appointment")
async def api_provider_lookup_appointment(provider_lookup_appointment_request: ProviderLookupAppointmentRequest):
    return provider_lookup_appointment(
            provider_lookup_appointment_request.token, 
            provider_lookup_appointment_request.appointment_id)


@router.post("/update_appointment")
async def api_provider_update_appointment(provider_update_appointment_request: ProviderUpdateAppointmentRequest):
    return provider_update_appointment(
            provider_update_appointment_request.auth_token, 
            provider_update_appointment_request.appointment_id, 
            provider_update_appointment_request.action)

@router.post("/get_monthly_calendar")
async def api_provider_get_monthly_calendar(provider_get_monthly_calendar_request: ProviderGetMonthlyCalendarRequest):
    print(provider_get_monthly_calendar_request)
    return provider_get_monthly_calendar(
            provider_get_monthly_calendar_request.auth_token, 
            provider_get_monthly_calendar_request.date, 
            provider_get_monthly_calendar_request.location_id)