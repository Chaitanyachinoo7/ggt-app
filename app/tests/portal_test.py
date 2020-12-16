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
from tests.resources import group, location

client = TestClient(app)


# def test_create_group():
#     response = client.post(
#         "/api/portal/site-admin/create_group",
#         headers={"X-Token": "coneofsilence"},
#         json=group
#     )
#
#     r = response.json()
#     assert response.status_code == 200
#     assert r['status'] == 'success'


def test_create_location():
    response = client.post(
        "/api/portal/site-admin/create_location",
        headers={"X-Token": "coneofsilence"},
        json=location
    )

    r = response.json()
    assert response.status_code == 200
    assert r['status'] == 'success'


# @pytest.mark.asyncio
# async def test_group_update():
#     group_code = group['group_code']
#     id = await get_group_id_by_code(group_code)
#     _update = group
#     _update['id'] = id
#     _update['account'] = "TEST ACCOUNT 2"
#     response = client.post(
#         "/api/portal/site-admin/update_group",
#         headers={"X-Token": "coneofsilence"},
#         json=_update
#     )
#
#     r = response.json()
#     print(r)
#     assert response.status_code == 200
#     assert r['status'] == 'success'
#     await delete_group_by_code(group_code)


async def get_group_id_by_code(code):
    sql = """SELECT * FROM groups WHERE group_code = %s"""
    vals = (code,)
    _group = await read_rows(sql, vals)
    return _group[0]['id']


async def delete_group_by_code(code):
    sql = """DELETE FROM groups WHERE group_code = %s"""
    vals = (code,)
    return await exec_delete(sql, vals)


