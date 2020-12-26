from datetime import date, datetime, timedelta

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.models.data_models.schedules import (
    get_available_dates,
    get_available_locations,
    get_available_locations_near_lat_lng,
    get_available_times,
    get_slot_information,
    get_schedule_generation_rules_by_location_id,
    delete_schedule_entries_by_location_id,
    delete_schedule_entries_by_location_id_for_date,
    add_schedule_entries,
    add_schedule_generation_rule,
    update_schedule_generation_rule,
    delete_schedule_generation_rule,
    get_all_available_dtl,
    trim_schedule_generation_rules_start_dt,
    get_slots_matching_dt_list
)

from ggt.models.data_models.locations import (
    get_all_locations,
    get_services_available_for_location
)

from ggt.lib.maps import (
    get_map_thumbnail_url
)
########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_schedule_dates_available(group_code):
    try:
        group_code = normalize_group_code(group_code)
        rows = get_available_dates(group_code)
        available_dates = []
        for row in rows:
            date_str = row['available_date']
            label_str = date_str.strftime("%A %B %d, %Y")
            available_dates.append(
                {
                    "label": label_str,
                    "value": date_str
                }
            )
            '''
            log_generic(
                type=c.INFO,
                available_dates=available_dates,
                function=whoami()
            )
            '''

        return {
            "available_dates": available_dates
        }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            group_code=group_code,
            rows=rows,
            function=whoami(),
            error=err
        )


def bp_get_schedule_locations_available_near_lat_lng(lat: float, lng: float, radius: int = None, date_str: str = None, group_code: str = None):
    if not radius:
        radius = 100

    if not group_code:
        group_code = c.DEFAULT_GROUP_CODE

    if not date_str:
        date_str = date.today().strftime("%Y-%m-%d")

    group_code = normalize_group_code(group_code)
    dtl_list = get_available_locations_near_lat_lng(
        lat, lng, radius, date_str, group_code)
    available_locations = []
    try:
        for dtl in dtl_list:
            if dtl.location.addr2:
                addr2 = dtl.location.addr2
            else:
                addr2 = ''

            location_text = "{} {}, {}, {}  {}".format(
                dtl.location.addr1,
                addr2,
                dtl.location.city,
                dtl.location.st,
                dtl.location.zip
            )

            if dtl.location.image_thumbnail:
                map_thumbnail = 'data:image/jpeg;base64,{}'.format(
                    dtl.location.image_thumbnail)
            else:
                map_thumbnail = get_map_thumbnail_url(location_text)

            available_locations.append(
                {
                    'id': dtl.location.id,
                    'name': dtl.location.name,
                    'address': location_text,
                    'lat': dtl.location.lat,
                    'lng': dtl.location.lng,
                    'billing_type': dtl.location.billing_type,
                    'collect_insurance_info': dtl.location.collect_insurance_info,
                    'allow_insurance_skip': dtl.location.allow_insurance_skip,
                    'collect_upfront_payment': dtl.location.collect_upfront_payment,
                    'next_test_date': dtl.first_date_time_available.strftime("%a, %-d %b %Y @ %-I:%M %p") if dtl.first_date_time_available else None,
                    'wait_time_mins': '< 10m',
                    'result_time_hours': '{}h'.format(dtl.average_processing_time),
                    'slots_available': dtl.slot_count,
                    'type': 'public',
                    'map_thumbnail': map_thumbnail,
                    'services_available': dtl.location.services_available,
                    'distance': dtl.distance,
                    'external': dtl.is_external,
                    'external_phone': dtl.external_phone,
                    'operated_by': dtl.operated_by,
                    'website': dtl.website,
                    'accepts_bookings': dtl.accepts_bookings,
                    'accepts_walkins': dtl.accepts_walkins,
                    'open_hours': dtl.open_hours,
                    'label': location_text,
                    'value': dtl.location.id
                }
            )

        log_generic(
            type=c.INFO,
            date_str=date_str,
            group_code=group_code,
            #available_locations=available_locations,
            function=whoami()
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            group_code=group_code,
            date_str=date_str,
            #dtl_list=dtl_list,
            function=whoami(),
            error=err
        )

    return {
        "available_location": available_locations
    }


