from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info,
    bp_appointment_update
)

from ggt.models.process_models.bp_printers import (
    bp_provider_get_workstations
)
'''
bp_get_monthly_calendar,
bp_get_monthly_calendar,
bp_provider_positive_result_followup,
bp_get_user_role,
bp_get_test_results
'''
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

'''
def printer_queue_check(printer_id, printer_token):
    return x_response(bp_printer_queue_check)
'''

def provider_get_workstations(auth_token):
    return x_response(
        bp_provider_get_workstations(),
        is_authenticated(auth_token)
    )


def provider_lookup_appointment(auth_token, appointment_id):
    return x_response(
        bp_get_appointment_info(appointment_id),
        is_authenticated(auth_token)
    )


def provider_update_appointment(auth_token, appointment_id, action, workstation_id):
    return x_response(
        bp_appointment_update(appointment_id, action, workstation_id),
        is_authenticated(auth_token)
    )


########################################################################################################
# [Protected] functions
########################################################################################################


def is_authenticated(auth_token):
    return auth_token == ADMIN_TOKEN
