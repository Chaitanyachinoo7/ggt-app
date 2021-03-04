import json

import requests
from requests import Response

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    exec_batch_execute,
    replica_read_row,
    replica_read_rows
)
from datetime import datetime, date

# TODO: read the params from Config files
auth_file = {
    "client_id": "6ok7VWNkeOA6An5sN30Jl9gHoH4oUT8j",
    "client_secret": "Rwx8-mby99m5O-2aR14JKgoim0VV0FJuO6sefpDxXjKiQ18mys4JWf2oAO6_5Mha",
    "audience": "https://gogettested.us.auth0.com/api/v2/", "grant_type": "client_credentials"
}
auth_url = "https://gogettested.us.auth0.com/oauth/token"
user_url = "https://gogettested.us.auth0.com/api/v2/users?page={}&per_page=100&include_totals=true"
roles_url = "https://gogettested.us.auth0.com/api/v2/users/{}/roles"
permissions_url = "https://gogettested.us.auth0.com/api/v2/users/{}/permissions"
delete_url = "https://gogettested.us.auth0.com/api/v2/users/{}"
update_user = "https://gogettested.us.auth0.com/api/v2/users/{}"


auth_response = requests.post(auth_url, data=auth_file)
auth = "Bearer {}".format(auth_response.json()['access_token'])
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}
existing_users: Response = requests.get(user_url.format(0), headers=headers)

total = existing_users.json()['total']
limit = 100
COUNT = 0
rounds = int(total/limit)


def add_organizations(users):
    users = users.json()['users']
    for user in users:
        if 'user_metadata' not in user.keys():
            add_organization_to_existing_user(user['user_id'], 1)


def add_organization_to_existing_user(user_id, org_id):
    body = {
        "user_metadata": {
            "organization": org_id
        }
    }
    body = json.dumps(body)
    r = requests.patch(update_user.format(user_id), data=body, headers=headers)
    _user = r.json()
    print("-------------------------------------------------------------------")
    print(_user)
    print("-------------------------------------------------------------------")
    return {'user': _user}


def delete_user(user_id, days):
    res = requests.delete(delete_url.format(user_id), headers=headers)
    print("{} - {} - {}".format(res.status_code, user_id, days))


def get_user_roles(user_id):
    user_roles = requests.get(roles_url.format(user_id), headers=headers)
    role_list = user_roles.json()
    role_list = list(map(lambda x: x['name'], role_list))
    return ','.join(role_list)


def get_user_permissions(user_id):
    user_roles = requests.get(permissions_url.format(user_id), headers=headers)
    permissions_list = user_roles.json()
    permissions_list = list(map(lambda x: x['permission_name'], permissions_list))
    return ','.join(permissions_list)


def update_ggt_users_roles_permissions(id, roles, permissions):
    sql = """UPDATE ggt_users
            SET
                roles = %s,
                permissions  = %s
            WHERE
                external_id = %s
"""
    exec_update(sql, (roles, permissions, id))


def get_all_users_in_db():
    sql = """SELECT external_id FROM ggt_users"""
    return replica_read_rows(sql)


def update_ggt_users(ggt_users, x):
    sql = """INSERT IGNORE INTO ggt_users
        (
            email,
            email_verified,
            family_name,
            given_name,
            name,
            picture,
            external_id,
            org_id,
            is_active
        )    
            VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
    # exec_batch_execute(sql, ggt_users) # Insert many throws errors with INSERT IGNORE

    ex_users = get_all_users_in_db()
    ext_ids = []
    for y in ex_users:
        ext_ids.append(y['external_id'])

    for idx, user in enumerate(ggt_users):
        if x == 0:
            COUNT = idx + 1
        else:
            COUNT = x*100 + idx + 1
        if user[6] not in ext_ids:
            print("{}. USER {} ADDED.".format(COUNT, user[0]))
            exec_insert(sql, user)
        else:
            print("PASS - {}".format(user[0]))


def task_populate_users(existing_users, x):
    print('\n\n********************task_populate_users****************************\n\n')
    users = existing_users.json()['users']
    filtered_users = list(map(lambda user: [
        user['email'],
        1 if user['email_verified'] else 0,
        user['family_name'] if 'family_name' in user.keys() else "",
        user['given_name'] if 'given_name' in user.keys() else "",
        user['name'] if 'name' in user.keys() else "",
        user['picture'] if 'picture' in user.keys() else "",
        user['user_id'],
        user['user_metadata']['organization'] if 'user_metadata' in user.keys() else 1,
        user['blocked'] if 'blocked' in user.keys() else 1
    ], users))
    update_ggt_users(filtered_users, x)

    # for u in users:
    #     id = str(u['user_id'])
    #     roles = get_user_roles(id)
    #     permissions = get_user_permissions(id)
    #     update_ggt_users_roles_permissions(id, roles, permissions)

    print('\n\n*******************************************************************\n\n')


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2[0:10], "%Y-%m-%d")
    return abs((d2 - d1).days)


def remove_user_after_30_inactive_days(users):
    for user in users.json()['users']:
        try:
            if user['user_id'] == 'google-oauth2|103990689398897563239':
                print('ss')
            if days_between(str(date.today()), user['last_login']) > 40:
                delete_user(user['user_id'], days_between(str(date.today()), user['last_login']))
        except KeyError:
            delete_user(user['user_id'], "never_logged_in")
            print(user)
            pass


for x in range(0, rounds):
    _existing_users: Response = requests.get(user_url.format(x), headers=headers)
    # task_populate_users(_existing_users, x)
    remove_user_after_30_inactive_days(_existing_users)
    # add_organizations(_existing_users)


def update_gps_coordinates(location_id, lat, lng):
    sql = """
        UPDATE 
            locations
        SET
            lat = %s,
            lng = %s,
            update_dt = NOW()
        WHERE 
            id = %s
    """
    vals = (lat, lng, location_id)
    exec_update(sql, vals)
