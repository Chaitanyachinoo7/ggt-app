from ggt.lib.db import read_rows, exec_insert, exec_update, exec_delete
from ggt.models.process_models.bp_portal_experience import bp_create_location
from ggt.models.workflow_models.clinical_test_site_admin_flow import add_schedule_generation_rule
from ggt.models.data_models.data_types import GgtDbLocation, ScheduleGenerationRule
import hashlib
import json


def rebuild_appsheet_database():
    appsheet_data = read_appsheet_databse()
    if not appsheet_data:
        print("No data in appsheet!")
        return
    if is_rebuild_required(appsheet_data):
        inserted_data = insert_into_locations_table(appsheet_data)
        if len(appsheet_data) != len(inserted_data):
            print("Data not persisted properly, expected {0} rows to be inserted, but only {} were actually inserted".format(len(appsheet_data), len(inserted_data)))
    else:
        print("Rebuild not required")

def read_appsheet_databse():
    sql = """SELECT * FROM vendor_bcg_appsheet_location_data"""
    return read_rows(sql,)

def is_rebuild_required(data):
    new_md5 = _compute_md5(data)
    old_md5 = _get_current_md5()

    print("Old md5: ", old_md5)
    print("New md5: ", new_md5)

    if new_md5 == old_md5:
        return False

    _set_current_md5(new_md5, update_existing=bool(old_md5))
    return True

def _compute_md5(data):
    sorted_data = sorted(data, key=lambda x: x['id'])
    return hashlib.md5(json.dumps(sorted_data, sort_keys=True).encode('utf-8')).hexdigest()

def _get_current_md5():
    sql = """SELECT * FROM vendor_bcg_sppsheet_md5 where id = 1"""
    result = read_rows(sql,)
    if not result:
        return None
    return result[0]['md5']


def _set_current_md5(value, update_existing=True):
    if update_existing:
        print("updating existing md5")
        sql = """UPDATE vendor_bcg_sppsheet_md5 SET md5 = %s WHERE id = 1"""
        vals = (value,)
        exec_update(sql, vals)
    else:
        print("insertng new md5")
        sql = """INSERT INTO vendor_bcg_sppsheet_md5 values (%s, %s)"""
        vals = (1, value,)
        exec_insert(sql, vals)

def insert_into_locations_table(data):
    sql = """DELETE from locations where org_id = 2 and id > -1"""
    exec_delete(sql)

    for location in data:
        _add_to_locations(
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

    sql = """SELECT * from locations where org_id = 2"""
    return read_rows(sql)

def _add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
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
        result = bp_create_location(GgtDbLocation(**payload), 2)
        print("created location", result)
        location_id = result['location_id']
        add_sched_rule(location_id)

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
        location_id = res['results'][0]['location_id']

    except Exception as err:
        print(err)
