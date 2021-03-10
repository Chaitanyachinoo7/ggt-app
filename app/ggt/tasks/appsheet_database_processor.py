from ggt.lib.db import read_rows, exec_insert, exec_update, exec_delete
from ggt.models.process_models.bp_portal_experience import bp_create_location, bp_update_location
from ggt.models.workflow_models.clinical_test_site_admin_flow import add_schedule_generation_rule
from ggt.models.data_models.data_types import GgtDbLocation, ScheduleGenerationRule, GgtUpdateLocation
from ggt.models.data_models.locations import remove_all_group, remove_all_service
from datetime import datetime, timedelta
import hashlib
import json
import time


def rebuild_appsheet_database():
    appsheet_data = read_appsheet_databse()

    additions = get_additions(appsheet_data)
    print("additions ", additions)
    insert_in_locations_table(additions)

    time.sleep(10)

    updates = get_updations(appsheet_data)
    print("updates ",  updates)
    update_in_locations_table(updates)

    time.sleep(10)

    deletions = get_deletions()
    print("deletions ", deletions)
    delete_in_locations_table(deletions)

    print("DONE")


def get_deletions():
    data = read_appsheet_databse()
    sql = """SELECT id FROM locations where org_id = 2"""
    all_locations = read_rows(sql,)
    expected_ids = set(item['location_id'] for item in data)
    actual_ids = set(item['id'] for item in all_locations)
    to_be_deleted = actual_ids.difference(expected_ids)
    return list(to_be_deleted)

def get_updations(data):
    updations = []
    for item in data:
        if item['processed_dt'] and item['update_dt'] > item['processed_dt'] + timedelta(seconds=30) and item['location_id']:
            updations.append(item)
    return updations

def get_additions(data):
    additions = []
    for item in data:
        if item['location_id'] is None or item['processed_dt'] is None:
            additions.append(item)
    return additions

def read_appsheet_databse():
    sql = """SELECT * FROM vendor_bcg_appsheet_location_data"""
    return read_rows(sql,)

def delete_in_locations_table(data):
    for location_id in data:
        print("DELETING LOCATION ID: ", location_id)
        remove_all_group(location_id)
        remove_all_service(location_id)
        remove_all_schedule_rules(location_id)
        sql = """DELETE FROM locations where id = %s"""
        vals = (location_id,)
        exec_delete(sql, vals)

def remove_all_schedule_rules(location_id):
    sql = """DELETE FROM schedule_generation_rules where location_id = %s"""
    vals = (location_id,)
    exec_delete(sql, vals)

def update_in_locations_table(data):
    for location in data:
        location_id = _update_to_locations(
            location['location_id'],
            location['id'],
            location['location_name'] + "|" + location['open_hours'],
            location['addr1'],
            location['addr2'],
            location['city'],
            location['st'],
            location['zip'],
            location['operator'],
            location['cta_phone_number'],
            location['cta_website'],
            location['open_hours']
        )

def insert_in_locations_table(data):

    for location in data:
        location_id = _add_to_locations(
            location['id'],
            location['location_name'] + "|" + location['open_hours'],
            location['addr1'],
            location['addr2'],
            location['city'],
            location['st'],
            location['zip'],
            location['operator'],
            location['cta_phone_number'],
            location['cta_website'],
            location['open_hours']
        )

def _update_to_locations(location_id, appsheet_id, name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
    payload = {
        "id": location_id,
        "site_code": "GGT",
        "group_code": "_DEFAULT_",
        "location_name": name,
        "addr1": addr1,
        "addr2": addr2,
        "addr3": "",
        "city": city,
        "st": st,
        "zip": zip,
        "lat": 0,
        "lng": 0,
        "time_zone": "CST",
        "time_zone_offset": "-06:00",
        "test_type_offered": "oral",
        "status": "enabled",
        "type": "drive_thru",
        "billing_type": "client_bill",
        "collect_insurance_info": 0,
        "allow_insurance_skip": 1,
        "collect_upfront_payment": 0,
        "image_thumbnail": "",
        "accepts_bookings": True,
        "accepts_walkins": True,
        "operator": operator,
        "phone_number": phone_number,
        "website": website,
        "open_hours": open_hours,
        "is_external": True,
        "group_ids": [1],
        "service_ids": [1]
    }

    try:
        result = bp_update_location(GgtUpdateLocation(**payload), 2)[0]
        print("updated location", result)
        location_id = result['location_id']

        sql = """UPDATE  vendor_bcg_appsheet_location_data SET processed_dt = %s WHERE id = %s"""
        now = datetime.utcnow()
        vals = (now, appsheet_id,)
        exec_update(sql, vals)

        add_sched_rule(location_id)
        return location_id

    except Exception as err:
        print(err)

def _add_to_locations(appsheet_id, name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
    payload = {
        "site_code": "GGT",
        "group_code": "_DEFAULT_",
        "name": name,
        "addr1": addr1,
        "addr2": addr2,
        "addr3": "",
        "city": city,
        "st": st,
        "zip": zip,
        "lat": 0,
        "lng": 0,
        "time_zone": "CST",
        "time_zone_offset": "-06:00",
        "test_type_offered": "oral",
        "status": "enabled",
        "type": "drive_thru",
        "billing_type": "client_bill",
        "collect_insurance_info": 0,
        "allow_insurance_skip": 1,
        "collect_upfront_payment": 0,
        "image_thumbnail": "",
        "accepts_bookings": True,
        "accepts_walkins": True,
        "operator": operator,
        "phone_number": phone_number,
        "website": website,
        "open_hours": open_hours,
        "is_external": True,
        "group_ids": [1],
        "service_ids": [1]
    }

    try:
        result = bp_create_location(GgtDbLocation(**payload), 2)[0]
        print("created location", result)
        location_id = result['location_id']

        sql = """UPDATE  vendor_bcg_appsheet_location_data SET location_id = %s, processed_dt = %s WHERE id = %s"""
        now = datetime.utcnow()
        vals = (location_id, now, appsheet_id,)
        exec_update(sql, vals)

        add_sched_rule(location_id)
        return location_id

    except Exception as err:
        print(err)


def add_sched_rule(location_id):
    payload = {
        "rule_type": "regular",
        "time_zone": "string",
        "time_zone_offset": "string",
        "status": "enabled",
        "location_id": location_id,
        "category": "test",
        "slot_increment": 10,
        "slot_multiplier": 1,
        "local_start_time": "09:00:00",
        "local_end_time": "09:10:00",
        "active_local_start_dt": "2021-12-31 09:00:00",
        "active_local_end_dt": "2021-12-31 09:10:00",
        "sun": True,
        "mon": True,
        "tue": True,
        "wed": True,
        "thu": True,
        "fri": True,
        "sat": True
    }
    try:
        res = add_schedule_generation_rule(ScheduleGenerationRule(**payload))

    except Exception as err:
        print(err)
