import json
from datetime import date, datetime, timedelta

from ggt.lib.adapters.dynamo_adapter import read_from_dynamo
from ggt.lib.adapters.mysql_adapter import exec_update
from ggt.lib.adapters.sqs_adapter import push_sqs_message
from ggt.lib.sms import send_sms
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami, get_sqs_queue_url, is_international
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
    get_slots_matching_dt_list, ggv_get_schedule_locations_available_near_lat_lng, get_second_shot_available_times,
    delete_ggv_schedules_metrics_cache, delete_schedules_metrics_cache, get_second_slot_reschedule_dates,
    get_ggv_available_dates, get_group_by_group_code, get_available_ggv_locations_near_lat_lng,
    get_first_available_times, lookup_certificate, update_patient_ifo_cert, update_cert_info, delete_certificate,
    verify_certificate, get_patient_from_crt_number, get_certificate_stats, get_phone_number_by_certificate_id
)

from ggt.models.data_models.locations import (
    get_all_locations,
    get_services_available_for_location
)

from ggt.lib.maps import (
    get_map_thumbnail_url
)

from cachetools import cached, LRUCache, TTLCache
from ggt.models.process_models.bp_patient_experience import __upload_vax_card_image, __send_ggv_certificate_level_1_sms, \
    __send_ggv_certificate_level_1_email

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


def bp_get_ggv_schedule_dates_available(group_code):
    try:
        group_code = normalize_group_code(group_code)
        rows = get_ggv_available_dates(group_code)
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


def bp_get_schedule_locations_available_near_lat_lng(lat: float, lng: float, radius: int = None, date_str: str = None,
                                                     group_code: str = None):
    if not radius:
        radius = 100

    if not group_code:
        group_code = c.DEFAULT_GROUP_CODE

    # if not date_str:
        # date_str = date.today().strftime("%Y-%m-%d")

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

            available_locations.append(
                {
                    'id': dtl.location.id,
                    'name': dtl.location.name,
                    'address': location_text,
                    'address_state':  dtl.location.st,
                    'lat': dtl.location.lat,
                    'lng': dtl.location.lng,
                    'billing_type': dtl.location.billing_type,
                    'collect_insurance_info': dtl.location.collect_insurance_info,
                    'allow_insurance_skip': dtl.location.allow_insurance_skip,
                    'collect_upfront_payment': dtl.location.collect_upfront_payment,
                    'next_test_date': dtl.first_date_time_available.strftime(
                        "%a, %-d %b %Y @ %-I:%M %p") if dtl.first_date_time_available else None,
                    'wait_time_mins': '< 10m',
                    'result_time_hours': '{}h'.format(dtl.average_processing_time),
                    'slots_available': dtl.slot_count,
                    'type': 'public',
                    'services_available': json.loads(dtl.services_available),
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
            # available_locations=available_locations,
            function=whoami()
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            group_code=group_code,
            date_str=date_str,
            # dtl_list=dtl_list,
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
                    'slots_available': dtl.slot_count * 8,
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
            # available_locations=available_locations,
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


def bp_ggv_get_schedule_locations_available_near_lat_lng(group_code, lat, lng, radius):
    try:
        return ggv_get_schedule_locations_available_near_lat_lng(group_code, lat, lng, radius)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            group_code=group_code,
            function=whoami(),
            error=err
        )


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
            function=whoami(),
            error=err
        )

    return {
        "available_times": available_times
    }


def bp_get_second_slot_reschedule_dates(location_id, ap1_date):
    available_dates = []
    try:
        rows = get_second_slot_reschedule_dates(location_id, ap1_date)
        if rows and len(rows) > 0:
            for row in rows:
                available_dates.append(row['available_date'])
        return {
            "available_dates": available_dates
        }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date=date,
            function=whoami(),
            error=err
        )
        return {
            "available_dates": []
        }


