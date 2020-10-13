from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_user_role
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

########################################################################################################
# [Public] functions
########################################################################################################

def portal_get_user_role(email):
    return bp_get_user_role(email)

'''
def provider_get_monthly_calendar(auth_token, date, location_id):
    return y_response(
        bp_get_monthly_calendar(date, location_id),
        is_authenticated(auth_token)
    )


def provider_positive_result_followup():
    # return x_response(
    return bp_provider_positive_result_followup()
    # is_authenticated(auth_token)
    # )


def provider_get_test_results():
    return bp_get_test_results()
'''
########################################################################################################
# [Protected] functions
########################################################################################################
