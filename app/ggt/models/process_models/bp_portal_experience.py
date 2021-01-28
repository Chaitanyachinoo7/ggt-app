from datetime import datetime

import ggt.lib.constants as c
from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.clinical_test_results import (
    get_all_test_results,
    search_details_by_name_and_dob,
    get_test_details
)
from ggt.models.data_models.clinical_test_sample import (
    create_test_sample_from_appointment,
    record_label_scan
)
from ggt.models.data_models.generic_search_result import (
    find_patients
)
from ggt.models.data_models.groups import get_all_groups, create_group, update_group, get_group_by_id
from ggt.models.data_models.locations import (
    search_locations,
    create_location, update_location, assign_group, remove_group, assign_service, remove_service,
    get_all_locations_without_thumbnail, assign_all_groups, assign_all_services, remove_all_group, remove_all_service,
    get_states)
from ggt.models.data_models.service_catalog import get_all_services
from ggt.models.data_models.users import (
    get_user_by_email
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
            type=c.ERROR,
            email=email,
            function=whoami(),
            error=err
        )


def bp_get_all_test_results():
    try:
        return get_all_test_results()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        # return False


def bp_get_general_search_results(first_name, middle_name, last_name, dob, phone_number, email, appointment_id,
                                  group_code, appointment_date, location_id, vial_id='', sort_field="register_dt", sort_type="desc",
                                  group_vax_results=False, token=None):
    try:
        if appointment_date != '':
            appointment_date = datetime.strptime(appointment_date, "%m%d%Y")

        search_results = find_patients(first_name, middle_name, last_name, dob, phone_number,
                             email, appointment_id, group_code, appointment_date, location_id, vial_id, sort_field, sort_type, token=token)
        if group_vax_results:
            return __group_vax_results(search_results)

        return search_results

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_create_group(group):
    try:
        _id = create_group(group)
        if _id is None:
            return None
        return get_group_by_id(_id)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_update_group(group):
    try:
        updated = update_group(group)
        if updated:
            return get_group_by_id(group.id)
        return None
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_create_location(location):
    try:
        l = create_location(location)
        if l is None:
            return None
        location_id = l['location_id']
        group_ids = location.group_ids
        service_ids = location.service_ids
        location_groups = []
        location_services = []

        for gid in group_ids:
            location_groups.append((gid, location_id))
        for sid in service_ids:
            location_services.append((location_id, sid))

        if len(location_groups) > 0:
            g_success = assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = search_locations('', '', l['site_code'], '')
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_assign_group(req):
    try:
        return assign_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_assign_service(req):
    try:
        return assign_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_remove_group(req):
    try:
        return remove_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_locations():
    try:
        return get_all_locations_without_thumbnail()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_remove_service(req):
    try:
        return remove_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_update_location(location):
    try:
        location_id = location.id
        update_location(location)
        remove_all_group(location_id)
        remove_all_service(location_id)
        group_ids = location.group_ids
        service_ids = location.service_ids
        location_groups = []
        location_services = []

        for gid in group_ids:
            location_groups.append((gid, location_id))
        for sid in service_ids:
            location_services.append((location_id, sid))

        if len(location_groups) > 0:
            g_success = assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = search_locations('', '', '', '', location_id)
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_all_groups():
    try:
        return get_all_groups()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_states():
    try:
        return get_states()
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_all_services():
    try:
        return get_all_services()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_location_search_results(account, group_code, site_code, location_name):
    try:
        return search_locations(account, group_code, site_code, location_name)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_create_test_sample_from_appointment(appointment_id):
    try:
        return create_test_sample_from_appointment(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_record_label_scan(appointment_id):
    try:
        return record_label_scan(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def __group_vax_results(results):
    grouped_results = []
    vaccine_appointment_found = False
    grouped_vax_result = {
        "service": "COVID_19_VAX",
        "doses": []
    }

    for result in results:
        if result["service_code"] == c.SERVICE_CODE_COVID19_TEST:
            grouped_results.append(dict(result, service=c.SERVICE_CODE_COVID19_TEST))
        if result["service_code"] in [c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_1,
                                    c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_2,
                                    c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_1,
                                    c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_2]:
            grouped_vax_result["doses"].append(result)
            vaccine_appointment_found = True

    if vaccine_appointment_found:
        grouped_results.append(grouped_vax_result)

    return grouped_results
