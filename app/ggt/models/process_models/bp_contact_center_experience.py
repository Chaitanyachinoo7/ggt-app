from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.test_results import (
    search_tested_patients,
    get_test_details
)

########################################################################################################
# [Public] functions
########################################################################################################

def bp_cc_patient_search(last_name, dob):
    return {
        "results": search_tested_patients(last_name, dob)
    }


def bp_cc_view_test_details(test_id):
    return {
        "test_details": get_test_details(test_id)
    }
