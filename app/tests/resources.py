import uuid

group = {
    "account": "TEST ACCOUNT",
    "group_code": str(uuid.uuid4()),
    "is_referral_code": 0,
    "consent_req": 0,
    "collect_insurance": 0,
    "insurance_req": 0,
    "allow_insurance_skip": 1,
    "upfront_payment_req": 0,
    "screen_seq": "is-patient,gender,race,ethnicity,symptoms,contact-tracing,public-places,"
                  "patient-details,patient-address,patient-contact,patient-vitals,pre-existing-conditions,"
                  "consent,date,location,time",
    "required_screens": "",
    "display_group_consent": 1,
    "consent_party_name": "APIs for APIs",
    "consent_url": "",
    "logo_1": "",
    "logo_2": "",
    "optional_screens": ""
}

location = {
    "name": str(uuid.uuid4()),
    "addr1": "123 any street",
    "addr2": "suit one",
    "addr3": "dd",
    "city": "ds",
    "st": "TX",
    "zip": "121",
    "time_zone": "CST",
    "test_type_offered": "oral",
    "status": "enabled",
    "type": "drive_thru",
    "billing_type": "insurance",
    "collect_insurance_info": False,
    "allow_insurance_skip": True,
    "collect_upfront_payment": False,
    "time_zone_offset": -240,
    "group_ids": [
    ],
    "service_ids": [
    ],
    "is_external": True
}

schedule_generation_rule = {
  "rule_type": "regular",
  "time_zone": "string",
  "time_zone_offset": "string",
  "status": "enabled",
  "location_id": 0,
  "slot_increment": 10,
  "slot_multiplier": 1,
  "local_start_time": "12:00:00",
  "local_end_time": "12:00:00",
  "active_local_start_dt": "2021-5-01 00:00:00",
  "active_local_end_dt": "2021-5-01 00:00:00",
  "sun": True,
  "mon": False,
  "tue": True,
  "wed": True,
  "thu": True,
  "fri": True,
  "sat": True,
  "category": "vax"
}

schedule_generation_rule_test = {
  "rule_type": "regular",
  "time_zone": "string",
  "time_zone_offset": "string",
  "status": "enabled",
  "location_id": 0,
  "slot_increment": 10,
  "slot_multiplier": 1,
  "local_start_time": "12:00:00",
  "local_end_time": "12:00:00",
  "active_local_start_dt": "2021-5-01 00:00:00",
  "active_local_end_dt": "2021-5-01 00:00:00",
  "sun": False,
  "mon": False,
  "tue": False,
  "wed": False,
  "thu": False,
  "fri": False,
  "sat": False,
  "category": "test"
}

