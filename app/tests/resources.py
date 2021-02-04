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
  "active_local_start_dt": "2020-01-01 00:00:00",
  "active_local_end_dt": "2020-01-01 00:00:00",
  "sun": False,
  "mon": False,
  "tue": False,
  "wed": False,
  "thu": False,
  "fri": False,
  "sat": False,
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
  "active_local_start_dt": "2020-01-01 00:00:00",
  "active_local_end_dt": "2020-01-01 00:00:00",
  "sun": False,
  "mon": False,
  "tue": False,
  "wed": False,
  "thu": False,
  "fri": False,
  "sat": False,
  "category": "test"
}

token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlZaZFowZ19JTjNJa09SSmVKejlwYiJ9.eyJodHRwOi8vcm9sZXMuZ2d0L3JvbGVzIjpbImJpbGxpbmdfYWRtaW4iLCJjYXJlX3Byb3ZpZGVyIiwiQ2FyZSBQcm92aWRlciIsImNsaW5pY2FsX3Byb3ZpZGVyIiwiQ2xpbmljYWwgUHJvdmlkZXIiLCJDb250YWN0IENlbnRlciIsImN1c3RvbWVyX2NvbnRhY3QiLCJEZWZhdWx0Iiwib3JnX2FkbWluIiwiUG9ydGFsIFByb3ZpZGVyIiwic2l0ZV9hZG1pbiIsIlNpdGUgQWRtaW4iLCJzdXBlcl9hZG1pbiIsIlN1cGVyIEFkbWluIl0sImh0dHA6Ly9yb2xlcy5nZ3QvbWV0YSI6eyJvcmdhbml6YXRpb24iOjF9LCJpc3MiOiJodHRwczovL2dvZ2V0dGVzdGVkLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1Zjk4YjJiZWRlNmZhNzAwNzUyYjYyOGYiLCJhdWQiOlsiaHR0cHM6Ly9yb2xlLWJhc2UtYXV0aC50ZXN0L2FwaSIsImh0dHBzOi8vZ29nZXR0ZXN0ZWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxMDM3MTMxNSwiZXhwIjoxNjEyOTYzMzE1LCJhenAiOiIwZ3gxc1c1NzNqRVhmSnMzN094RU5zN25udkZ2aHFMWCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJhZGRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlIiwiYXBpIiwiYXJjaGl2ZV9wcm9jZXNzZWRfbm90aWZpY2F0aW9ucyIsImFzc2lnbl9ncm91cCIsImFzc2lnbl9zZXJ2aWNlIiwiY2FsbF9wYXRpZW50IiwiY3JlYXRlX2dyb3VwIiwiY3JlYXRlX2luc3VyYW5jZV9yZWNvcmQiLCJjcmVhdGVfbG9jYXRpb24iLCJkZWxldGVfaW5zdXJhbmNlX3JlY29yZCIsImRlbGV0ZV9zY2hlZHVsZSIsImRlbGV0ZV9zY2hlZHVsZV9nZW5lcmF0aW9uX3J1bGUiLCJlZGl0X3NjaGVkdWxlX2dlbmVyYXRpb25fcnVsZSIsImdlbmVyYWxfc2VhcmNoIiwiZ2VuZXJhdGVfYWxsX3NjaGVkdWxlcyIsImdlbmVyYXRlX3NjaGVkdWxlIiwiZ2V0X2FsbF9ncm91cHMiLCJnZXRfYWxsX3NlcnZpY2VzIiwiZ2V0X2FsbF90ZXN0X3Jlc3VsdHMiLCJnZXRfYmlsbGluZ19saXN0IiwiZ2V0X2xvY2F0aW9ucyIsImdldF9wcm92aWRlcl9wcm9jZXNzaW5nX2xpc3QiLCJnZXRfc2NoZWR1bGVfZ2VuZXJhdGlvbl9ydWxlcyIsImdldF93b3Jrc3RhdGlvbnMiLCJsb2NhdGlvbl9zZWFyY2giLCJsb2NrX3Byb3ZpZGVyX3Rhc2siLCJsb29rdXBfYXBwb2ludG1lbnQiLCJtaXNjX3Byb2Nlc3NvciIsIm5vdGlmeV9wYXRpZW50cyIsIm91dGJvdW5kX3Jlc3VsdCIsIm91dGJvdW5kX3Jlc3VsdF9zdGF0dXMiLCJwYXRpZW50X2xvb2t1cCIsInBvcHVsYXRlX2xvY2F0aW9uX3RodW1ibmFpbHMiLCJwcm9jZXNzX2VtYWlsX3F1ZXVlIiwicHJvY2Vzc19pbmJvdW5kX2xhYl9yZXBvcnRzIiwicHJvY2Vzc19wcm9jZXNzX291dGJvdW5kX2xhYl9vcmRlcnMiLCJwcm9jZXNzX3Ntc19xdWV1ZSIsInByb2Nlc3Nfdm9pY2VfcXVldWUiLCJwcm92aWRlcl9jb21wbGV0ZV90YXNrIiwicHJvdmlkZXJfcm9sbGJhY2tfdG9fcGVuZGluZ190YXNrIiwicmVtb3ZlX2dyb3VwcyIsInJlbW92ZV9zZXJ2aWNlIiwic2Nhbl9sYWJlbCIsInNjaGVkdWxlX3Jlc3VsdF9ub3RpZmljYXRpb25zX2FuZF9mb2xsb3d1cHMiLCJzZW5kZW1haWwiLCJzZW5kc21zIiwic21zX2VtYWlsX25vdGlmeSIsInVwZGF0ZV9hcHBvaW50bWVudCIsInVwZGF0ZV9iaWxsaW5nX3N0YXR1cyIsInVwZGF0ZV9jb25zdWx0YXRpb25fbm90ZSIsInVwZGF0ZV9ncm91cCIsInVwZGF0ZV9pbnN1cmFuY2VfcmVjb3JkIiwidXBkYXRlX2xvY2F0aW9uIiwidmFsaWRhdGVfaW5zdXJhbmNlX3JlY29yZCIsInZpZXdfaW5zdXJhbmNlX2NhcmQiLCJ2aWV3X3Rlc3RfcmVwb3J0Il19.RW7oUdA4_14OWJMBpudfV20O-lAlFA7uzrNYZvZ-kCAY7D3Tf__RJzmwXDddpMWEESU6TRqXwj0QNtZlHG_A683zHOFKQ9S2Y0Uay2bUS_TVFLje54mab2wigt9VrznunzYSgdWZSq6OfcsDvA0m6-G_Wu3NjJ39-jWSgO0u3pMAy3jLuQRMNJD3xflgO5r9qsj-KIRvOtXeJ_7sOktEo3xMe2QIrt78ynLzXDMHnshVlD6SPSDvX3tK54iSfA4-acL6Qvcdn586YeNRzJf_B_RXwvHaVJR4fApM39FqlhJUlC6cCyGt4pbipjANszB1ndAseUWBgGqH9ltupCTASw"
