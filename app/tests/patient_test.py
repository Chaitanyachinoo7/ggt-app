import os
import sys
import time

import nest_asyncio
import pytest

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


def test_get_available_dates():
    response = client.get(
        "/api/get_available_dates/_DEFAULT_",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_screen_flow_seq():
    response = client.get(
        "/api/get_screen_flow_seq/_DEFAULT_",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_available_locations():
    date = time.strftime('%Y-%m-%d')
    response = client.get(
        "/api/get_available_locations/_DEFAULT_/{}".format(date),
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations():
    response = client.get(
        "/api/get_locations",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations_2():
    response = client.get(
        "/api/get_locations/_DEFAULT_",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations_near_me_1():
    response = client.get(
        "/api/get_locations_near_me/32.779167/-96.808891",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations_near_me_2():
    response = client.get(
        "/api/get_locations_near_me/32.779167/-96.808891/50",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations_near_me_3():
    response = client.get(
        "/api/get_locations_near_me/_DEFAULT_/32.779167/-96.808891/50",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_locations_near_me_4():
    date = time.strftime('%Y%m%d')
    response = client.get(
        "/api/get_locations_near_me/_DEFAULT_/{}/32.779167/-96.808891/50".format(date),
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_get_available_times_1():
    date = time.strftime('%Y%m%d')
    response = client.get(
        "/api/get_available_times/7/{}".format(date),
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


def test_get_get_available_times_2():
    response = client.get(
        "/api/get_available_times/7",
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


@pytest.mark.asyncio
async def test_get_appointment_results():
    sql = """SELECT * FROM detailed_test_results
                ORDER by test_id DESC
                LIMIT 1"""
    patient = read_rows(sql)
    token = patient[0]['token']
    dob = patient[0]['dob'].strftime("%Y%m%d")
    response = client.get(
        "/api/appointment/result/{}/{}".format(token, dob),
        headers={"X-Token": "coneofsilence"}
    )
    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'

