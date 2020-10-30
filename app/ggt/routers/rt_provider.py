from fastapi import APIRouter, Request, Depends, HTTPException

from ggt.lib.auth import get_current_user

from ggt.lib.utils import is_clinical_provider

from ggt.models.data_models.data_types import (
    ProviderLoginRequest,
    ProviderUpdateAppointmentRequest,
    ProviderLookupAppointmentRequest,
    ScanLabelRequest,
    User)

from ggt.models.workflow_models.provider_field_testing_flow import (
    provider_login,
    provider_get_workstations,
    provider_lookup_appointment,
    provider_update_appointment,
    scan_label
)

from ggt.lib.constants import (
    AUTH_FAILED_MESSAGE
)

router = APIRouter()


@router.post("/login")
async def api_provider_login(provider_login_request: ProviderLoginRequest,
                             user: User = Depends(get_current_user)):
    if is_clinical_provider(user):
        return provider_login(
            provider_login_request.token)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.get("/get_workstations")
async def api_provider_get_workstations(user: User = Depends(get_current_user)):
    if is_clinical_provider(user):
        return provider_get_workstations()
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/lookup_appointment")
async def api_provider_lookup_appointment(provider_lookup_appointment_request: ProviderLookupAppointmentRequest,
                                          user: User = Depends(get_current_user)):
    if is_clinical_provider(user):
        return provider_lookup_appointment(provider_lookup_appointment_request.appointment_id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/update_appointment")
async def api_provider_update_appointment(provider_update_appointment_request: ProviderUpdateAppointmentRequest,
                                          user: User = Depends(get_current_user)):
    if is_clinical_provider(user):
        return provider_update_appointment(
            provider_update_appointment_request.appointment_id,
            provider_update_appointment_request.action,
            provider_update_appointment_request.workstation_id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )


@router.post("/scan_label")
async def api_scan_label(scan_label_request: ScanLabelRequest, user: User = Depends(get_current_user)):
    if is_clinical_provider(user):
        return scan_label(scan_label_request.appointment_id)
    else:
        raise HTTPException(
            status_code=401,
            detail=AUTH_FAILED_MESSAGE
        )
