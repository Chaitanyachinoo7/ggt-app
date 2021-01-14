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
from tests.resources import token
from ggt.lib.db import read_rows

client = TestClient(app)

'''Clinical Provider Workflow'''


def verify_response(response, expected_status_code=200, expected_status='success'):
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_get_workstations():
    response = client.get(
        "/api/provider/get_workstations",
        headers={"X-Token": "coneofsilence", "Authorization": token}
    )
    verify_response(response)

def test_lookup_appointment():
    response = client.post(
        "/api/provider/lookup_appointment",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={"appointment_id": 1}
    )
    verify_response(response)

def test_update_appointment():
    response = client.post(
        "/api/provider/update_appointment",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "appointment_id": 1,
            "action": "check_in",
            "workstation_id": 1
        }
    )
    verify_response(response)

def test_scan_label():
    response = client.post(
        "/api/provider/scan_label",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "appointment_id": 1
        }
    )
    verify_response(response)
