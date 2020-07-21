from fastapi import APIRouter, Request, Response, status

from ggt.models.data_models.data_types import (
    ProviderLoginRequest,
    ProviderPatientCodeRequest,
    ProviderUpdateAppointmentRequest,
    ProviderLookupAppointmentRequest,
    ProviderGetMonthlyCalendarRequest,
    UserRoleRequest
)

from ggt.models.workflow_models.provider_field_testing_flow import (
    provider_login,
    provider_get_workstations,
    provider_lookup_appointment,
    provider_update_appointment,
    provider_get_monthly_calendar,
    provider_positive_result_followup,
    provider_get_user_role,
    provider_get_test_results
)
from ggt.lib.auth import (verify_google_idtoken)
router = APIRouter()


@router.post("/login")
async def api_provider_login(provider_login_request: ProviderLoginRequest):
    return provider_login(
        provider_login_request.token)


@router.get("/get_workstations/{auth_token}")
async def api_provider_get_workstations(request: Request, auth_token: str):
    return provider_get_workstations(
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
        provider_update_appointment_request.action,
        provider_update_appointment_request.workstation_id)


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


@router.post("/get_user_role")
async def get_user_role(user_role_request: UserRoleRequest, request: Request, response: Response):
    if(verify_google_idtoken(request.headers['Authorization'])):
        print(user_role_request.email)
        return provider_get_user_role(
            user_role_request.email)
    else:
        return {
            response.status_code: status.HTTP_401_UNAUTHORIZED
        }


@router.post("/get_admin_test_results")
async def get_test_results(request: Request, response: Response):
    # if(verify_google_idtoken(request.headers['Authorization'])):
    return provider_get_test_results(
    )
    # else:
    #     return {
    #         response.status_code: status.HTTP_401_UNAUTHORIZED
    #     }
