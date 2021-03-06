import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()

from ggt.lib.adapters.mysql_adapter import exec_batch_execute
import requests
import ujson

token_dev = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlZaZFowZ19JTjNJa09SSmVKejlwYiJ9.eyJodHRwOi8vcm9sZXMuZ2d0L3JvbGVzIjpbImJpbGxpbmdfYWRtaW4iLCJjYXJlX3Byb3ZpZGVyIiwiQ2FyZSBQcm92aWRlciIsImNsaW5pY2FsX3Byb3ZpZGVyIiwiQ2xpbmljYWwgUHJvdmlkZXIiLCJDb250YWN0IENlbnRlciIsImN1c3RvbWVyX2NvbnRhY3QiLCJEZWZhdWx0Iiwib3JnX2FkbWluIiwiUG9ydGFsIFByb3ZpZGVyIiwic2l0ZV9hZG1pbiIsIlNpdGUgQWRtaW4iLCJzdXBlcl9hZG1pbiIsIlN1cGVyIEFkbWluIl0sImh0dHA6Ly9yb2xlcy5nZ3QvbWV0YSI6eyJvcmdhbml6YXRpb24iOjF9LCJpc3MiOiJodHRwczovL2dvZ2V0dGVzdGVkLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDI1MWMzYWM3MjJhZjAwNjk3MmNjY2IiLCJhdWQiOlsiaHR0cHM6Ly9yb2xlLWJhc2UtYXV0aC50ZXN0L2FwaSIsImh0dHBzOi8vZ29nZXR0ZXN0ZWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxNDYzNTMyMSwiZXhwIjoxNjE3MjI3MzIxLCJhenAiOiIwZ3gxc1c1NzNqRVhmSnMzN094RU5zN25udkZ2aHFMWCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJhZGRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlIiwiYXBpIiwiYXJjaGl2ZV9wcm9jZXNzZWRfbm90aWZpY2F0aW9ucyIsImFzc2lnbl9ncm91cCIsImFzc2lnbl9zZXJ2aWNlIiwiY2FsbF9wYXRpZW50IiwiY3JlYXRlX2dyb3VwIiwiY3JlYXRlX2luc3VyYW5jZV9yZWNvcmQiLCJjcmVhdGVfbG9jYXRpb24iLCJkZWxldGVfaW5zdXJhbmNlX3JlY29yZCIsImRlbGV0ZV9zY2hlZHVsZSIsImRlbGV0ZV9zY2hlZHVsZV9nZW5lcmF0aW9uX3J1bGUiLCJlZGl0X3NjaGVkdWxlX2dlbmVyYXRpb25fcnVsZSIsImdlbmVyYWxfc2VhcmNoIiwiZ2VuZXJhdGVfYWxsX3NjaGVkdWxlcyIsImdlbmVyYXRlX3NjaGVkdWxlIiwiZ2V0X2FsbF9ncm91cHMiLCJnZXRfYWxsX3NlcnZpY2VzIiwiZ2V0X2FsbF90ZXN0X3Jlc3VsdHMiLCJnZXRfYmlsbGluZ19saXN0IiwiZ2V0X2xvY2F0aW9ucyIsImdldF9wcm92aWRlcl9wcm9jZXNzaW5nX2xpc3QiLCJnZXRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlcyIsImdldF93b3Jrc3RhdGlvbnMiLCJsb2NhdGlvbl9zZWFyY2giLCJsb2NrX3Byb3ZpZGVyX3Rhc2siLCJsb29rdXBfYXBwb2ludG1lbnQiLCJtaXNjX3Byb2Nlc3NvciIsIm5vdGlmeV9wYXRpZW50cyIsIm91dGJvdW5kX3Jlc3VsdCIsIm91dGJvdW5kX3Jlc3VsdF9zdGF0dXMiLCJwYXRpZW50X2xvb2t1cCIsInBvcHVsYXRlX2xvY2F0aW9uX3RodW1ibmFpbHMiLCJwcm9jZXNzX2VtYWlsX3F1ZXVlIiwicHJvY2Vzc19pbmJvdW5kX2xhYl9yZXBvcnRzIiwicHJvY2Vzc19wcm9jZXNzX291dGJvdW5kX2xhYl9vcmRlcnMiLCJwcm9jZXNzX3Ntc19xdWV1ZSIsInByb2Nlc3Nfdm9pY2VfcXVldWUiLCJwcm92aWRlcl9jb21wbGV0ZV90YXNrIiwicHJvdmlkZXJfcm9sbGJhY2tfdG9fcGVuZGluZ190YXNrIiwicmVtb3ZlX2dyb3VwcyIsInJlbW92ZV9zZXJ2aWNlIiwic2Nhbl9sYWJlbCIsInNjaGVkdWxlX3Jlc3VsdF9ub3RpZmljYXRpb25zX2FuZF9mb2xsb3d1cHMiLCJzZW5kZW1haWwiLCJzZW5kc21zIiwic21zX2VtYWlsX25vdGlmeSIsInVwZGF0ZV9hcHBvaW50bWVudCIsInVwZGF0ZV9iaWxsaW5nX3N0YXR1cyIsInVwZGF0ZV9jb25zdWx0YXRpb25fbm90ZSIsInVwZGF0ZV9ncm91cCIsInVwZGF0ZV9pbnN1cmFuY2VfcmVjb3JkIiwidXBkYXRlX2xvY2F0aW9uIiwidmFsaWRhdGVfaW5zdXJhbmNlX3JlY29yZCIsInZpZXdfaW5zdXJhbmNlX2NhcmQiLCJ2aWV3X3Rlc3RfcmVwb3J0Il19.juflEb18qxamZD3yCgwE9CgUROPe2ytxrREgxxECM0yY94qwvWLaELdMTq7GFBsvo6qKESsjTcoy9p-dc6sS26hmLSqD4HL4LWgs_pETMn3Py4OFp3zeXtuUTW2Ovy6px6QhxgA4d_niMMJ1u4C3cPmnI_Z1jS6ak2-7TKqMEb4PhECeaut_DbfOVMZV2OFNAgjnIV2jJXEu2nDsCs9luNXjzisU5NQCc4AOm1RTIyp6K5biDZtd7Crwr5SzIdiIYmU-rCSBq0IKtusXu5HboSA3Zg9Zfgaifd9a4X6YluwMWglaNNqgBsVbWKm8YB9KZHibP8VQLVWEQD_QltLXPw"
token_prod = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlZaZFowZ19JTjNJa09SSmVKejlwYiJ9.eyJodHRwOi8vcm9sZXMuZ2d0L3JvbGVzIjpbImJpbGxpbmdfYWRtaW4iLCJjYXJlX3Byb3ZpZGVyIiwiQ2FyZSBQcm92aWRlciIsImNsaW5pY2FsX3Byb3ZpZGVyIiwiQ2xpbmljYWwgUHJvdmlkZXIiLCJDb250YWN0IENlbnRlciIsImN1c3RvbWVyX2NvbnRhY3QiLCJEZWZhdWx0Iiwib3JnX2FkbWluIiwiUG9ydGFsIFByb3ZpZGVyIiwic2l0ZV9hZG1pbiIsIlNpdGUgQWRtaW4iLCJzdXBlcl9hZG1pbiIsIlN1cGVyIEFkbWluIl0sImh0dHA6Ly9yb2xlcy5nZ3QvbWV0YSI6eyJvcmdhbml6YXRpb24iOjR9LCJpc3MiOiJodHRwczovL2dvZ2V0dGVzdGVkLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDI1MWMzYWM3MjJhZjAwNjk3MmNjY2IiLCJhdWQiOlsiaHR0cHM6Ly9wZmUtYXBpLmdvZ2V0dGVzdGVkLmNvbS9hcGkiLCJodHRwczovL2dvZ2V0dGVzdGVkLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTUwMjgyMzAsImV4cCI6MTYxNTExNDYzMCwiYXpwIjoiME9aZjRZMEczWWNGODNoUjJXMElTeGZlaGpSZDZsUEIiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiYWRkX3NjaGVkdWxlX2dlbmVyYXRpb25fcnVsZSIsImFwaSIsImFyY2hpdmVfcHJvY2Vzc2VkX25vdGlmaWNhdGlvbnMiLCJhc3NpZ25fZ3JvdXAiLCJhc3NpZ25fc2VydmljZSIsImNhbGxfcGF0aWVudCIsImNyZWF0ZV9ncm91cCIsImNyZWF0ZV9pbnN1cmFuY2VfcmVjb3JkIiwiY3JlYXRlX2xvY2F0aW9uIiwiZGVsZXRlX2luc3VyYW5jZV9yZWNvcmQiLCJkZWxldGVfc2NoZWR1bGUiLCJkZWxldGVfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlIiwiZWRpdF9zY2hlZHVsZV9nZW5lcmF0aW9uX3J1bGUiLCJnZW5lcmFsX3NlYXJjaCIsImdlbmVyYXRlX2FsbF9zY2hlZHVsZXMiLCJnZW5lcmF0ZV9zY2hlZHVsZSIsImdldF9hbGxfZ3JvdXBzIiwiZ2V0X2FsbF9zZXJ2aWNlcyIsImdldF9hbGxfdGVzdF9yZXN1bHRzIiwiZ2V0X2JpbGxpbmdfbGlzdCIsImdldF9sb2NhdGlvbnMiLCJnZXRfcHJvdmlkZXJfcHJvY2Vzc2luZ19saXN0IiwiZ2V0X3NjaGVkdWxlX2dlbmVyYXRpb25fcnVsZXMiLCJnZXRfd29ya3N0YXRpb25zIiwibG9jYXRpb25fc2VhcmNoIiwibG9ja19wcm92aWRlcl90YXNrIiwibG9va3VwX2FwcG9pbnRtZW50IiwibWlzY19wcm9jZXNzb3IiLCJub3RpZnlfcGF0aWVudHMiLCJvdXRib3VuZF9yZXN1bHQiLCJvdXRib3VuZF9yZXN1bHRfc3RhdHVzIiwicGF0aWVudF9sb29rdXAiLCJwb3B1bGF0ZV9sb2NhdGlvbl90aHVtYm5haWxzIiwicHJvY2Vzc19lbWFpbF9xdWV1ZSIsInByb2Nlc3NfaW5ib3VuZF9sYWJfcmVwb3J0cyIsInByb2Nlc3NfcHJvY2Vzc19vdXRib3VuZF9sYWJfb3JkZXJzIiwicHJvY2Vzc19zbXNfcXVldWUiLCJwcm9jZXNzX3ZvaWNlX3F1ZXVlIiwicHJvdmlkZXJfY29tcGxldGVfdGFzayIsInByb3ZpZGVyX3JvbGxiYWNrX3RvX3BlbmRpbmdfdGFzayIsInJlbW92ZV9ncm91cHMiLCJyZW1vdmVfc2VydmljZSIsInNjYW5fbGFiZWwiLCJzY2hlZHVsZV9yZXN1bHRfbm90aWZpY2F0aW9uc19hbmRfZm9sbG93dXBzIiwic2VuZGVtYWlsIiwic2VuZHNtcyIsInNtc19lbWFpbF9ub3RpZnkiLCJ1cGRhdGVfYXBwb2ludG1lbnQiLCJ1cGRhdGVfYmlsbGluZ19zdGF0dXMiLCJ1cGRhdGVfY29uc3VsdGF0aW9uX25vdGUiLCJ1cGRhdGVfZ3JvdXAiLCJ1cGRhdGVfaW5zdXJhbmNlX3JlY29yZCIsInVwZGF0ZV9sb2NhdGlvbiIsInZhbGlkYXRlX2luc3VyYW5jZV9yZWNvcmQiLCJ2aWV3X2luc3VyYW5jZV9jYXJkIiwidmlld190ZXN0X3JlcG9ydCJdfQ.Lc4x6boicsc4qmeHQdVlCb6hWf_ZHdCED1yQt9IXTfCVZcVecsL6Tl7UPFDGZVJSj1NuGrj57ZuQSf1qi2gSMeB9jUMhl1DBeq4lvfuxQvjvU3cAz43qegOwiemR4kIhieK8aYDCJ7AnAGGcL5D6kdnlYTbPCBffLwXq75m66eDozkSO8JUEoiK3skHCoOEe3WITU10riFyNceYTqw71I7QIWkdoU6fr9fXrPMn8sIBgN057EsMjmxwjZRI8-KtPA2BatZr_IQYDLlDe0yPP3gcuYptHCUDF01NBMNnS4NyZyhJempsw9ZdiXz6Mm5aZiEdk5_itcyp3NCmoRY_-9g"
host_dev = "https://pfe-api-dev.gogettested.com/{}"
host_prod = "https://ggt-portal-api.gogettested.com/{}"
host_local = "http://0.0.0.0:8888/{}"

HOST = host_local
TOKEN = token_prod

auth = "Bearer {}".format(TOKEN)

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': auth}


def __get_names_by_email(email):
    temp = email.split('@')[0]
    first_name = ""
    last_name = ""

    names = temp.split('.')
    if len(names) > 0:
        last_name = names[0]
    if len(names) > 1:
        first_name = names[1]

    if first_name == "":
        first_name = last_name
    if last_name == "":
        last_name = first_name

    return first_name, last_name


def create_users():
    with open('data/new_users') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            email = row[0]
            first_name, last_name = __get_names_by_email(email)
            data = {
                "name": "{} {}".format(first_name, last_name),
                "blocked": False,
                "email_verified": True,
                "given_name": first_name,
                "family_name": last_name,
                "email": email,
                "nickname": first_name,
                "role": [
                    "site_admin",
                    "care_provider",
                    "clinical_provider",
                    "billing_admin",
                    "customer_contact"
                ]
            }
            user = ujson.dumps(data)
            print(user)
            res = requests.post(HOST.format('api/management/create_user'), data=user, headers=headers)
            print(res.json())


create_users()