def bp_get_ggv_schedule_times_available(location_id, date):
    available_times = []
    dates = {}
    res = []
    try:
        rows = get_first_available_times(location_id, date)
        for row in rows:
            d = datetime.strptime(str(row['start_time']), "%H:%M:%S")
            day = str(datetime.strptime(str(row['start_dt'])[0:10], "%Y-%m-%d"))[0:10]

            if day in dates.keys():
                dates[day]['available_times'].append(
                    {
                        "label": d.strftime("%I:%M %p"),
                        "value": row['id']
                    }
                )
            else:
                dates[day] = {
                    "available_times": [
                        {
                            "label": d.strftime("%I:%M %p"),
                            "value": row['id']
                        }
                    ]
                }

        for key in dates.keys():
            res.append({
                "date": key,
                "available_times": dates[key]['available_times']
            })

        # print('***************************START - 1  {}******************************'.format(datetime.now()))
        # request = {
        #     "date": date,
        #     "id": location_id,
        #     "r_type": 1
        # }
        #
        # r = json.dumps(request)
        # msg_id = push_sqs_message(get_sqs_queue_url(location_id), r)
        # if msg_id:
        #     start_time = datetime.now()
        #     while True:
        #         x = x + 1
        #         res = read_from_dynamo(get_config_val('aws.dynamo_table_name'), msg_id)
        #         if res and "Item" in res.keys():
        #             temp = res['Item']
        #             if temp['available_times']:
        #                 for r in temp['available_times']:
        #                     r['value'] = int(r['value'])
        #             print("xxxxx - {}".format(x))
        #             print(
        #                 '***************************Exit - 1  {}******************************'.format(datetime.now()))
        #             return temp
        #         else:
        #             if (datetime.now() - start_time).total_seconds() > 10:
        #                 print("xxxxx - {}".format(x))
        #                 print('***************************Exit Failed - 1  {}******************************'.format(
        #                     datetime.now()))
        #                 return None

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date=date,
            function=whoami(),
            error=err
        )
    print('***************************EXIT - 1 - end  {}******************************'.format(datetime.now()))
    return {
        "available_times": res[0]['available_times']
    }


