########################################################################################################
# [Public] functions
########################################################################################################
from ggt.models.data_models.reporting import get_stats_today, get_stats_by_date, get_sms_stats_by_date, \
    get_email_stats_by_date, aging_samples_with_lab_by_ship_date, get_user_activity


def bp_get_stats_today():
    return get_stats_today()


def bp_get_stats_by_date(date):
    return get_stats_by_date(date)


def bp_get_sms_stats_by_date(date):
    return get_sms_stats_by_date(date)


def bp_get_email_stats_by_date(date):
    return get_email_stats_by_date(date)


def bp_aging_samples_with_lab():
    return aging_samples_with_lab_by_ship_date()


def bp_get_user_activity(req):
    return get_user_activity(req)
