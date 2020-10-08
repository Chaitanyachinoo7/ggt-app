from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_general_search_results,
    bp_get_location_search_results
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

def site_admin_general_search(auth_token, first_name, middle_name, last_name, dob, phone_number, email, appointment_id, group_code, appointment_date, location_id):
    return y_response(
        bp_get_general_search_results(
            first_name, middle_name, last_name, dob, phone_number, email, appointment_id, group_code, appointment_date, location_id
        )
    )


def site_admin_location_search(account, group_code, site_code):
    return y_response(
        bp_get_location_search_results(
            account, group_code, site_code
        )
    )


def generate_schedule(location_id):
    bp_generate_full_schedule(location_id)


def generate_all_schedules():
    bp_generate_all_schedules()


def delete_schedule_generation_rule(id):
    return x_response(
        bp_delete_schedule_generation_rule(id)
    )


def delete_schedule(location_id):
    return x_response(
        bp_delete_schedule(location_id)
    )


def add_schedule_generation_rule(data):
    status = False
    if bp_add_schedule_generation_rule(data):
        bp_generate_full_schedule(data.location_id)
        status = True
    return x_response(
        status
    )

    return x_response(
        bp_add_schedule_generation_rule(data)
    )


def update_schedule_generation_rule(data):
    status = False
    if bp_update_schedule_generation_rule(data):
        bp_generate_full_schedule(data.location_id)
        status = True
    return x_response(
        status
    )


def get_schedule_generation_rules(location_id):
    return y_response(
        bp_get_schedule_generation_rules(location_id)
    )
########################################################################################################
# [Protected] functions
########################################################################################################
