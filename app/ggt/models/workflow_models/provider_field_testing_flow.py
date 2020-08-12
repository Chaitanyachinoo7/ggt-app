from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info,
    bp_appointment_update
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


# TODO: return a dynamic list
def provider_get_workstations(auth_token):
    return x_response(
        {
            'workstations': [
                {
                    'id': 1,
                    'label': 'METOHH1'
                },
                {
                    'id': 2,
                    'label': '0VPPP27'
                },
                {
                    'id': 3,
                    'label': '8B1I13S'
                },
                {
                    'id': 4,
                    'label': 'ARU68PR'
                },
                {
                    'id': 5,
                    'label': 'FLHRMLA'
                },
                {
                    'id': 6,
                    'label': '10Q890L'
                },
                {
                    'id': 7,
                    'label': 'OKQHIA1'
                },
                {
                    'id': 8,
                    'label': 'UNLL4LH'
                },
                {
                    'id': 9,
                    'label': 'LDAPD2UK'
                },
                {
                    'id': 10,
                    'label': 'PVO7LFT'
                },
                {
                    'id': 11,
                    'label': '6HIFU57'
                },
                {
                    'id': 12,
                    'label': 'KGDNA67'
                },
                {
                    'id': 13,
                    'label': 'OMHC0PV'
                },
                {
                    'id': 14,
                    'label': 'EIB8VMJ'
                },
                {
                    'id': 15,
                    'label': 'UHJ8AH7'
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
