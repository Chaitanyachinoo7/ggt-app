from aiocache import cached
from ggt.lib.constants import (
    ERROR
)
from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.providers import get_provider_processing_list, provider_lock_task, \
    create_patient_test_consultation, update_consultation_note, provider_complete_task, \
    provider_rollback_to_pending_task


########################################################################################################
# [Public] functions
########################################################################################################

@cached(ttl=30)
async def bp_get_provider_processing_list(offset, consultation_status, consultation_notes, positive_call, limit):
    try:
        if not offset:
            offset = 0

        return get_provider_processing_list(offset, consultation_status, consultation_notes, positive_call, limit)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )


async def bp_update_consultation_note(consultation_id, note, consultation_type_code, resolution_code):
    return update_consultation_note(consultation_id, note, consultation_type_code, resolution_code)


async def bp_call_patient(patient_number, provider_number):
    return "To be implemented, {} should call {}".format(provider_number, patient_number)


async def bp_provider_complete_task(test_id):
    return provider_complete_task(test_id)


async def bp_provider_rollback_to_pending_task(test_id):
    return provider_rollback_to_pending_task(test_id)


async def bp_lock_provider_task(test_id):
    return provider_lock_task(test_id)


async def bp_create_patient_test_consultation(appointment_id, user_id):
    return create_patient_test_consultation(appointment_id, user_id)



