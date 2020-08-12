from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_general_search_results
)

from ggt.models.process_models.bp_schedules import (
    bp_generate_full_schedule,
    bp_generate_all_schedules
)

########################################################################################################
# [Public] functions
########################################################################################################

def site_admin_general_search(auth_token, first_name, middle_name, last_name, dob, phone_number, email, appointment_id, group_code,appointment_date, location_id):
    return y_response(
        bp_get_general_search_results(
            first_name, middle_name, last_name, dob, phone_number, email, appointment_id, group_code,appointment_date, location_id
        )
    )


def generate_schedule(location_id):
    return x_response(
        bp_generate_full_schedule(location_id)
    )

def generate_all_schedules():
    return x_response(
        bp_generate_all_schedules()
    )
########################################################################################################
# [Protected] functions
########################################################################################################

