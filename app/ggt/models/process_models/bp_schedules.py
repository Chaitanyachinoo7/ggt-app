from datetime import datetime
from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.schedules import (
    get_available_dates,
    get_available_locations,
    get_available_times,
    get_slot_information,
    get_schedule_generation_rules_by_location_id
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

            log_generic(type="info", available_dates=available_dates, function='get_schedule_dates_available')

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

        log_generic(type="info", date=date, group_code=group_code, available_locations=available_locations, function='get_schedule_locations_available')

    except Exception as err:
        log_generic(type="error", group_code=group_code, date=date, rows=rows, function='get_schedule_locations_available', error=err)
    
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




'''
def generate_full_schedule(location_id, start_date, day_count):
    try:
        record = get_schedule_generation_rules_by_location_id(location_id)
        if(record):
            sun = True if record['sun'] else False
            mon = True if record['mon'] else False
            tue = True if record['tue'] else False
            wed = True if record['wed'] else False
            thu = True if record['thu'] else False
            fri = True if record['fri'] else False
            sat = True if record['sat'] else False

            start_date = record['active_start_dt']
            end_date = record['active_end_dt']
            start_time = record['start_time']
            end_time = record['end_time']

            slot_increment = record['slot_increment'] * 60
            slot_multiplier = record['slot_multiplier']

            start_time = datetime.datetime(2020,7,20,9,0,0)
            end_time = datetime.datetime(2020,7,20,16,0,0)

            curr_time = start_time

            while curr_time < end_time:
                for x in range(slot_multiplier):
                    print(curr_time)

            curr_time = curr_time + datetime.timedelta(0,slot_increment)

    except Exception as err:
        log_generic(type="error", 
                location_id=location_id, 
                start_date=start_date, 
                day_count=day_count,
                function='generate_full_schedule', 
                error=err)
    
    return False
'''

########################################################################################################
# [Protected] functions
########################################################################################################
