import os
import sys
import time

import nest_asyncio
import pytest
from datetime import datetime, timedelta

nest_asyncio.apply()
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from fastapi.testclient import TestClient
from main import app
from ggt.lib.db import read_rows

client = TestClient(app)

''''
Patient workflow
'''

date = datetime.today()
date_past = date - timedelta(days=10)

str_date_today = date.strftime('%Y-%m-%d')
str_date_past = date_past.strftime('%Y-%m-%d')
str_date_today_wrong_format = date.strftime('%d-%m-%Y')

dates = [str_date_today, str_date_past, str_date_today_wrong_format]


def verify_response(response, expected_status_code=200, expected_status='success'):
    print("Response", response.json())
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


@pytest.mark.parametrize("group_code", ["_DEFAULT_", "random"])
def test_get_available_dates(group_code):
    response = client.get(
        "/api/get_available_dates/{0}".format(group_code),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


@pytest.mark.parametrize("group_code", ["_DEFAULT_", "random"])
def test_get_screen_flow_seq(group_code):
    response = client.get(
        "/api/get_screen_flow_seq/{0}".format(group_code),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


@pytest.mark.parametrize("group_code", ["_DEFAULT_", "random"])
@pytest.mark.parametrize("date_", dates)
def test_get_available_locations(group_code, date_):
    # get_all_locations,get_available_locations: who builds cache tables? locations_metrics_cache - rn empty results
    response = client.get(
        "/api/get_available_locations/{0}/{1}".format(group_code, date_),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


@pytest.mark.parametrize("group_code", ["_DEFAULT_", "", "random"])
def test_get_locations(group_code):
    # get_all_locations,get_available_locations: who builds cache tables? locations_metrics_cache - rn empty results for below ones also
    response = client.get(
        "/api/get_locations/{0}".format(group_code),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)




def test_get_locations_near_me_1():
    response = client.get(
        "/api/get_locations_near_me/32.779167/-96.808891",
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


def test_get_locations_near_me_2():
    response = client.get(
        "/api/get_locations_near_me/32.779167/-96.808891/50",
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


def test_get_locations_near_me_3():
    response = client.get(
        "/api/get_locations_near_me/_DEFAULT_/32.779167/-96.808891/50",
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


def test_get_locations_near_me_4():
    date = time.strftime('%Y%m%d')
    response = client.get(
        "/api/get_locations_near_me/_DEFAULT_/{}/32.779167/-96.808891/50".format(date),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


@pytest.mark.parametrize("location_id", [1, -10])
@pytest.mark.parametrize("date_", ['2025-12-15'])
def test_get_get_available_times_1(location_id, date_):
    response = client.get(
        "/api/get_available_times/{0}/{1}".format(location_id, date_),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)


def test_get_appointment_results():
    #### Wrong token leads to failed api
    #### Wrong date leads to failed api

    sql = """SELECT * FROM detailed_test_results
                ORDER by test_id DESC
                LIMIT 1"""
    patient = read_rows(sql)
    token = patient[0]['token']

    # date format - yyyymmdd
    dob = patient[0]['dob'].strftime("%Y%m%d")
    response = client.get(
        "/api/appointment/result/{0}/{1}".format(token, dob),
        headers={"X-Token": "coneofsilence"}
    )
    verify_response(response)

    # # another date format - ddmmyyyy
    # dob = patient[0]['dob'].strftime("%d%m%Y")
    # response = client.get(
    #     "/api/appointment/result/{0}/{1}".format(token, dob),
    #     headers={"X-Token": "coneofsilence"}
    # )
    # verify_response(response)
    #
    # # wrong token
    # dob = patient[0]['dob'].strftime("%Y%m%d")
    # response = client.get(
    #     "/api/appointment/result/{0}/{1}".format("wrong_token", dob),
    #     headers={"X-Token": "coneofsilence"}
    # )
    # verify_response(response)


# def test_lookup_appointments_by_phone():
#     #### Basic test case is failing -- seems to depracated in rt_patient
#
#     sql = """SELECT * FROM appointment_with_patient LIMIT 1"""
#     appointment = read_rows(sql)
#     phone_number = appointment[0]['phone_number']
#     dob = appointment[0]['dob'].strftime("%Y%m%d")
#
#     response = client.get(
#         "/api/lookup_appointments_by_phone/{0}/{1}".format(phone_number, dob),
#         headers={"X-Token": "coneofsilence"}
#     )
#     verify_response(response)
#
#     # incorrect phone number
#     response = client.get(
#         "/api/lookup_appointments_by_phone/{0}/{1}".format(phone_number[::-1], dob),
#         headers={"X-Token": "coneofsilence"}
#     )
#     verify_response(response)

def test_lookup_appoitment():
    #### Test failure for wrong appointment ID - but error seems to be unclear (strftime)

    sql = """SELECT * FROM appointment_with_patient LIMIT 1"""
    appointment = read_rows(sql)
    body = {
        "dob": appointment[0]['dob'].strftime("%Y%m%d"),
        "appointment_id": appointment[0]['id']
    }

    response = client.post(
        "/api/lookup_appointment",
        headers={"X-Token": "coneofsilence"},
        json=body
    )
    verify_response(response)

    # # incorrect appointment_id
    # body = {
    #     "dob": appointment[0]['dob'].strftime("%Y%m%d"),
    #     "appointment_id": -100
    # }
    #
    # response = client.post(
    #     "/api/lookup_appointment",
    #     headers={"X-Token": "coneofsilence"},
    #     json=body
    # )
    # verify_response(response)
