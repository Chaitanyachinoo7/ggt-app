from ggt.lib.db import read_rows, exec_insert, exec_update, exec_delete, exec_batch_execute
import json
import time
import os
import sys


def add_new_groups():
    try:
        appsheet_data = read_appsheet_data()
        location_ids = get_all_location_ids(org_id=1)
        for element in appsheet_data:
            if element["approved"].upper().startswith("Y"):
                print("Processing Appsheet ID", element["id"])
                group_id = insert_into_groups(element["group_code"])
                print("Created new group:", element["group_code"], group_id)
                if group_id:
                    add_group_to_org_map(group_id, org_id=1)
                    add_group_to_locations(group_id, location_ids)
                    set_processed(element["id"])
    except Exception as e:
        print(str(e))
        return False

    return True


def set_processed(id_):
    sql = """UPDATE vendor_third_party_agents_groupcodes set is_processed = 1 where id = %s"""
    vals = (id_,)
    exec_update(sql, vals)


def add_group_to_locations(group_id, location_ids):
    vals = []
    for location_id in location_ids:
        vals.append((group_id, location_id))
    exec_batch_execute(
        "insert into group_codes_to_locations_mapping (group_id, location_id) values (%s, %s)", vals)


def get_all_location_ids(org_id):
    sql = """SELECT id FROM locations where org_id = %s"""
    vals = (org_id,)
    return [e["id"] for e in read_rows(sql, vals)]


def insert_into_groups(group_code):
    sql = """INSERT IGNORE INTO groups
                (
                    account,
                    org_id,
                    group_code,
                    is_referral_code,
                    consent_req,
                    collect_insurance,
                    insurance_req,
                    allow_insurance_skip,
                    upfront_payment_req,
                    screen_seq,
                    required_screens
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    vals = (
        group_code,
        1,
        group_code,
        1,
        0,
        0,
        0,
        1,
        0,
        'groups#US:_DEFAULT_, MX:_DEFAULT_MX_',
        'groups#US:_DEFAULT_, MX:_DEFAULT_MX_'
    )
    group_id = exec_insert(sql, vals)
    return group_id


def add_group_to_org_map(group_id, org_id):
    sql = """insert into 
                    groups_to_org_map (group_id, org_id) 
                    values (%s, %s);"""
    vals = (
        group_id,
        org_id
    )
    return exec_insert(sql, vals)


def read_appsheet_data(unprocessed_data_only=True):
    if unprocessed_data_only:
        sql = """SELECT * FROM vendor_third_party_agents_groupcodes where is_processed IN (0, NULL)"""
    else:
        sql = """SELECT * FROM vendor_third_party_agents_groupcodes"""
    return read_rows(sql,)
