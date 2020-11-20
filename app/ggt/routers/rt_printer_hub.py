from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.workflow_models.printer_flow import (
    printer_queue_check,
    printer_get_next_label
)
from ggt.models.data_models.data_types import (
    PermissionsEnum as p
)

router = APIRouter()


@router.get("/printer_queue_check/{workstation_id}/{workstation_token}",
            dependencies=[Security(authorize_user, scopes=[p.PRINTER_QUEUE_CHECK])])
async def api_printer_queue_check(workstation_id: str, workstation_token: str):
    return printer_queue_check(workstation_id, workstation_token)


@router.get("/printer_get_next_label/{workstation_id}/{workstation_token}",
            dependencies=[Security(authorize_user, scopes=[p.PRINTER_GET_NEXT_LABEL])])
async def api_printer_get_next_label(workstation_id: str, workstation_token: str):
    return printer_get_next_label(workstation_id, workstation_token)