# @cached(cache=TTLCache(maxsize=1024, ttl=60))
def bp_get_second_shot_available_times(location_id, date):
    # x = 0
    # try:
    #     request = {
    #         "date": date,
    #         "id": location_id,
    #         "r_type": 2
    #     }
    #     print('***************************START - 2  {}******************************'.format(datetime.now()))
    #     r = json.dumps(request)
    #     msg_id = push_sqs_message(get_sqs_queue_url(location_id), r)
    #     if msg_id:
    #         start_time = datetime.now()
    #         while True:
    #             x = x + 1
    #             res = read_from_dynamo(get_config_val('aws.dynamo_table_name'), msg_id)
    #             if res and "Item" in res.keys():
    #                 temp = res['Item']
    #                 if temp['available_times']:
    #                     for x in temp['available_times']:
    #                         for y in x['available_times']:
    #                             y['value'] = int(y['value'])
    #                 print("xxxxx - {}".format(x))
    #                 print(
    #                     '***************************Exit - 2  {}******************************'.format(datetime.now()))
    #                 return {
    #                     "available_dates": temp['available_times']
    #                 }
    #             else:
    #                 if (datetime.now() - start_time).total_seconds() > 10:
    #                     print("xxxxx - {}".format(x))
    #                     print('***************************Exit Failed - 2  {}******************************'.format(
    #                         datetime.now()))
    #                     return None

    rows = get_second_shot_available_times(location_id, date)
    dates = {}
    res = []
    try:
        for row in rows:
            d = datetime.strptime(str(row['start_time']), "%H:%M:%S")
            day = str(datetime.strptime(str(row['start_dt'])[0:10], "%Y-%m-%d"))[0:10]

            if day in dates.keys():
                dates[day]['available_times'].append(
                    {
                        "label": d.strftime("%I:%M %p"),
                        "value": row['id']
                    }
                )
            else:
                dates[day] = {
                    "available_times": [
                        {
                            "label": d.strftime("%I:%M %p"),
                            "value": row['id']
                        }
                    ]
                }

        for key in dates.keys():
            res.append({
                "date": key,
                "available_times": dates[key]['available_times']
            })

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date=date,
            # rows=rows,
            function=whoami(),
            error=err
        )

    return {
        "available_dates": res
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


def bp_lookup_certificate(first_name, last_name, dob, phone_number):
    try:
        return lookup_certificate(phone_number, dob, first_name, last_name)[0]

    except Exception as err:
        log_generic(
            type=c.ERROR,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return False


def bp_lookup_unverified_certificate(first_name, last_name, dob, phone_number, limit, offset):
    try:
        return lookup_certificate(phone_number, dob, first_name, last_name, None, 1, limit, offset)[0]

    except Exception as err:
        log_generic(
            type=c.ERROR,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return False


def bp_update_patient_ifo_cert(id, first_name, last_name, dob, phone_number):
    try:
        return update_patient_ifo_cert(id, phone_number, dob, first_name, last_name)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )

    return False


def bp_update_cert_info(id, service_code, lot_no, vax_date):
    try:
        vax_date = "{} 00:00:00".format(vax_date)
        return update_cert_info(id, service_code, lot_no, vax_date)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            service_code=service_code,
            lot_no=lot_no,
            function=whoami(),
            error=err
        )

    return False


def bp_delete_certificate(cert_id, notify_customer):
    try:
        if notify_customer:
            res = get_phone_number_by_certificate_id(cert_id)
            phone_number = res['phone_number']
            international = is_international(phone_number)
            message = "We were unable to validate your submission. " \
                    "You can resubmit your request by going to  " \
                    "http://vaxyes.com  and entering in your phone number.  " \
                    "Please make sure you take clear photos of your ID and " \
                    "Vaccine card in order to process"
            send_sms(phone_number,
                    message.replace('\t', ''), international=international)
        return delete_certificate(cert_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            cert_id=cert_id,
            function=whoami(),
            error=err
        )

    return False


def bp_get_certificate_stats():
    try:
        return get_certificate_stats()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return False


def bp_delete_schedule_for_date(location_id, date_str, category):
    try:
        return delete_schedule_entries_by_location_id_for_date(location_id, date_str, category)

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
            delete_ggv_schedules_metrics_cache(rule['id'])
            delete_schedules_metrics_cache(rule['id'])
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
        data.local_end_time = data.local_end_time.replace(second=0)
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
        if delete_schedule_generation_rule(id):
            delete_ggv_schedules_metrics_cache(id)
            delete_schedules_metrics_cache(id)
            return True
        else:
            return False

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


def bp_verify_certificate(cert_id, verification_level):
    try:
        verify_certificate(cert_id, verification_level)
        patient = get_patient_from_crt_number(cert_id)
        __send_ggv_certificate_level_1_sms(patient["first_name"], patient["phone_number"])
        __send_ggv_certificate_level_1_email(patient["first_name"], patient["email"])
        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            cert_id=cert_id,
            verification_level=verification_level,
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
        rule_id = rule['id']
        category = rule['category']
        rule_type = rule['rule_type']
        start_date = rule['active_local_start_dt']
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date = rule['active_local_end_dt']
        start_time = rule['local_start_time']
        end_time = rule['local_end_time']
        schedule_date = start_date
        current_dt = datetime.today()

        if rule_type == 'exception':
            bp_delete_schedule_for_date(location_id, start_date_str, category)

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
                            'available',
                            rule_id
                        )

                        for _ in range(rule['slot_multiplier']):
                            rows.append(row)

                        day_curr_time = day_curr_appointment_end_time

            schedule_date = schedule_date + timedelta(days=1)

        if rows:
            rows = __remove_reserved_slots(rows, location_id, category)
        if rows:
            add_schedule_entries(rows, category)
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


def __remove_reserved_slots(rows, location_id, category):
    try:
        generated_dt_counts = {}  # counts map
        generated_dt_list = []  # flat list
        selected_rows = []
        deleted_rows = []
        for row in rows:
            dtkey = row[1]
            if dtkey in generated_dt_list:
                generated_dt_counts[dtkey] = generated_dt_counts[dtkey] + 1
            else:
                generated_dt_counts[dtkey] = 1
                generated_dt_list.append(dtkey)

        reserved_slots = get_slots_matching_dt_list(
            generated_dt_list, location_id, category)

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
                selected_rows.append(row)
                if val <= 1:
                    generated_dt_counts.pop(dtkey)
                else:
                    generated_dt_counts[dtkey] = val - 1
            else:
                # rows.remove(row)
                deleted_rows.append(row)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )

    return selected_rows


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
                    'next_test_date': dtl.first_date_time_available.strftime(
                        "%a, %-d %b %Y @ %-I:%M %p") if dtl.first_date_time_available else None,
                    'wait_time_mins': '< 10m',
                    'result_time_hours': '{}h'.format(dtl.average_processing_time),
                    'slots_available': dtl.slot_count * 8,
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
    whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
    group_code = ''.join(filter(whitelist.__contains__, group_code.upper()))
    return group_code

