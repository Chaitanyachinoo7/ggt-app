from starlette.responses import StreamingResponse

from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    x_response,
    y_response
)
from ggt.models.process_models.bp_biller_experience import bp_get_billing_list, bp_update_billing_status, \
    bp_image_from_bucket, bp_report_from_bucket, bp_create_insurance_record, bp_update_insurance_record, \
    bp_validate_insurance_record, bp_delete_insurance_record, bp_download_billing_list

from ggt.models.process_models.bp_care_provider_experience import (
    bp_get_provider_processing_list, bp_lock_provider_task, bp_create_patient_test_consultation,
    bp_update_consultation_note, bp_provider_complete_task, bp_provider_rollback_to_pending_task)


########################################################################################################
# [Public] functions
########################################################################################################
from ggt.models.process_models.bp_reporting import bp_get_stats_today, bp_get_stats_by_date, bp_get_sms_stats_by_date, \
    bp_get_email_stats_by_date, bp_aging_samples_with_lab

@cached(cache=TTLCache(maxsize=1024, ttl=30))
def get_stats_today():
    return y_response(
        bp_get_stats_today()
    )

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_stats_by_date(date):
    return y_response(
        bp_get_stats_by_date(date)
    )

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_sms_stats_by_date(date):
    return y_response(
        bp_get_sms_stats_by_date(date)
    )

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_email_stats_by_date(date):
    return y_response(
        bp_get_email_stats_by_date(date)
    )

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def aging_samples_with_lab():
    return y_response(
        bp_aging_samples_with_lab()
    )

########################################################################################################
# [Protected] functions
########################################################################################################
