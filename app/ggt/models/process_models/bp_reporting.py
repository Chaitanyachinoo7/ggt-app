########################################################################################################
# [Public] functions
########################################################################################################
from cachetools import cached, LRUCache, TTLCache

from ggt.models.data_models.reporting import get_stats_today, get_stats_by_date, get_sms_stats_by_date, \
    get_email_stats_by_date, aging_samples_with_lab_by_ship_date, get_user_activity, get_patient_drill_down_by_date, \
    get_portal_stats_today, get_portal_stats


def bp_get_stats_today():
    return get_stats_today()


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def bp_get_stats_by_date(date, org_id):
    return get_stats_by_date(date, org_id)


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def bp_get_portal_stats_today(org_id):
    return get_portal_stats_today(org_id)


def bp_get_sms_stats_by_date(date):
    return get_sms_stats_by_date(date)


def bp_get_email_stats_by_date(date):
    return get_email_stats_by_date(date)


def bp_aging_samples_with_lab():
    return aging_samples_with_lab_by_ship_date()


def bp_get_user_activity(req):
    return get_user_activity(req)


def bp_get_patient_drill_down_by_date(location_id, date, status, org_id):
    return get_patient_drill_down_by_date(location_id, date, status, org_id)


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def bp_get_portal_stats(org_id, location_id, timestamp):
    return get_portal_stats(org_id, location_id, timestamp)
