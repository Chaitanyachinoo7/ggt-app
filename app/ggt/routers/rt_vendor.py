from fastapi import APIRouter, Security, Request, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from ggt.lib.auth import authorize_user, get_vendor_api_key

from ggt.models.workflow_models.vendor_integration_flow import (
    lab_status_update,
)

from ggt.models.data_models.data_types import (
    LabStatusUpdateRequest
)

router = APIRouter()


@router.post("/status_updates/{vcode}")
def api_lab_status_updates(status_updates_request: LabStatusUpdateRequest, api_key: APIKey = Depends(get_vendor_api_key)):
    return lab_status_update(status_updates_request)

