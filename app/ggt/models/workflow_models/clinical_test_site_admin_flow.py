from cachetools import cached, LRUCache, TTLCache

from ggt.lib.adapters.auth0_adapter import get_organization_id
from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)
from ggt.models.data_models.schedules import get_location_id_by_rule_id

from ggt.models.process_models.bp_portal_experience import (
    bp_get_general_search_results,
    bp_get_location_search_results,
    bp_create_location, bp_get_all_groups, bp_update_location, bp_assign_group, bp_remove_group, bp_assign_service,
    bp_remove_service, bp_get_all_services, bp_get_locations, bp_create_group, bp_update_group, bp_get_states,
    bp_get_f11,
    bp_get_consent_forms,
    bp_get_vax_waitlist_search_results
)

from ggt.models.process_models.bp_schedules import (
    bp_generate_full_schedule,
    bp_generate_all_schedules,
    bp_add_schedule_generation_rule,
    bp_update_schedule_generation_rule,
    bp_delete_schedule_generation_rule,
    bp_get_schedule_generation_rules,
    bp_delete_schedule
)

import ggt.lib.constants as c


########################################################################################################
# [Public] functions
########################################################################################################


# Do not cache
def site_admin_general_search(user, first_name, middle_name, last_name, dob, phone_number, email, appointment_id,
                              group_code, appointment_date, location_id, vial_id="", sort_field="register_dt",
                              sort_type="desc", group_vax_results=False, token=None, is_patient=False):
    if not is_patient:
        org_id = get_organization_id(user)
    else:
        org_id = None

    return y_response(
        bp_get_general_search_results(
            org_id,
            first_name,
            middle_name,
            last_name,
            dob,
            phone_number,
            email,
            appointment_id,
            group_code,
            appointment_date,
            location_id,
            vial_id,
            sort_field,
            sort_type,
            group_vax_results=group_vax_results,
            token=token,
            is_patient=is_patient
        ), allow=True
    )


def site_admin_get_f11(appointment_ids):
    return y_response(
        bp_get_f11(appointment_ids))
def site_admin_get_consent_forms(patient_ids):
    return y_response(
        bp_get_consent_forms(patient_ids))

# @cached(cache=TTLCache(maxsize=1024, ttl=60))


# Do not cache
def site_admin_location_search(account, group_code, site_code, location_name, st, user, location_id=None):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_location_search_results(
            account, group_code, site_code, location_name, st, org_id, location_id=location_id
        )
    )


def create_location(location, user):
    org_id = get_organization_id(user)
    return y_response(
        bp_create_location(location, org_id)
    )


def get_states():
    return y_response(
        bp_get_states()
    )


def create_group(group):
    return y_response(
        bp_create_group(group)
    )


def update_group(group):
    return y_response(
        bp_update_group(group)
    )


def assign_group(req):
    return y_response(
        bp_assign_group(req)
    )


def assign_service(req):
    return y_response(
        bp_assign_service(req)
    )


def remove_group(req):
    return x_response(
        bp_remove_group(req)
    )


def get_locations(user):
    org_id = get_organization_id(user)
    return y_response(
        bp_get_locations(org_id)
    )


def remove_service(req):
    return x_response(
        bp_remove_service(req)
    )


def update_location(location, user):
    org_id = get_organization_id(user)
    return y_response(
        bp_update_location(location, org_id)
    )


def get_all_groups(user):
    return y_response(
        bp_get_all_groups(user)
    )


def get_all_services():
    return y_response(
        bp_get_all_services()
    )


def generate_schedule(location_id):
    bp_generate_full_schedule(location_id)


def generate_all_schedules():
    bp_generate_all_schedules()


def delete_schedule_generation_rule(id):
    status = False
    location_id = get_location_id_by_rule_id(id)
    if location_id:
        if bp_delete_schedule_generation_rule(id):
            status = bp_generate_full_schedule(location_id)

    return x_response(
        status
    )


def delete_schedule(location_id):
    return x_response(
        bp_delete_schedule(location_id)
    )


def add_schedule_generation_rule(data):
    status = False
    if bp_add_schedule_generation_rule(data):
        status = bp_generate_full_schedule(data.location_id)

    return x_response(
        status
    )


def update_schedule_generation_rule(data):
    status = False
    if bp_update_schedule_generation_rule(data):
        status = bp_generate_full_schedule(data.location_id)

    return x_response(
        status
    )


def get_schedule_generation_rules(location_id):
    return y_response(
        bp_get_schedule_generation_rules(location_id)
    )

def site_admin_vax_waitlist_search(data):
    return y_response(
        bp_get_vax_waitlist_search_results(data), True
    )

########################################################################################################
# [Protected] functions
########################################################################################################
