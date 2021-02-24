import os
import sys

import nest_asyncio

nest_asyncio.apply()
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from fastapi.testclient import TestClient
from main import app
from tests.resources import token

client = TestClient(app)

'''Clinical Provider Workflow'''
import datetime

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
df_tomorrow = tomorrow + datetime.timedelta(days=1)

def verify_response(response, expected_status_code=200, expected_status='success'):
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_begin_and_end_consultation():
    response = client.post(
        "/api/care_provider/begin_consultation",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "test_id": 1,
            "user_id": 1,
            "appointment_id": 1
        }
    )
    verify_response(response)

    consultation_id = response.json()["results"]["consultation_id"]

    response = client.post(
        "/api/care_provider/end_consultation",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "consultation_id": consultation_id,
            "note": "string",
            "test_id": 1,
            "consultation_type_code": "pre_covid_consultation",
            "resolution_code": "neg_with_pmh"
        }
    )
    verify_response(response)


# def test_provider_rollback_to_pending_task():
#     response = client.post(
#         "/api/care_provider/provider_rollback_to_pending_task",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={"test_id": 1}
#     )
#     verify_response(response)


def test_get_provider_processing_list():
    response = client.post(
        "/api/care_provider/get_provider_processing_list",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "offset": 0,
            "positive_call": "any",
            "consultation_notes": "any",
            "consultation_status": "any",
            "start_date": str(today),
            "end_date": str(df_tomorrow)
        }
    )
    verify_response(response)
