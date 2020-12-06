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


async def bp_get_billing_list(offset, status, from_dt, to_dt, limit, sort, pre_consulted,
                              provider_reviewed, test_status, appointment_status):
    return await get_billing_list(offset, status, from_dt, to_dt, limit, sort, pre_consulted, provider_reviewed,
                                  test_status, appointment_status)


async def bp_update_billing_status(appointment_id):
    return await update_billing_status(appointment_id)


async def bp_create_insurance_record(record):
    return await create_insurance_record(record)


async def bp_update_insurance_record(record):
    return await update_insurance_record(record)


async def bp_validate_insurance_record(record):
    return await validate_insurance_record(record)


async def bp_delete_insurance_record(record):
    return await delete_insurance_record(record)


async def bp_download_billing_list(offset, limit):
    _offset = offset
    _limit = 500
    factor = int(limit/500)
    reminder = limit % 500
    temp = factor + 1 if reminder == 0 else factor + 2
    for x in range(1, temp):
        values = []
        headers = []
        string = ''
        if x == factor + 1:
            _limit = reminder
        lst = await get_billing_list(offset=offset, limit=_limit)
        lst = lst['list']
        for idx, l in enumerate(lst):
            if x == 1 and idx == 0:
                headers = l.keys()
                string = ','.join(headers) + '\n'
            values = l.values()
            values = [str(t) for t in values]
            string = string + ','.join(values) + '\n'
        yield string


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


