import os
import sys
import uuid
import nest_asyncio

nest_asyncio.apply()
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from fastapi.testclient import TestClient
from main import app
from ggt.lib.db import read_rows
from tests.resources import token

client = TestClient(app)

'''Management APIs Workflow'''

def get_request_org_id_by_name(name):
    sql = """SELECT * FROM organization_requests WHERE org_name = %s"""
    vals = (name,)
    _orgs = read_rows(sql, vals)
    return _orgs[0]['id']

def get_user_external_id_by_name(name):
    sql = """SELECT * FROM ggt_users WHERE name = %s"""
    vals = (name,)
    _users = read_rows(sql, vals)
    return _users[0]['external_id']


def verify_response(response, expected_status_code=200, expected_status='success'):
    print(response.json())
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_list_organizations():
    response = client.post(
        "/api/management/list_organizations",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "name": "TEST"
        }
    )
    verify_response(response)

def test_change_org_status():
    response = client.post(
        "/api/management/change_org_status",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "id": 1,
            "is_active": False
        }
    )
    verify_response(response)

    # change it back

    response = client.post(
        "/api/management/change_org_status",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "id": 1,
            "is_active": True
        }
    )
    verify_response(response)

def test_create_new_org_request():
    response = client.post(
        "/api/management/create_new_organisation_request",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "org_name": "PYTEST_ORG",
            "email": "pytest-{0}@ggt.com".format(str(uuid.uuid4())),
            "given_name": "PYTEST",
            "family_name": "PYTEST",
            "name": "PYTEST_ORG",
            "nickname": "PYTEST_ORG"
        }
    )
    verify_response(response)

def test_list_org_requests():
    response = client.post(
        "/api/management/list_org_requests",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "status": "pending"
        }
    )
    verify_response(response)

# def test_process_org_request():
#     org_id = get_request_org_id_by_name("PYTEST_ORG")
#     print(org_id)
#     response = client.post(
#         "/api/management/process_org_request",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={
#             "id": org_id,
#             "status": "accepted",
#             "comment": "congrats"
#         }
#     )
#     verify_response(response)
#
#     # delete the user created with that org
#
#     ext_id = get_user_external_id_by_name("PYTEST_ORG")
#     response = client.post(
#         "/api/management/delete_user",
#         headers={"X-Token": "coneofsilence", "Authorization": token},
#         json={
#             "ext_user_id": ext_id
#         }
#     )
#     verify_response(response)

def test_create_user():
    response = client.post(
        "/api/management/create_user",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
              "organization_id": 1,
              "role": [
                "billing_admin"
              ],
              "email": "test_new_user-{0}@ggt.com".format(str(uuid.uuid4())),
              "given_name": "TEST",
              "family_name": "USER",
              "name": "TEST_USER",
              "nickname": "TU",
              "blocked": False,
              "email_verified": False
        }
    )
    verify_response(response)

def test_update_user():
    ext_id = get_user_external_id_by_name("TEST_USER")
    response = client.post(
        "/api/management/update_user",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
              "ext_id": ext_id,
              "email": "test_new_user_2@ggt.com",
              "given_name": "TEST",
              "family_name": "USER",
              "name": "TEST_USER",
              "nickname": "TU_NEW"
        }
    )
    verify_response(response)

def test_update_user_state():
    ext_id = get_user_external_id_by_name("TEST_USER")
    response = client.post(
        "/api/management/update_user_state",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
              "ext_id": ext_id,
              "is_active": False
        }
    )
    verify_response(response)

def test_update_user_role():
    ext_id = get_user_external_id_by_name("TEST_USER")
    response = client.post(
        "/api/management/update_user_role",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
              "ext_user_id": ext_id,
              "current_role": [
                "billing_admin"
              ],
              "new_role": [
                "care_provider"
              ]
        }
    )
    verify_response(response)

def test_list_users():
    response = client.post(
        "/api/management/list_users",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
              "role": "",
              "name": "TEST",
              "email": "",
              "offset": 0,
              "limit": 20
        }
    )
    verify_response(response)

def test_delete_user():
    ext_id = get_user_external_id_by_name("TEST_USER")
    response = client.post(
        "/api/management/delete_user",
        headers={"X-Token": "coneofsilence", "Authorization": token},
        json={
            "ext_user_id": ext_id
        }
    )
    verify_response(response)

# def test_get_user_profile():
#     response = client.get(
#         "/api/management/user_profile",
#         headers={"X-Token": "coneofsilence", "Authorization": token}
#     )
#     verify_response(response)

# def test_password_change_ticket():
#     response = client.get(
#         "/api/management/password_change_ticket",
#         headers={"X-Token": "coneofsilence", "Authorization": token}
#     )
#     verify_response(response)
