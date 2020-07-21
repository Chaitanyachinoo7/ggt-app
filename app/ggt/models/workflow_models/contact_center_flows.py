from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_contact_center_experience import (
    bp_cc_patient_search,
    bp_cc_view_test_details,
    bp_cc_patient_lookup
)

# TODO: move this to a table for dynamic lookup
ADMIN_TOKEN = "temptoken2020"

########################################################################################################
# [Public] functions
########################################################################################################
# TODO: return a token with claims


def cc_login(auth_token):
    return x_response(
        {
            'auth_token': ADMIN_TOKEN
        },
        is_authenticated(auth_token)
    )


def cc_patient_search(auth_token, last_name, dob):
    return x_response(
        bp_cc_patient_search(
            last_name,
            dob
        ),
        is_authenticated(auth_token)
    )


def cc_view_test_details(auth_token, test_id):
    return x_response(
        bp_cc_view_test_details(
            test_id
        ),
        is_authenticated(auth_token)
    )


def cc_patient_lookup(lname, dob):
    print(lname)
    return y_response(
        bp_cc_patient_lookup(
            lname, dob
        ),
        True
    )

########################################################################################################
# [Protected] functions
########################################################################################################


def is_authenticated(auth_token):
    return auth_token == ADMIN_TOKEN
