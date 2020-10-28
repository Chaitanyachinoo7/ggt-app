from fastapi import APIRouter

from ggt.models.workflow_models.printer_flow import (
    printer_queue_check,
    printer_get_next_label
)

router = APIRouter()


@router.get("/printer_queue_check/{workstation_id}/{workstation_token}")
async def api_printer_queue_check(workstation_id: str, workstation_token: str):
    return printer_queue_check(workstation_id, workstation_token)


@router.get("/printer_get_next_label/{workstation_id}/{workstation_token}")
async def api_printer_get_next_label(workstation_id: str, workstation_token: str):
    return printer_get_next_label(workstation_id, workstation_token)
