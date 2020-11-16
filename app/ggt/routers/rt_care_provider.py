from fastapi import APIRouter, Security

from ggt.lib.auth import authorise_user
from ggt.models.data_models.data_types import (
    PermissionsEnum as p, ProviderProcessListRequest, LockProviderTask, UpdateNoteReq,
    UpdateProviderTask, CompleteNoteReq, CallReq)
from ggt.models.workflow_models.care_provider_field_flow import (
    get_provider_processing_list, lock_provider_task, update_consultation_note, provider_complete_task,
    provider_rollback_to_pending_task, call_patient)

router = APIRouter()


@router.post("/provider_rollback_to_pending_task", dependencies=[Security(authorise_user, scopes=[p.PROVIDER_ROLLBACK_TO_PENDING_TASK])])
async def api_provider_rollback_to_pending_task(complete_task: UpdateProviderTask):
    return provider_rollback_to_pending_task(complete_task.test_id)


@router.post("/end_consultation", dependencies=[Security(authorise_user, scopes=[p.PROVIDER_COMPLETE_TASK])])
async def api_provider_complete_task(complete_task: CompleteNoteReq):
    return provider_complete_task(complete_task)


@router.post("/call_patient", dependencies=[Security(authorise_user, scopes=[p.CALL_PATIENT])])
async def api_call_patient(call_request: CallReq):
    return call_patient(call_request)


@router.post("/begin_consultation", dependencies=[Security(authorise_user, scopes=[p.LOCK_PROVIDER_TASK])])
async def api_lock_provider_task(lock_request: LockProviderTask):
    return lock_provider_task(lock_request)


@router.post("/get_provider_processing_list", dependencies=[Security(authorise_user, scopes=[p.GET_PROVIDER_PROCESSING_LIST])])
async def api_get_provider_processing_list(provide_request: ProviderProcessListRequest):
    return get_provider_processing_list(provide_request)



