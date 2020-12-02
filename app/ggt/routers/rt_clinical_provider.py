from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.data_models.data_types import (
        ProviderUpdateAppointmentRequest,
        ProviderLookupAppointmentRequest,
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
        scan_label
    )

router = APIRouter()


@router.get("/get_workstations", dependencies=[Security(authorize_user, scopes=[p.GET_WORKSTATIONS])])
async def api_provider_get_workstations():
    return await provider_get_workstations()


@router.post("/lookup_appointment", dependencies=[Security(authorize_user, scopes=[p.LOOKUP_APPOINTMENT])])
async def api_provider_lookup_appointment(provider_lookup_appointment_request: ProviderLookupAppointmentRequest):
    return await provider_lookup_appointment(provider_lookup_appointment_request.appointment_id)


@router.post("/update_appointment", dependencies=[Security(authorize_user, scopes=[p.UPDATE_APPOINTMENT])])
async def api_provider_update_appointment(provider_update_appointment_request: ProviderUpdateAppointmentRequest):
    return await provider_update_appointment(
        provider_update_appointment_request.appointment_id,
        provider_update_appointment_request.action,
        provider_update_appointment_request.workstation_id
    )


@router.post("/scan_label", dependencies=[Security(authorize_user, scopes=[p.SCAN_LABEL])])
async def api_scan_label(scan_label_request: ScanLabelRequest):
    return await scan_label(scan_label_request.appointment_id)
