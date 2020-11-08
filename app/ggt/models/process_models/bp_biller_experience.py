from ggt.lib.constants import (
    ERROR
)
from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.billers import get_billing_list, update_billing_status
from ggt.models.data_models.providers import get_provider_processing_list, provider_lock_task, \
    create_patient_test_consultation, update_consultation_note, provider_complete_task, \
    provider_rollback_to_pending_task


########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_billing_list(offset, status, from_dt, to_dt):
    return get_billing_list(offset, status, from_dt, to_dt)


def bp_update_billing_status(appointment_id):
    return update_billing_status(appointment_id)


