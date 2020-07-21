from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.test_results import (
    search_tested_patients,
    get_test_details,
    cc_patient_lookup
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


def bp_cc_patient_lookup(lname, dob):
    try:
        print(lname)
        rows = cc_patient_lookup(lname, dob)
        result = ""
        if rows[0]['test_result'] == "pos" or rows[0]['test_result'] == "neg":
                result = "Received"
        else:
                result = "Pending"
        return rows
    except Exception as err:
        print(err)
        return{
            "status": "failure"
        }
        