def bp_get_schedule_locations_available(date, group_code=c.DEFAULT_GROUP_CODE):
    group_code = normalize_group_code(group_code)
    dtl_list = get_available_locations(date, group_code)
    available_locations = []
    try:
        for dtl in dtl_list:
            if dtl.location.addr2:
                addr2 = dtl.location.addr2
            else:
                addr2 = ''

            location_text = "{} {}, {}, {}  {}".format(
                dtl.location.addr1,
                addr2,
                dtl.location.city,
                dtl.location.st,
                dtl.location.zip
            )

            if dtl.location.image_thumbnail:
                map_thumbnail = 'data:image/jpeg;base64,{}'.format(
                    dtl.location.image_thumbnail)
            else:
                map_thumbnail = get_map_thumbnail_url(location_text)

            available_locations.append(
                {
                    'id': dtl.location.id,
                    'name': dtl.location.name,
                    'address': location_text,
                    'lat': dtl.location.lat,
                    'lng': dtl.location.lng,
                    'billing_type': dtl.location.billing_type,
                    'collect_insurance_info': dtl.location.collect_insurance_info,
                    'allow_insurance_skip': dtl.location.allow_insurance_skip,
                    'collect_upfront_payment': dtl.location.collect_upfront_payment,
                    'next_test_date': dtl.first_date_time_available.strftime("%a, %-d %b %Y @ %-I:%M %p"),
                    'wait_time_mins': '< 10m',
                    'result_time_hours': '{}h'.format(dtl.average_processing_time),
                    'slots_available': dtl.slot_count*8,
                    'type': 'public',
                    'map_thumbnail': map_thumbnail,
                    'services_available': dtl.location.services_available,
                    "label": location_text,
                    "value": dtl.location.id
                }
            )

        log_generic(
            type=c.INFO,
            date=date,
            group_code=group_code,
            #available_locations=available_locations,
            function=whoami()
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            group_code=group_code,
            date=date,
            dtl_list=dtl_list,
            function=whoami(),
            error=err
        )

    return {
        "available_location": available_locations
    }


def bp_get_all_available_locations_and_times(group_code=c.DEFAULT_GROUP_CODE):
    if not group_code:
        group_code = c.DEFAULT_GROUP_CODE
    group_code = normalize_group_code(group_code)

    dtl_list = get_all_available_dtl(group_code)
    available_locations = __map_dtl_list_to_available_locations(dtl_list)

    return {
        "available_location": available_locations
    }


def bp_get_schedule_times_available(location_id, date):
    rows = get_available_times(location_id, date)
    available_times = []
    try:
        for row in rows:
            d = datetime.strptime(str(row['start_time']), "%H:%M:%S")

            available_times.append(
                {
                    "label": d.strftime("%I:%M %p"),
                    "value": row['id']
                }
            )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date=date,
            rows=rows,
            function=whoami(),
            error=err
        )

    return {
        "available_times": available_times
    }


def bp_generate_all_schedules():
    try:
        locations = get_all_locations()
        for location in locations:
            bp_generate_full_schedule(location['id'])

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return False


def bp_delete_schedule(location_id):
    try:
        return delete_schedule_entries_by_location_id(location_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )

    return False


def bp_delete_schedule_for_date(location_id, date_str):
    try:
        return delete_schedule_entries_by_location_id_for_date(location_id, date_str)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date_str=date_str,
            function=whoami(),
            error=err
        )

    return False


def bp_generate_full_schedule(location_id):
    try:
        print('START schedule generation / location id: {} / at: {}'.format(
            location_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        latest_schedule_dt = datetime.today() - timedelta(days=1)
        latest_schedule_dt = latest_schedule_dt.replace(
            hour=0, minute=0, second=0, microsecond=0)

        delete_schedule_entries_by_location_id(location_id)
        trim_schedule_generation_rules_start_dt(location_id, latest_schedule_dt)
        rules = get_schedule_generation_rules_by_location_id(location_id)

        for rule in rules:
            __process_schedule_rule(rule)

        print('END schedule generation / location id: {} / at: {}'.format(
            location_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )

    return False


def bp_add_schedule_generation_rule(data):
    try:
        # Zero out the seconds and hours for dt fields
        data.local_start_time = data.local_start_time.replace(second=0)
        data.local_end_time = data.local_start_time.replace(second=0)
        data.active_local_start_dt = data.active_local_start_dt.replace(
            hour=0, minute=0, second=0)
        data.active_local_end_dt = data.active_local_end_dt.replace(
            hour=0, minute=0, second=0)

        return add_schedule_generation_rule(data)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            data=data,
            function=whoami(),
            error=err
        )

    return False


def bp_update_schedule_generation_rule(data):
    try:
        # Zero out the seconds and hours for dt fields
        data.local_start_time = data.local_start_time.replace(second=0)
        data.local_end_time = data.local_end_time.replace(second=0)
        data.active_local_start_dt = data.active_local_start_dt.replace(
            hour=0, minute=0, second=0)
        data.active_local_end_dt = data.active_local_end_dt.replace(
            hour=0, minute=0, second=0)

        return update_schedule_generation_rule(data)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            data=data,
            function=whoami(),
            error=err
        )

    return False


def bp_delete_schedule_generation_rule(id):
    try:
        return delete_schedule_generation_rule(id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            id=id,
            function=whoami(),
            error=err
        )

    return False


def bp_get_schedule_generation_rules(location_id):
    try:
        return get_schedule_generation_rules_by_location_id(location_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )

    return False

########################################################################################################
# [Protected] functions
########################################################################################################


def __process_schedule_rule(rule):
    try:
        location_id = rule['location_id']
        rule_type = rule['rule_type']
        start_date = rule['active_local_start_dt']
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date = rule['active_local_end_dt']
        start_time = rule['local_start_time']
        end_time = rule['local_end_time']
        schedule_date = start_date
        current_dt = datetime.today()

        if rule_type == 'exception':
            bp_delete_schedule_for_date(location_id, start_date_str)

        rows = []
        valid_days = __get_valid_days(rule)
        while schedule_date <= end_date:  # day loop
            if (current_dt - schedule_date).days < 2:
                if valid_days[schedule_date.strftime("%A")]:
                    day_end_dt = schedule_date + end_time
                    day_curr_time = schedule_date + start_time

                    while day_curr_time <= day_end_dt:  # time loop
                        slot_increment = rule['slot_increment'] * 60
                        day_curr_appointment_end_time = day_curr_time + \
                            timedelta(0, slot_increment)

                        row = (
                            location_id,
                            day_curr_time.strftime('%Y-%m-%d %H:%M:%S'),
                            day_curr_appointment_end_time,
                            rule['time_zone'],
                            rule['time_zone_offset'],
                            slot_increment,
                            'available'
                        )

                        for _ in range(rule['slot_multiplier']):
                            rows.append(row)

                        day_curr_time = day_curr_appointment_end_time

            schedule_date = schedule_date + timedelta(days=1)

        if rows:
            rows = __remove_reserved_slots(rows, location_id)
        if rows:
            add_schedule_entries(rows)
        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rule=rule,
            function=whoami(),
            error=err
        )


