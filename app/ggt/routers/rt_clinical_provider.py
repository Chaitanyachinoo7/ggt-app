from fastapi import APIRouter, Security, Request, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from ggt.lib.auth import authorize_user, get_api_key
from ggt.models.data_models.data_types import (
    ProviderUpdateAppointmentRequest,
    ProviderLookupAppointmentRequest,
    StatusUpdatesRequest,
    ScanLabelRequest, PermissionsEnum as p,
    ProviderProcessListRequest,
    LockProviderTask,
    UpdateNoteReq,
    UpdateProviderTask
)
from ggt.models.workflow_models.provider_field_testing_flow import (
    provider_get_workstations,
    provider_lookup_appointment,
    provider_update_appointment,
    scan_label,
    lab_status_update
)

router = APIRouter()


@router.get("/get_workstations", dependencies=[Security(authorize_user, scopes=[p.GET_WORKSTATIONS])])
async def api_provider_get_workstations():
    return provider_get_workstations()


@router.post("/lookup_appointment", dependencies=[Security(authorize_user, scopes=[p.LOOKUP_APPOINTMENT])])
async def api_provider_lookup_appointment(provider_lookup_appointment_request: ProviderLookupAppointmentRequest):
    return provider_lookup_appointment(provider_lookup_appointment_request.appointment_id)


@router.post("/update_appointment")
async def api_provider_update_appointment(provider_update_appointment_request: ProviderUpdateAppointmentRequest,
                                          user=Security(authorize_user, scopes=[p.UPDATE_APPOINTMENT])):
    return provider_update_appointment(
        provider_update_appointment_request.appointment_id,
        provider_update_appointment_request.action,
        provider_update_appointment_request.workstation_id,
        provider_update_appointment_request.vial_id,
        user
    )


@router.post("/scan_label", dependencies=[Security(authorize_user, scopes=[p.SCAN_LABEL])])
async def api_scan_label(scan_label_request: ScanLabelRequest):
    return scan_label(scan_label_request.appointment_id)


@router.post("/status_updates")
def api_lab_status_updates(status_updates_request: StatusUpdatesRequest, api_key: APIKey = Depends(get_api_key)):
    return lab_status_update(status_updates_request)
