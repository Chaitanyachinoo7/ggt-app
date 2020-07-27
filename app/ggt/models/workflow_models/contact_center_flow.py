from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_portal_experience import (
    bp_cc_view_test_details,
    bp_cc_search_details_by_name_and_dob
)

########################################################################################################
# [Public] functions
########################################################################################################

def cc_view_test_details(auth_token, test_id):
    return x_response(
        bp_cc_view_test_details(
            test_id
        )
    )


def cc_search_details_by_name_and_dob(last_name, dob):
    return y_response(
        bp_cc_search_details_by_name_and_dob(
            last_name, dob
        )
    )

########################################################################################################
# [Protected] functions
########################################################################################################