token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlZaZFowZ19JTjNJa09SSmVKejlwYiJ9.eyJodHRwOi8vcm9sZXMuZ2d0L3JvbGVzIjpbImJpbGxpbmdfYWRtaW4iLCJjYXJlX3Byb3ZpZGVyIiwiQ2FyZSBQcm92aWRlciIsImNsaW5pY2FsX3Byb3ZpZGVyIiwiQ2xpbmljYWwgUHJvdmlkZXIiLCJDb250YWN0IENlbnRlciIsImN1c3RvbWVyX2NvbnRhY3QiLCJEZWZhdWx0Iiwib3JnX2FkbWluIiwiUG9ydGFsIFByb3ZpZGVyIiwic2l0ZV9hZG1pbiIsIlNpdGUgQWRtaW4iLCJzdXBlcl9hZG1pbiIsIlN1cGVyIEFkbWluIl0sImh0dHA6Ly9yb2xlcy5nZ3QvbWV0YSI6eyJvcmdhbml6YXRpb24iOjF9LCJpc3MiOiJodHRwczovL2dvZ2V0dGVzdGVkLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDUyMTY3MTQ0NDc1MDAwNjc4MGQwMTYiLCJhdWQiOlsiaHR0cHM6Ly9yb2xlLWJhc2UtYXV0aC50ZXN0L2FwaSIsImh0dHBzOi8vZ29nZXR0ZXN0ZWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxNjU0NzI2NCwiZXhwIjoxNjE5MTM5MjY0LCJhenAiOiIwZ3gxc1c1NzNqRVhmSnMzN094RU5zN25udkZ2aHFMWCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJhZGRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlIiwiYXBpIiwiYXJjaGl2ZV9wcm9jZXNzZWRfbm90aWZpY2F0aW9ucyIsImFzc2lnbl9ncm91cCIsImFzc2lnbl9zZXJ2aWNlIiwiY2FsbF9wYXRpZW50IiwiY3JlYXRlX2dyb3VwIiwiY3JlYXRlX2luc3VyYW5jZV9yZWNvcmQiLCJjcmVhdGVfbG9jYXRpb24iLCJkZWxldGVfaW5zdXJhbmNlX3JlY29yZCIsImRlbGV0ZV9zY2hlZHVsZSIsImRlbGV0ZV9zY2hlZHVsZV9nZW5lcmF0aW9uX3J1bGUiLCJlZGl0X3NjaGVkdWxlX2dlbmVyYXRpb25fcnVsZSIsImdlbmVyYWxfc2VhcmNoIiwiZ2VuZXJhdGVfYWxsX3NjaGVkdWxlcyIsImdlbmVyYXRlX3NjaGVkdWxlIiwiZ2V0X2FsbF9ncm91cHMiLCJnZXRfYWxsX3NlcnZpY2VzIiwiZ2V0X2FsbF90ZXN0X3Jlc3VsdHMiLCJnZXRfYmlsbGluZ19saXN0IiwiZ2V0X2xvY2F0aW9ucyIsImdldF9wcm92aWRlcl9wcm9jZXNzaW5nX2xpc3QiLCJnZXRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlcyIsImdldF93b3Jrc3RhdGlvbnMiLCJsb2NhdGlvbl9zZWFyY2giLCJsb2NrX3Byb3ZpZGVyX3Rhc2siLCJsb29rdXBfYXBwb2ludG1lbnQiLCJtaXNjX3Byb2Nlc3NvciIsIm5vdGlmeV9wYXRpZW50cyIsIm91dGJvdW5kX3Jlc3VsdCIsIm91dGJvdW5kX3Jlc3VsdF9zdGF0dXMiLCJwYXRpZW50X2xvb2t1cCIsInBvcHVsYXRlX2xvY2F0aW9uX3RodW1ibmFpbHMiLCJwcmludGVyX2dldF9uZXh0X2xhYmVsIiwicHJpbnRlcl9xdWV1ZV9jaGVjayIsInByb2Nlc3NfZW1haWxfcXVldWUiLCJwcm9jZXNzX2luYm91bmRfbGFiX3JlcG9ydHMiLCJwcm9jZXNzX3Byb2Nlc3Nfb3V0Ym91bmRfbGFiX29yZGVycyIsInByb2Nlc3Nfc21zX3F1ZXVlIiwicHJvY2Vzc192b2ljZV9xdWV1ZSIsInByb3ZpZGVyX2NvbXBsZXRlX3Rhc2siLCJwcm92aWRlcl9yb2xsYmFja190b19wZW5kaW5nX3Rhc2siLCJyZW1vdmVfZ3JvdXBzIiwicmVtb3ZlX3NlcnZpY2UiLCJzY2FuX2xhYmVsIiwic2NoZWR1bGVfcmVzdWx0X25vdGlmaWNhdGlvbnNfYW5kX2ZvbGxvd3VwcyIsInNlbmRlbWFpbCIsInNlbmRzbXMiLCJzbXNfZW1haWxfbm90aWZ5IiwidXBkYXRlX2FwcG9pbnRtZW50IiwidXBkYXRlX2JpbGxpbmdfc3RhdHVzIiwidXBkYXRlX2NvbnN1bHRhdGlvbl9ub3RlIiwidXBkYXRlX2dyb3VwIiwidXBkYXRlX2luc3VyYW5jZV9yZWNvcmQiLCJ1cGRhdGVfbG9jYXRpb24iLCJ2YWxpZGF0ZV9pbnN1cmFuY2VfcmVjb3JkIiwidmlld19pbnN1cmFuY2VfY2FyZCIsInZpZXdfdGVzdF9yZXBvcnQiXX0.FqNuKb8_b0MGNeydzx6FUDtR4_mkUpoaQg3GHGEsXvgMc96MtVP9sVZfkZIkFWRonXJVZbbrhFbeB64X3NiSKveY-EwqaMfntGze5yiWDnyBJhafAKca64_-wyMhfd4TaRdikNTX9YuwRckE6F3fRl4P61aaWMAktLu3zgdPpC-4PH8Shc-q3uhjfzlsBL-SdDaRe0Q0EBcFk_5RRIK_nJvWBXLVeIpkTlAExLweEU0VbTsHmuFN8hCM6pp9-ou72S-JDpRI7273IZJYI2F0lI3tz2nuX7Nz70fIrvm0NGBDThVbqPInPu9IhbgJZMUo2CP5KRYuaAiJ9d2T8zOVMQ"