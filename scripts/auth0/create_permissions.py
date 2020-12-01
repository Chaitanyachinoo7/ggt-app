import requests
import ujson
import sys

auth_url = "https://gogettested.us.auth0.com/oauth/token"
production_api_id = "5f73824e68a7bf00460564ce"
development_api_id = "5f83b1c0dd8213003e8ea4ad"
create_permission_url = "https://gogettested.us.auth0.com/api/v2/resource-servers/{}"

print("\n\n########################### STARTED ADDING PERMISSIONS #####################################\n")

with open("get_auth.json") as f:
    auth_file = json.load(f)

auth_response = requests.post(auth_url, data=auth_file['body'])
auth = "Bearer {}".format(auth_response.json()['access_token'])
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}

with open("permissions.json") as f:
    payload = json.load(f)

permissions = payload['permissions']

dev_url = create_permission_url.format(development_api_id)
prod_url = create_permission_url.format(production_api_id)

environments = (dev_url, prod_url)

body = {'scopes': permissions}
body = json.dumps(body)


for idx, url in enumerate(environments):
    current_status = requests.get(url, headers=headers)
    current_status = current_status.json()
    current_permissions = list(map(lambda s: s['value'], current_status['scopes']))
    new_permissions = list(map(lambda s: s['value'], permissions))
    deleting_list = list(set(current_permissions) - set(new_permissions))
    new_list = list(set(new_permissions) - set(current_permissions))
    env = 'dev' if idx == 0 else 'prod'
    if len(new_list) > 0:
        print('\n\n- Following permissions will be added to the {} API\n'.format(env))
        for idx, p in enumerate(new_list):
            print("{} -   {}  ".format(idx + 1, p))

    if len(deleting_list) > 0:
        print('\n\n- Following permissions will be removed from the {} API\n'.format(env))
        for idx, p in enumerate(deleting_list):
            print("{} -   {}  ".format(idx + 1, p))

    if len(deleting_list) > 0 or len(new_list) > 0:
        temp = input('\nPlease press "Y" to continue "N" to abort : ')
    else:
        temp = "y"
        print('No permission change be in the {} API'.format(env))

    if temp.lower() == "y":
        r = requests.patch(url, data=body, headers=headers)
        # print(r.json())
    else:
        print('Process aborted by user.')
        pass

print("\n\n########################### END OF ADDING PERMISSIONS ######################################\n")
