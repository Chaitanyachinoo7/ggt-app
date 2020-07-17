from datetime import datetime
from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.schedules import (
    get_available_dates,
    get_available_locations,
    get_available_times,
    get_slot_information
)

########################################################################################################
# [Public] functions
########################################################################################################
def bp_get_schedule_dates_available(group_code):
    rows = get_available_dates(group_code)
    available_dates = []
    for row in rows:
        date_str = row['available_date']
        # label_str = datetime.strptime(date_str, '%Y-%m-%d').strftime("%A %B %d, %Y") #this works by itself, bu errors here
        available_dates.append(
            {
                "label": date_str,
                "value": date_str
            }
        )

        log_generic(type="info", available_dates=available_dates, function='get_schedule_dates_available')

    return {
        "available_dates": available_dates
    }


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
########################################################################################################
# [Protected] functions
########################################################################################################