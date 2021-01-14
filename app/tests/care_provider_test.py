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

### FAILING: data_models/providers.py line 324 needs to be pending.value
# def test_provider_rollback_to_pending_task():
#     response = client.post(
#         "/api/care_provider/provider_rollback_to_pending_task",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={"test_id": 1}
#     )
#     verify_response(response)



### FAILING: data_models/providers.py line 208 needs to be in_progress.value
# def test_begin_and_end_consultation():
#     response = client.post(
#         "/api/care_provider/begin_consultation",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={
#           "test_id": 1,
#           "user_id": 1,
#           "appointment_id": 1
#          }
#     )
#     verify_response(response)
#
#     consultation_id = response.json()["results"]["consultation_id"]
#
#     response = client.post(
#         "/api/care_provider/end_consultation",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={
#           "consultation_id": consultation_id,
#           "note": "string",
#           "test_id": 1,
#           "consultation_type_code": "pre_covid_consultation",
#           "resolution_code": "neg_with_pmh"
#         }
#     )
#     verify_response(response)
