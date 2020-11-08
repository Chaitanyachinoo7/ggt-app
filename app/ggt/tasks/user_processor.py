import base64
import requests
import json
from requests import Response

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_rows,
    exec_batch_execute
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

# TODO: read the params from Config files
auth_file = {
    "client_id": "6ok7VWNkeOA6An5sN30Jl9gHoH4oUT8j",
    "client_secret": "Rwx8-mby99m5O-2aR14JKgoim0VV0FJuO6sefpDxXjKiQ18mys4JWf2oAO6_5Mha",
    "audience": "https://gogettested.us.auth0.com/api/v2/", "grant_type": "client_credentials"
}
auth_url = "https://gogettested.us.auth0.com/oauth/token"
user_url = "https://gogettested.us.auth0.com/api/v2/users"
roles_url = "https://gogettested.us.auth0.com/api/v2/users/{}/roles"
permissions_url = "https://gogettested.us.auth0.com/api/v2/users/{}/permissions"

auth_response = requests.post(auth_url, data=auth_file)
auth = "Bearer {}".format(auth_response.json()['access_token'])
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}
existing_users: Response = requests.get(user_url, headers=headers)


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


def update_ggt_users(ggt_users):
    sql = """INSERT IGNORE INTO ggt_users
        (
            email,
            email_verified,
            family_name,
            given_name,
            name,
            picture,
            external_id
        )    
            VALUES
        (%s, %s, %s, %s, %s, %s, %s);
"""
    # exec_batch_execute(sql, ggt_users) # Insert many throws errors with INSERT IGNORE
    for user in ggt_users:
        exec_insert(sql, user)


def task_populate_users(existing_users):
    print('\n\n********************task_populate_users****************************\n\n')
    users = existing_users.json()
    filtered_users = list(map(lambda user: [
        user['email'],
        1 if user['email_verified'] else 0,
        user['family_name'] if 'family_name' in user.keys() else "",
        user['given_name'] if 'given_name' in user.keys() else "",
        user['name'] if 'name' in user.keys() else "",
        user['picture'] if 'picture' in user.keys() else "",
        user['user_id']
    ], users))
    # update_ggt_users(filtered_users)

    for u in users:
        id = str(u['user_id'])
        roles = get_user_roles(id)
        permissions = get_user_permissions(id)
        update_ggt_users_roles_permissions(id, roles, permissions)

    print('\n\n*******************************************************************\n\n')


task_populate_users(existing_users)


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
