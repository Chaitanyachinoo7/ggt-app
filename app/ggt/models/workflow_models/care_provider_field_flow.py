from ggt.lib.utils import (
    x_response,
    y_response
)

from ggt.models.process_models.bp_care_provider_experience import (
    bp_get_provider_processing_list, bp_lock_provider_task, bp_create_patient_test_consultation,
    bp_update_consultation_note, bp_provider_complete_task, bp_provider_rollback_to_pending_task)


########################################################################################################
# [Public] functions
########################################################################################################

def get_provider_processing_list(provide_request):
    return y_response(
        bp_get_provider_processing_list(provide_request.offset, provide_request.consultation_status,
                                        provide_request.consultation_notes, provide_request.positive_call)
    )


def lock_provider_task(lock_request):
    updated = bp_lock_provider_task(lock_request.test_id)
    if updated:
        return y_response(bp_create_patient_test_consultation(lock_request.test_id, lock_request.user_id))
    else:
        return x_response(None)


def update_consultation_note(update_note):
    return x_response(bp_update_consultation_note(update_note.consultation_id, update_note.note))


def provider_complete_task(test_id):
    return x_response(bp_provider_complete_task(test_id))


"""
Following is a admin task, in case of emergency
"""


def provider_rollback_to_pending_task(test_id):
    return x_response(bp_provider_rollback_to_pending_task(test_id))

########################################################################################################
# [Protected] functions
########################################################################################################
