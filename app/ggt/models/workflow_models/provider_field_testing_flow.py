from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info,
    bp_appointment_update
)

from ggt.models.process_models.bp_printers import (
    bp_provider_get_workstations
)

from ggt.models.process_models.bp_portal_experience import (
    bp_record_label_scan,
    bp_create_test_sample_from_appointment
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
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


def provider_get_workstations():
    return x_response(bp_provider_get_workstations())


def provider_lookup_appointment(appointment_id):
    return x_response(bp_get_appointment_info(appointment_id, 'allowdoboverride'))


def provider_update_appointment(appointment_id, action, workstation_id):
    return x_response(bp_appointment_update(appointment_id, action, workstation_id))


def scan_label(appointment_id):
    #TODO add to sys log, multiple scans can happen, keeps only latest scan
    bp_create_test_sample_from_appointment(appointment_id)
    return x_response(bp_record_label_scan(appointment_id))

########################################################################################################
# [Protected] functions
########################################################################################################


def is_authenticated(auth_token):
    return auth_token == ADMIN_TOKEN
