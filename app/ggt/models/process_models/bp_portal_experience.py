from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.users import (
    get_user_by_email
)

from ggt.models.data_models.test_results import (
    get_all_test_results,
    search_details_by_name_and_dob,
    get_test_details
)

from ggt.models.data_models.generic_search_result import (
    find_patient
)
########################################################################################################
# [Public] functions
########################################################################################################
def bp_cc_search_details_by_name_and_dob(last_name, dob):
    return search_details_by_name_and_dob(last_name, dob)
    

def bp_cc_view_test_details(test_id):
    return get_test_details(test_id)


def bp_get_user_role(email):
    try:
        user = get_user_by_email(email)
        return user['role']

    except Exception as err:
        log_generic(
            type="error",
            email=email,
            function='bp_get_user_role',
            error=err
        )


def bp_get_all_test_results():
    try:
        return get_all_test_results()
    except Exception as err:
        log_generic(
            type="error",
            email="",
            function='bp_get_all_test_results',
            error=err
        )
        # return False

def bp_get_general_search_results(first_name, middle_name, last_name, dob, phone_number, 
                                    email, appointment_id, group_code,appointment_date, location_id):
    return find_patient(first_name, middle_name, last_name, dob, phone_number, 
                            email, appointment_id, group_code,appointment_date, location_id)