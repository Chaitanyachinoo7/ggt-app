from datetime import datetime

from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.groups import get_all_groups, create_group, update_group
from ggt.models.data_models.service_catalog import get_all_services

from ggt.models.data_models.users import (
    get_user_by_email
)

from ggt.models.data_models.test_results import (
    get_all_test_results,
    search_details_by_name_and_dob,
    get_test_details
)

from ggt.models.data_models.test_sample import (
    create_test_sample_from_appointment,
    record_label_scan
)

from ggt.models.data_models.generic_search_result import (
    find_patients
)

from ggt.models.data_models.locations import (
    search_locations,
    create_location, update_location, assign_group, remove_group, assign_service, remove_service,
    get_all_locations_without_thumbnail)

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
            type=ERROR,
            email=email,
            function=whoami(),
            error=err
        )


def bp_get_all_test_results():
    try:
        return get_all_test_results()
    except Exception as err:
        log_generic(
            type=ERROR,
            email="",
            function=whoami(),
            error=err
        )
        # return False


def bp_get_general_search_results(first_name, middle_name, last_name, dob, phone_number, email, appointment_id, group_code, appointment_date, location_id):
    try:
        if appointment_date != '':
            appointment_date = datetime.strptime(appointment_date, "%m%d%Y")
    
        return find_patients(first_name, middle_name, last_name, dob, phone_number, 
                                email, appointment_id, group_code, appointment_date, location_id)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )


def bp_create_group(group):
    return create_group(group)


def bp_update_group(group):
    return update_group(group)


def bp_create_location(location):
    return create_location(location)


def bp_assign_group(req):
    return assign_group(req)


def bp_assign_service(req):
    return assign_service(req)


def bp_remove_group(req):
    return remove_group(req)


def bp_get_locations():
    return get_all_locations_without_thumbnail()


def bp_remove_service(req):
    return remove_service(req)


def bp_update_location(location):
    return update_location(location)


def bp_get_all_groups():
    return get_all_groups()


def bp_get_all_services():
    return get_all_services()


def bp_get_location_search_results(account, group_code, site_code):
    return search_locations(account, group_code, site_code)


def bp_create_test_sample_from_appointment(appointment_id):
    return create_test_sample_from_appointment(appointment_id)


def bp_record_label_scan(appointment_id):
    return record_label_scan(appointment_id)
