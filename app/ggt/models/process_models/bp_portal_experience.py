from datetime import datetime

from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.groups import get_all_groups, create_group, update_group, get_group_by_id
from ggt.models.data_models.providers import get_provider_processing_list, provider_lock_task, \
    create_patient_test_consultation, update_consultation_note, provider_complete_task, \
    provider_rollback_to_pending_task
from ggt.models.data_models.service_catalog import get_all_services

from ggt.models.data_models.users import (
    get_user_by_email
)

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

from ggt.models.data_models.locations import (
    search_locations,
    create_location, update_location, assign_group, remove_group, assign_service, remove_service,
    get_all_locations_without_thumbnail, assign_all_groups, assign_all_services, remove_all_group, remove_all_service,
    get_states)

import ggt.lib.constants as c


########################################################################################################
# [Public] functions
########################################################################################################
async def bp_cc_search_details_by_name_and_dob(last_name, dob):
    return await search_details_by_name_and_dob(last_name, dob)


async def bp_cc_view_test_details(test_id):
    return await get_test_details(test_id)


async def bp_get_user_role(email):
    try:
        user = await get_user_by_email(email)
        return user['role']


    except Exception as err:
        log_generic(
            type=c.ERROR,
            email=email,
            function=whoami(),
            error=err
        )


async def bp_get_all_test_results():
    try:
        return await get_all_test_results()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        # return await False


async def bp_get_general_search_results(first_name, middle_name, last_name, dob, phone_number, email, appointment_id,
                                        group_code, appointment_date, location_id, vial_id='', sort_field="register_dt", sort_type="desc"):
    try:
        if appointment_date != '':
            appointment_date = datetime.strptime(appointment_date, "%m%d%Y")

        return await find_patients(first_name, middle_name, last_name, dob, phone_number,
                                   email, appointment_id, group_code, appointment_date, location_id, vial_id, sort_field, sort_type)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_create_group(group):
    try:
        _id = await create_group(group)
        if _id is None:
            return None
        return await get_group_by_id(_id)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_update_group(group):
    try:
        updated = await update_group(group)
        if updated:
            return await get_group_by_id(group.id)
        return None
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_create_location(location):
    try:
        l = await create_location(location)
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
            g_success = await assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = await assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = await search_locations('', '', l['site_code'], '')
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_assign_group(req):
    try:
        return await assign_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_assign_service(req):
    try:
        return await assign_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_remove_group(req):
    try:
        return await remove_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_get_locations():
    try:
        return await get_all_locations_without_thumbnail()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_remove_service(req):
    try:
        return await remove_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_update_location(location):
    try:
        location_id = location.id
        await update_location(location)
        await remove_all_group(location_id)
        await remove_all_service(location_id)
        group_ids = location.group_ids
        service_ids = location.service_ids
        location_groups = []
        location_services = []

        for gid in group_ids:
            location_groups.append((gid, location_id))
        for sid in service_ids:
            location_services.append((location_id, sid))

        if len(location_groups) > 0:
            g_success = await assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = await assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = await search_locations('', '', '', '', location_id)
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_get_all_groups():
    try:
        return await get_all_groups()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_get_states():
    try:
        return await get_states()
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_get_all_services():
    try:
        return await get_all_services()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_get_location_search_results(account, group_code, site_code, location_name):
    try:
        return await search_locations(account, group_code, site_code, location_name)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_create_test_sample_from_appointment(appointment_id):
    try:
        return await create_test_sample_from_appointment(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


async def bp_record_label_scan(appointment_id):
    try:
        return await record_label_scan(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
