import os
import sys
import time

import pytest
import nest_asyncio

nest_asyncio.apply()
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from fastapi.testclient import TestClient
from ggt.lib.db import read_rows, exec_delete
from main import app
from tests.resources import group, location, schedule_generation_rule, token

client = TestClient(app)


def verify_response(response, expected_status_code=200, expected_status='success'):
    print(response.json())
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def get_group_id_by_code(code):
    sql = """SELECT * FROM ggt_prod.groups WHERE group_code = %s"""
    vals = (code,)
    _group = read_rows(sql, vals)
    return _group[0]['id']

def get_location_id_by_name(name):
    sql = """SELECT * FROM locations WHERE name = %s"""
    vals = (name,)
    _location = read_rows(sql, vals)
    return _location[0]['id']

def get_rule_by_location_id(id_):
    sql = """SELECT * FROM schedule_generation_rules WHERE location_id = %s"""
    vals = (id_,)
    _location = read_rows(sql, vals)
    return _location[0]['id']

def delete_group_by_code(code):
    sql = """DELETE FROM ggt_prod.groups WHERE group_code = %s"""
    vals = (code,)
    return exec_delete(sql, vals)


def test_get_states():
    response = client.get(
        "/api/portal/site-admin/get_states",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)


def test_get_locations():
    response = client.get(
        "/api/portal/site_admin/location/get_locations",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)


def test_get_all_groups():
    response = client.get(
        "/api/portal/site-admin/get_all_groups",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)


def test_get_all_services():
    response = client.get(
        "/api/portal/site-admin/get_all_services",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)


@pytest.mark.parametrize("location_id", [1, -10])
def test_generate_schedule(location_id):
    response = client.get(
        "/api/portal/site-admin/generate_schedule/{0}".format(location_id),
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)

@pytest.mark.parametrize('group_', [group])
def test_create_group(group_):
    response = client.post(
        "/api/portal/site-admin/create_group",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=group_
    )
    verify_response(response)


@pytest.mark.parametrize('location_', [location])
def test_create_location(location_):
    response = client.post(
        "/api/portal/site-admin/create_location",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=location_
    )
    verify_response(response)


@pytest.mark.asyncio
def test_group_update():
    group_id = get_group_id_by_code(group["group_code"])
    _update = group.copy()
    _update['id'] = group_id
    _update['account'] = "TEST ACCOUNT 2"
    response = client.post(
        "/api/portal/site-admin/update_group",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=_update
    )
    verify_response(response)
    # delete_group_by_code(group["group_code"])

def test_assign_group():
    location_id = get_location_id_by_name(location["name"])
    group_id = get_group_id_by_code(group["group_code"])

    response = client.post(
        "/api/portal/site_admin/location/assign_group",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"location_id": location_id, "group_id": group_id}
    )
    verify_response(response)

def test_remove_group():
    location_id = get_location_id_by_name(location["name"])
    group_id = get_group_id_by_code(group["group_code"])

    response = client.post(
        "/api/portal/site_admin/location/remove_groups",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"location_id": location_id, "group_id": group_id}
    )
    verify_response(response)

def test_assign_service():
    location_id = 1
    service_id = 3

    response = client.post(
        "/api/portal/site_admin/location/assign_service",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"location_id": location_id, "service_id": service_id}
    )
    verify_response(response)

def test_remove_service():
    location_id = 1
    service_id = 1

    response = client.post(
        "/api/portal/site_admin/location/remove_service",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"location_id": location_id, "service_id": service_id}
    )
    verify_response(response)

def test_update_location():
    location_id = get_location_id_by_name(location["name"])

    new_location = location.copy()
    new_location["id"] = location_id
    new_location["website"] = "www.test.com"
    new_location["location_name"] = new_location.pop("name")

    response = client.post(
        "/api/portal/site-admin/update_location",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=new_location
    )
    verify_response(response)

def test_generate_all_schedules():
    response = client.post(
        "/api/portal/site-admin/generate_all_schedules",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)

def test_location_search():

    response = client.post(
        "/api/portal/site-admin/location_search",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"location_name": "TEST_LOCATION", "site_code": "", "group_code": "", "account": "", "st": ""}
    )
    verify_response(response)

def test_add_schedule_generation_rule():
    location_id = get_location_id_by_name(location["name"])
    schedule_generation_rule["location_id"] = location_id

    response = client.post(
        "/api/portal/site-admin/add_schedule_generation_rule",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=schedule_generation_rule
    )
    verify_response(response)

def test_edit_schedule_generation_rule():
    location_id = get_location_id_by_name(location["name"])
    rule_id = get_rule_by_location_id(location_id)
    new_rule = schedule_generation_rule.copy()
    new_rule["location_id"] = location_id
    new_rule["mon"] = True

    response = client.post(
        "/api/portal/site-admin/add_schedule_generation_rule",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=new_rule
    )
    verify_response(response)

def test_get_schedule_generation_rules():
    location_id = get_location_id_by_name(location["name"])
    response = client.get(
        "/api/portal/site-admin/get_schedule_generation_rules/{0}".format(location_id),
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)

def test_delete_schedule_generation_rule():
    location_id = get_location_id_by_name(location["name"])
    rule_id = get_rule_by_location_id(location_id)

    response = client.post(
        "/api/portal/site-admin/delete_schedule_generation_rule/{0}".format(rule_id),
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)

def test_patient_lookup(name='Dhimal', dob=''):
    response = client.post(
        "/api/portal/contact-center/patient_lookup",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"last_name": name, "dob": dob}
    )
    verify_response(response)

def test_general_search():
    criteria = {
       "appointment_date":"",
       "appointment_id":1,
       "auth_token":"",
       "dob":"",
       "email":"",
       "first_name":"",
       "group_code":"",
       "last_name":"",
       "location_id":"",
       "middle_name":"",
       "phone_number":""
    }
    response = client.post(
        "/api/portal/site-admin/general_search",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json=criteria
    )
    verify_response(response)

def test_patient_lookup():

    response = client.post(
        "/api/portal/contact-center/patient_lookup",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "last_name": "Dhimal",
            "dob": "2000-10-01"
        }
    )
    verify_response(response)
