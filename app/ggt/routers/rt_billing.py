from fastapi import APIRouter, Security

from ggt.lib.auth import authorise_user
from ggt.models.data_models.data_types import (
    PermissionsEnum as p, ProviderProcessListRequest, LockProviderTask, UpdateNoteReq,
    UpdateProviderTask, GetBillingListReq, UpdateBilligStatus)
from ggt.models.workflow_models.billing_flow import get_billing_list, update_billing_status
from ggt.models.workflow_models.care_provider_field_flow import (
    get_provider_processing_list, lock_provider_task, update_consultation_note, provider_complete_task,
    provider_rollback_to_pending_task)

router = APIRouter()


@router.post("/get_billing_list", dependencies=[Security(authorise_user, scopes=[p.GET_BILLING_LIST])])
async def api_get_billing_list(bill_req: GetBillingListReq):
    return get_billing_list(bill_req)


@router.post("/update_billing_status", dependencies=[Security(authorise_user, scopes=[p.UPDATE_BILLING_STATUS])])
async def api_update_billing_status(bill_req: UpdateBilligStatus):
    return update_billing_status(bill_req)


