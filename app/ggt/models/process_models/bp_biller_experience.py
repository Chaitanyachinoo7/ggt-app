from ggt.lib.storage import get_file_blob
from ggt.lib.constants import (
    ERROR
)
from ggt.lib.utils import (
    log_generic,
    whoami, get_config_val)
from ggt.models.data_models.billers import get_billing_list, update_billing_status, create_insurance_record, \
    update_insurance_record, validate_insurance_record, delete_insurance_record
from ggt.models.data_models.providers import get_provider_processing_list, provider_lock_task, \
    create_patient_test_consultation, update_consultation_note, provider_complete_task, \
    provider_rollback_to_pending_task


########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_billing_list(offset, status, from_dt, to_dt, limit, sort, pre_consulted, provider_reviewed):
    return get_billing_list(offset, status, from_dt, to_dt, limit, sort, pre_consulted, provider_reviewed)


def bp_update_billing_status(appointment_id):
    return update_billing_status(appointment_id)


def bp_create_insurance_record(record):
    return create_insurance_record(record)


def bp_update_insurance_record(record):
    return update_insurance_record(record)


def bp_validate_insurance_record(record):
    return validate_insurance_record(record)


def bp_delete_insurance_record(record):
    return delete_insurance_record(record)


async def bp_image_from_bucket(image_id):
    insurance_cards_bucket_name = get_config_val('gcp.insurance_cards_bucket_name')
    blob = await get_file_blob(insurance_cards_bucket_name, image_id)
    if blob:
        yield blob.download_as_bytes()
    else:
        blob = await get_file_blob(insurance_cards_bucket_name, 'card.png')
        yield blob.download_as_bytes()


async def bp_report_from_bucket(image_id):
    lab_reports_bucket_name = get_config_val('gcp.lab_reports_bucket_name')
    blob = await get_file_blob(lab_reports_bucket_name, image_id)
    if blob:
        yield blob.download_as_bytes()
    else:
        yield "No report found"


