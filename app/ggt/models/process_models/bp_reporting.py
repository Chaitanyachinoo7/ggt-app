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
from ggt.models.data_models.reporting import get_stats_today, get_stats_by_date, get_sms_stats_by_date, \
    get_email_stats_by_date, aging_samples_with_lab_by_ship_date


async def bp_get_stats_today():
    return await get_stats_today()


async def bp_get_stats_by_date(date):
    return await get_stats_by_date(date)


async def bp_get_sms_stats_by_date(date):
    return await get_sms_stats_by_date(date)


async def bp_get_email_stats_by_date(date):
    return await get_email_stats_by_date(date)


async def bp_aging_samples_with_lab():
    return await aging_samples_with_lab_by_ship_date()
