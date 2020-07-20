from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info,
    bp_appointment_update,
    bp_get_monthly_calendar,
    bp_get_monthly_calendar,
    bp_provider_positive_result_followup
)

# TODO: move this to a table for dynamic lookup
ADMIN_TOKEN = "entourage2020"


########################################################################################################
# [Public] functions
########################################################################################################
# TODO: return a token with claims
def provider_login(auth_token):
    return x_response(
        {
            'auth_token': ADMIN_TOKEN
        },
        is_authenticated(auth_token)
    )


# TODO: return a dynamic list
def provider_get_testing_locations(auth_token):
    return x_response(
        {
            'locations': [
                {
                    'id': 1,
                    'label': 'Location X - Lane A'
                }
            ]
        },
        is_authenticated(auth_token)
    )


def provider_lookup_appointment(auth_token, appointment_id):
    return x_response(
        bp_get_appointment_info(appointment_id),
        is_authenticated(auth_token)
    )


def provider_update_appointment(auth_token, appointment_id, action):
    return x_response(
        bp_appointment_update(appointment_id, action),
        is_authenticated(auth_token)
    )


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

########################################################################################################
# [Protected] functions
########################################################################################################


def is_authenticated(auth_token):
    return auth_token == ADMIN_TOKEN
