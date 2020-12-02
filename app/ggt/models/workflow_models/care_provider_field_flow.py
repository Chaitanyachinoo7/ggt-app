from aiocache import cached

from ggt.lib.utils import (
    x_response,
    y_response
)

from ggt.models.process_models.bp_care_provider_experience import (
    bp_get_provider_processing_list, bp_lock_provider_task, bp_create_patient_test_consultation,
    bp_update_consultation_note, bp_provider_complete_task, bp_provider_rollback_to_pending_task, bp_call_patient)


########################################################################################################
# [Public] functions
########################################################################################################
def get_provider_processing_list(provide_request):
    return y_response(
        bp_get_provider_processing_list(provide_request.offset, provide_request.consultation_status,
                                        provide_request.consultation_notes, provide_request.positive_call,
                                        provide_request.limit)
    )


def lock_provider_task(lock_request):
    updated = bp_lock_provider_task(lock_request.test_id)
    if updated:
        return y_response(bp_create_patient_test_consultation(lock_request.appointment_id, lock_request.user_id))
    else:
        return x_response(None)


def update_consultation_note(update_note):
    return x_response(bp_update_consultation_note(update_note.consultation_id, update_note.note))


def call_patient(call_req):
    return y_response(bp_call_patient(call_req.patient_mobile, call_req.provider_mobile))


def provider_complete_task(complete_task):
    updated = bp_provider_complete_task(complete_task.test_id)

    if updated:
        return x_response(bp_update_consultation_note(complete_task.consultation_id, complete_task.note,
                                                      complete_task.consultation_type_code,
                                                      complete_task.resolution_code))
    else:
        return y_response(None)


"""
Following is a admin task, in case of emergency
"""


def provider_rollback_to_pending_task(test_id):
    return x_response(bp_provider_rollback_to_pending_task(test_id))

########################################################################################################
# [Protected] functions
########################################################################################################
