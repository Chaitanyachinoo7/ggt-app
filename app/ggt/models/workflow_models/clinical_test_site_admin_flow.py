from aiocache import cached

from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_general_search_results,
    bp_get_location_search_results,
    bp_create_location, bp_get_all_groups, bp_update_location, bp_assign_group, bp_remove_group, bp_assign_service,
    bp_remove_service, bp_get_all_services, bp_get_locations, bp_create_group, bp_update_group, bp_get_states,
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


@cached(ttl=60)
async def site_admin_general_search(first_name, middle_name, last_name, dob, phone_number, email, appointment_id,
                                    group_code, appointment_date, location_id, vial_id="", sort_field="register_dt", sort_type="desc"):
    return y_response(
        await bp_get_general_search_results(
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
            sort_type
        )
    )


# @cached(ttl=60)
async def site_admin_location_search(account, group_code, site_code, location_name):
    return y_response(
        await bp_get_location_search_results(
            account, group_code, site_code, location_name
        )
    )


async def create_location(location):
    return y_response(
        await bp_create_location(location)
    )


async def get_states():
    return y_response(
        await bp_get_states()
    )


async def create_group(group):
    return y_response(
        await bp_create_group(group)
    )


async def update_group(group):
    return y_response(
        await bp_update_group(group)
    )


async def assign_group(req):
    return y_response(
        await bp_assign_group(req)
    )


async def assign_service(req):
    return y_response(
        await bp_assign_service(req)
    )


async def remove_group(req):
    return x_response(
        await bp_remove_group(req)
    )


async def get_locations():
    return y_response(
        await bp_get_locations()
    )


async def remove_service(req):
    return x_response(
        await bp_remove_service(req)
    )


async def update_location(location):
    return y_response(
        await bp_update_location(location)
    )


async def get_all_groups():
    return y_response(
        await bp_get_all_groups()
    )


async def get_all_services():
    return y_response(
        await bp_get_all_services()
    )


async def generate_schedule(location_id):
    await bp_generate_full_schedule(location_id)


async def generate_all_schedules():
    await bp_generate_all_schedules()


async def delete_schedule_generation_rule(id):
    status = False
    if await bp_delete_schedule_generation_rule(id):
        status = await bp_generate_full_schedule(id)

    return x_response(
        status
    )


async def delete_schedule(location_id):
    return x_response(
        await bp_delete_schedule(location_id)
    )


async def add_schedule_generation_rule(data):
    status = False
    if await bp_add_schedule_generation_rule(data):
        status = await bp_generate_full_schedule(data.location_id)

    return x_response(
        status
    )


async def update_schedule_generation_rule(data):
    status = False
    if await bp_update_schedule_generation_rule(data):
        status = await bp_generate_full_schedule(data.location_id)

    return x_response(
        status
    )


async def get_schedule_generation_rules(location_id):
    return y_response(
        await bp_get_schedule_generation_rules(location_id)
    )
########################################################################################################
# [Protected] functions
########################################################################################################
