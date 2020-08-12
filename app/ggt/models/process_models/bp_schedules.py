from datetime import datetime, timedelta
from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.schedules import (
    get_available_dates,
    get_available_locations,
    get_available_times,
    get_slot_information,
    get_schedule_generation_rules_by_location_id,
    add_schedule_entries
)

from ggt.models.data_models.locations import (
    get_all_locations
)

########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_schedule_dates_available(group_code):
    try:
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

            log_generic(type="info", available_dates=available_dates,
                        function='get_schedule_dates_available')

        return {
            "available_dates": available_dates
        }
    except Exception as err:
        log_generic(type="error",
                    group_code=group_code,
                    rows=rows,
                    function='bp_get_schedule_dates_available',
                    error=err)


def bp_get_schedule_locations_available(date, group_code='_DEFAULT_'):
    rows = get_available_locations(date, group_code)
    available_locations = []
    try:
        for row in rows:
            location_text = "{}, {} {}  {}".format(
                row['addr1'],
                row['city'],
                row['st'],
                row['zip'])
            available_locations.append(
                {
                    "label": location_text,
                    "value": row['location_id']
                }
            )

        log_generic(type="info", date=date, group_code=group_code,
                    available_locations=available_locations, function='get_schedule_locations_available')

    except Exception as err:
        log_generic(type="error", group_code=group_code, date=date,
                    rows=rows, function='get_schedule_locations_available', error=err)

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
        log_generic(type="error",
                    location_id=location_id,
                    date=date,
                    rows=rows,
                    function='get_schedule_times_available',
                    error=err)

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
        log_generic(type="error",
                    function='bp_generate_all_schedules',
                    error=err)

    return False



def bp_generate_full_schedule(location_id):
    try:
        rules = get_schedule_generation_rules_by_location_id(location_id)

        for rule in rules:
            __process_schedule_rule(rule)

        return True
            
    except Exception as err:
        log_generic(type="error",
                    location_id=location_id,
                    function='generate_full_schedule',
                    error=err)

    return False


########################################################################################################
# [Protected] functions
########################################################################################################
def __process_schedule_rule(rule):
    try:
        start_date = rule['active_local_start_dt']
        end_date = rule['active_local_end_dt']
        start_time = rule['local_start_time']
        end_time = rule['local_end_time']
        schedule_date = start_date

        rows = []
        valid_days = __get_valid_days(rule)
        while schedule_date <= end_date: #day loop
            if valid_days[schedule_date.strftime("%A")]: 
                day_end_dt =  schedule_date + end_time
                day_curr_time = schedule_date + start_time
                
                while day_curr_time < day_end_dt: #time loop
                    slot_increment = rule['slot_increment'] * 60
                    day_curr_appointment_end_time = day_curr_time + timedelta(0, slot_increment)

                    row = (
                        rule['location_id'], 
                        day_curr_time.strftime('%Y-%m-%d %H:%M:%S'), 
                        day_curr_appointment_end_time,  
                        rule['time_zone'],
                        rule['time_zone_offset'],
                        rule['slot_increment'],
                        'available'
                    ) 
                    rows.append(row)

                    day_curr_time = day_curr_appointment_end_time

            schedule_date = schedule_date + timedelta(days=1)

        add_schedule_entries(rows)
        return True

    except Exception as err:
        log_generic(type="error",
                    rule=rule,
                    function='__process_schedule_rule',
                    error=err)


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
