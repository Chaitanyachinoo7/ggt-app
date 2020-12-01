import requests
import ujson
import sys

role_url = "https://gogettested.us.auth0.com/api/v2/roles"
auth_url = "https://gogettested.us.auth0.com/oauth/token"
permission_role_url = "https://gogettested.us.auth0.com/api/v2/roles/{}/permissions"

production_api = "https://pfe-api.gogettested.com/api"
development_api = "https://role-base-auth.test/api"

print("\n\n########################### STARTED MAPPING PERMISSIONS TO ROLES ###########################\n")
with open("get_auth.json") as f:
    auth_file = json.load(f)

auth_response = requests.post(auth_url, data=auth_file['body'])
auth = "Bearer {}".format(auth_response.json()['access_token'])
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}

with open("permission_to_roles_map.json") as f:
    p_to_r_map = json.load(f)

with open("permissions.json") as f:
    p_dict = json.load(f)

with open("role_id_map.json") as f:
    r_id_map = json.load(f)

roles = p_to_r_map.keys()

permissions_list = p_dict['permissions']
available_permissions = list(map(lambda p: p['value'], permissions_list))

for role in roles:
    body = {}
    old_body = {}
    permissions = []
    new_names = []
    for permission in p_to_r_map[role]:
        if permission in available_permissions:
            permissions.append({
                "permission_name": permission,
                "resource_server_identifier": development_api
            })
            permissions.append({
                "permission_name": permission,
                "resource_server_identifier": production_api

            })
            new_names.append(permission)
    role_id = r_id_map[role]
    url = permission_role_url.format(role_id)
    current_permissions = requests.get(url, headers=headers).json()
    _current_permissions = []
    current_names = []
    for p in current_permissions:
        _current_permissions.append(
            {"permission_name": p['permission_name'], "resource_server_identifier": p['resource_server_identifier']})
        current_names.append(p['permission_name'])

    new_list = list(set(new_names) - set(current_names))
    deleting_list = list(set(current_names) - set(new_names))

    if len(new_list) > 0:
        print('\n\n- Following permissions will be added to the ROLE - {}\n'.format(role))
        for idx, p in enumerate(new_list):
            print("{} -   {}  ".format(idx + 1, p))

    if len(deleting_list) > 0:
        print('\n\n- Following permissions will be removed from ROLE - {}\n'.format(role))
        for idx, p in enumerate(deleting_list):
            print("{} -   {}  ".format(idx + 1, p))

    if len(new_list) > 0 or len(deleting_list) > 0:
        temp = input('\n\n- Please press "Y" to continue "N" to abort : ')
    else:
        temp = 'y'
        print('\n- No permission change in the ROLE - {}\n'.format(role))

    if temp.lower() == "y":
        body['permissions'] = permissions
        old_body['permissions'] = _current_permissions
        body = json.dumps(body)
        old_body = json.dumps(old_body)
        if len(current_permissions) > 0:
            r = requests.delete(url, data=old_body, headers=headers)
            print(old_body)
        r = requests.post(url, data=body, headers=headers)
        print(r.json())
    else:
        break;

print("\n\n########################### END OF MAPPING PERMISSIONS TO ROLES ############################\n")
print("\n\n\nPlease re-assign permissions to machine to machine APIs...")
