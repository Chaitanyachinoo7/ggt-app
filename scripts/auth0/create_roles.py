import requests
import json

print("\n\n########################### STARTED CREATING ROLES #########################################\n")

role_url = 'https://gogettested.us.auth0.com/api/v2/roles'
auth_url = "https://gogettested.us.auth0.com/oauth/token"

with open("get_auth.json") as f:
	auth_file = json.load(f)

auth_response = requests.post(auth_url, data=auth_file['body'])
auth = "Bearer {}".format(auth_response.json()['access_token']) 

with open("roles.json") as f:
	payload = json.load(f)

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}
roles = payload['roles']
existing_roles = requests.get(role_url, headers=headers)
existing_roles = existing_roles.json()
existing_role_names = list(map(lambda role: role['name'], existing_roles))

for role in roles:
	if role['name'] not in existing_role_names:
		role = json.dumps(role)
		r = requests.post(role_url, data=role, headers=headers)
		print("Role - {} created".format(role))
	else:
		print("Role - {} is already exists.".format(role))

new_roles = requests.get(role_url, headers=headers)
new_roles = new_roles.json()

role_id_map = {}
for role in new_roles:
	role_id_map[role['name']] = role['id']
	
with open('role_id_map.json', 'w') as outfile:
    json.dump(role_id_map, outfile)

print("\n\n########################### FINISHED CREATING ROLES ########################################\n\n")