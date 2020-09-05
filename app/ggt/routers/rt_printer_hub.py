
from fastapi import APIRouter, Request, Response, status

from ggt.models.data_models.data_types import (
    ProviderLoginRequest,
    ProviderUpdateAppointmentRequest,
    ProviderLookupAppointmentRequest
)

from ggt.models.workflow_models.provider_field_testing_flow import (
    provider_login,
    provider_get_workstations,
    provider_lookup_appointment,
    provider_update_appointment,
    printer_queue_check
)

router = APIRouter()



@router.post("/printer_queue_check/{printer_id}/{printer_token}")
async def api_printer_queue_check(request: Request, printer_id: str, printer_token: str):
    return printer_queue_check(printer_id, printer_token)