def __get_valid_days(row):
    return {
        'Sunday': True if row['sun'] else False,
        'Monday': True if row['mon'] else False,
        'Tuesday': True if row['tue'] else False,
        'Wednesday': True if row['wed'] else False,
        'Thursday': True if row['thu'] else False,
        'Friday': True if row['fri'] else False,
        'Saturday': True if row['sat'] else False
    }


def __remove_reserved_slots(rows, location_id):
    try:
        generated_dt_counts = {}  # counts map
        generated_dt_list = []  # flat list
        for row in rows:
            dtkey = row[1]
            if dtkey in generated_dt_list:
                generated_dt_counts[dtkey] = generated_dt_counts[dtkey] + 1
            else:
                generated_dt_counts[dtkey] = 1
                generated_dt_list.append(dtkey)

        reserved_slots = get_slots_matching_dt_list(
            generated_dt_list, location_id)

        for slot in reserved_slots:
            slot_start_dt_str = slot.start_dt.strftime('%Y-%m-%d %H:%M:%S')
            if slot_start_dt_str in generated_dt_counts:
                val = generated_dt_counts[slot_start_dt_str]
                if val <= 1:
                    generated_dt_counts.pop(slot_start_dt_str)
                else:
                    generated_dt_counts[slot_start_dt_str] = val - 1

        for row in rows:
            dtkey = row[1]
            if dtkey in generated_dt_counts:
                val = generated_dt_counts[dtkey]
                if val <= 1:
                    generated_dt_counts.pop(dtkey)
                else:
                    generated_dt_counts[dtkey] = val - 1
            else:
                rows.remove(row)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )

    return rows


def __map_dtl_list_to_available_locations(dtl_list):
    available_locations = []

    if dtl_list is None:
        return available_locations

    try:
        for dtl in dtl_list:
            if dtl.location.addr2:
                addr2 = dtl.location.addr2
            else:
                addr2 = ''

            location_text = "{} {}, {}, {}  {}".format(
                dtl.location.addr1,
                addr2,
                dtl.location.city,
                dtl.location.st,
                dtl.location.zip
            )

            if dtl.location.image_thumbnail:
                map_thumbnail = 'data:image/jpeg;base64,{}'.format(
                    dtl.location.image_thumbnail)
            else:
                map_thumbnail = get_map_thumbnail_url(location_text)

            available_locations.append(
                {
                    'id': dtl.location.id,
                    'name': dtl.location.name,
                    'address': location_text,
                    'lat': dtl.location.lat,
                    'lng': dtl.location.lng,
                    'billing_type': dtl.location.billing_type,
                    'collect_insurance_info': dtl.location.collect_insurance_info,
                    'allow_insurance_skip': dtl.location.allow_insurance_skip,
                    'collect_upfront_payment': dtl.location.collect_upfront_payment,
                    'next_test_date': dtl.first_date_time_available.strftime("%a, %-d %b %Y @ %-I:%M %p"),
                    'wait_time_mins': '< 10m',
                    'result_time_hours': '{}h'.format(dtl.average_processing_time),
                    'slots_available': dtl.slot_count*8,
                    'type': 'public',
                    'map_thumbnail': map_thumbnail,
                    'services_available': dtl.location.services_available,
                    "label": location_text,
                    "value": dtl.location.id
                }
            )

        '''
        log_generic(
            type=c.INFO,
            available_locations=available_locations,
            function=whoami()
        )
        '''

    except Exception as err:
        log_generic(
            type=c.ERROR,
            dtl_list=dtl_list,
            function=whoami(),
            error=err
        )

    return available_locations


def normalize_group_code(group_code):
    whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    group_code = ''.join(filter(whitelist.__contains__, group_code.upper()))
    return group_code
