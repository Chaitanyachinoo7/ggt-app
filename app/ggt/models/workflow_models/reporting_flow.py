from starlette.responses import StreamingResponse

from cachetools import cached, LRUCache, TTLCache

from ggt.lib.adapters.auth0_adapter import get_organization_id
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
    bp_get_email_stats_by_date, bp_aging_samples_with_lab, bp_get_user_activity, bp_get_patient_drill_down_by_date, \
    bp_get_portal_stats_today, bp_get_portal_stats


@cached(cache=TTLCache(maxsize=1024, ttl=30))
def get_stats_today():
    return y_response(
        bp_get_stats_today()
    )


# @cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_stats_by_date(date, user):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_stats_by_date(date, org_id)
    )


def get_portal_stats_today(user):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_portal_stats_today(org_id)
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


def get_user_activity(req):
    return y_response(
        bp_get_user_activity(req)
    )


def get_patient_drill_down_by_date(user, patient_drill_down_request):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_patient_drill_down_by_date(
            patient_drill_down_request.location_id,
            patient_drill_down_request.date,
            patient_drill_down_request.status,
            org_id
        )
    )


def get_portal_stats(user, location_id, timestamp):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_portal_stats(org_id, location_id, timestamp)
    )


########################################################################################################
# [Protected] functions
########################################################################################################
