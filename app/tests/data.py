"""
Mock Data for tests
"""
import datetime

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
df_tomorrow = tomorrow + datetime.timedelta(days=1)

locations = [
    {
        "id": 1,
        "site_code": "TEST_SITE_CODE",
        "org_id": 1,
        "name": "TEST_LOCATION",
        "addr1": "123 Any Street",
        "addr2": None,
        "addr3": None,
        "city": "Any City",
        "st": "ST",
        "zip": "99999",
        "lat": 33.160919,
        "lng": -96.832382,
        "time_zone": "CST",
        "time_zone_offset": "-05:00",
        "test_type_offered": "oral",
        "status": "enabled",
        "type": "drive_thru",
        "billing_type": "insurance",
        "collect_insurance_info": 1,
        "allow_insurance_skip": 1,
        "collect_upfront_payment": 0,
        "image_thumbnail": "temp",
        "accepts_bookings": None,
        "accepts_walkins": None,
        "operator": None,
        "phone_number": None,
        "website": None,
        "open_hours": None,
        "misc": None,
        "is_external": 0,
        "lab_id": 1,
        "create_dt": "2020-07-21 14:40:53",
        "update_dt": "2020-10-02 11:12:41",
        "country": None
    }
]

groups = [
    {
        "id": 1,
        "account": "_DEFAULT_",
        "org_id": 1,
        "group_code": "_DEFAULT_",
        "is_referral_code": 0,
        "consent_req": 0,
        "collect_insurance": 0,
        "insurance_req": 0,
        "allow_insurance_skip": 1,
        "upfront_payment_req": 0,
        "screen_seq": "is-patient,gender,race,ethnicity,symptoms,contact-tracing,public-places,patient-details,patient-address,patient-contact,patient-vitals,pre-existing-conditions,consent,date,location,time,insurance-card",
        "required_screens": "insurance-card",
        "ggv_screen_seq": "",
        "ggv_required_screens": "",
        "display_group_consent": None,
        "consent_party_name": None,
        "intro_text": None,
        "consent_url": None,
        "logo_1": None,
        "logo_2": None,
        "optional_screens": None,
        "additional_fields": None,
        "create_dt": "2020-09-16 16:22:45",
        "update_dt": "2020-09-16 16:22:45"
    }
]

group_codes_to_locations_mapping = [
    {
        "id": 1,
        "group_id": 1,
        "location_id": 1
    }
]

schedules = [
    {
        "id": 1,
        "location_id": 1,
        "start_dt": "2020-12-10 08:00:00",
        "end_dt": "2020-12-10 08:10:00",
        "time_zone": "CST",
        "time_zone_offset": "-05:00",
        "duration": 600,
        "status": "available",
        "appointment_id": None,
        "lock_time": "2020-12-10 08:10:00",
        "rule_id": None
    },
    {
        "id": 2,
        "location_id": 1,
        "start_dt": "2025-12-15 08:00:00",
        "end_dt": "2025-12-15 08:10:00",
        "time_zone": "CST",
        "time_zone_offset": "-05:00",
        "duration": 600,
        "status": "available",
        "appointment_id": None,
        "lock_time": "2020-12-15 08:10:00",
        "rule_id": None
    }
]

patients = [
    {
        "id": 1,
        "first_name": "Roman",
        "middle_name": "",
        "last_name": "Dhimal",
        "gender": "male",
        "height_ft": "5”8",
        "height_in": None,
        "weight_lb": "120",
        "ethnicity": "false",
        "race": "race_asian",
        "addr1": "5816 Hickoryhill Rd",
        "addr2": None,
        "addr3": None,
        "city": "Watauga",
        "county": "Tarrant",
        "st": "TX",
        "zip": "76148",
        "dob": "2000-10-01",
        "phone_number": "+16822022920",
        "phone_number_verified": "1",
        "email": "dhimalroman@gmail.com",
        "email_verified": None,
        "token": "8aa37097-2762-431f-b78c-1e9e582c4a19",
        "result_token": None,
        "token_expire": "2021-06-30 16:55:05",
        "create_dt": "2020-06-30 16:55:05",
        "update_dt": "2020-06-30 16:55:05",
        "country": None
    }
]

appointments = [
    {
        "id": 1,
        "scheduled_dt": "2020-07-06 10:20:00",
        "check_in_dt": None,
        "pre_consultation_provider_id": None,
        "pre_consultation_notes": None,
        "pre_consultaiton_start_dt": None,
        "pre_consultation_end_dt": None,
        "location_id": 1,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "vial_id": None,
        "test_start_dt": None,
        "test_end_dt": None,
        "wp_receipt_token": None,
        "wp_customer_info_id": None,
        "total_cost": None,
        "billed_amount": None,
        "status": "scheduled",
        "billing_status": "pending",
        "vax_start_dt": "2020-07-06 16:40:09",
        "vax_notes_dt": "2020-07-06 16:40:09",
        "vax_end_dt": "2020-07-06 16:40:09",
        "injection_site": None,
        "no_adverse_reactions": 1,
        "lot_no": None,
        "expiration_date": None,
        "gtin": None,
        "sample_collection_location_id": 1,
        "language": None,
        "create_dt": "2020-07-06 16:40:09",
        "update_dt": "2020-07-06 16:40:09"
    },
    {
        "id": 2,
        "scheduled_dt": "2020-07-06 10:20:00",
        "check_in_dt": None,
        "pre_consultation_provider_id": None,
        "pre_consultation_notes": None,
        "pre_consultaiton_start_dt": None,
        "pre_consultation_end_dt": None,
        "location_id": 1,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "vial_id": None,
        "test_start_dt": None,
        "test_end_dt": None,
        "wp_receipt_token": None,
        "wp_customer_info_id": None,
        "total_cost": None,
        "billed_amount": None,
        "status": "scheduled",
        "billing_status": "pending",
        "vax_start_dt": "2020-07-06 16:40:09",
        "vax_notes_dt": "2020-07-06 16:40:09",
        "vax_end_dt": "2020-07-06 16:40:09",
        "injection_site": None,
        "no_adverse_reactions": 1,
        "lot_no": None,
        "expiration_date": None,
        "gtin": None,
        "sample_collection_location_id": 1,
        "language": None,
        "create_dt": "2020-07-06 16:40:09",
        "update_dt": "2020-07-06 16:40:09"
    },
    {
        "id": 3,
        "scheduled_dt": "2020-07-06 10:20:00",
        "check_in_dt": None,
        "pre_consultation_provider_id": None,
        "pre_consultation_notes": None,
        "pre_consultaiton_start_dt": None,
        "pre_consultation_end_dt": None,
        "location_id": 1,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "vial_id": None,
        "test_start_dt": None,
        "test_end_dt": None,
        "wp_receipt_token": None,
        "wp_customer_info_id": None,
        "total_cost": None,
        "billed_amount": None,
        "status": "scheduled",
        "billing_status": "pending",
        "vax_start_dt": "2020-07-06 16:40:09",
        "vax_notes_dt": "2020-07-06 16:40:09",
        "vax_end_dt": "2020-07-06 16:40:09",
        "injection_site": None,
        "no_adverse_reactions": 1,
        "lot_no": None,
        "expiration_date": None,
        "gtin": None,
        "sample_collection_location_id": 1,
        "language": None,
        "create_dt": "2020-07-06 16:40:09",
        "update_dt": "2020-07-06 16:40:09"
    }
]

test_samples = [
    {
        "id": 1,
        "appointment_id": 1,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "provider_id": None,
        "vial_id": "TEST",
        "sample_collection_location_id": 1,
        "sample_collection_start_dt": None,
        "sample_collection_end_dt": None,
        "pre_ship_label_scan_dt": "2020-12-14 19:58:05",
        "lab_id": 1,
        "lab_submission_batch_id": None,
        "lab_physical_submission_dt": None,
        "lab_electronic_submission_dt": None,
        "lab_result_receive_dt": None,
        "test_result": None,
        "notification_status": None,
        "notification_method": None,
        "notification_acknowledgement_dt": None,
        "consultation_status": "pending",
        "consultation_notes": None,
        "consultation_categorization": None,
        "location_id": None,
        "status": "ready_to_tx",
        "test_type": "oral",
        "initial_billed_status": 0,
        "post_test_billed_status": 0,
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 2,
        "appointment_id": 2,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "provider_id": None,
        "vial_id": "TEST",
        "sample_collection_location_id": 1,
        "sample_collection_start_dt": None,
        "sample_collection_end_dt": None,
        "pre_ship_label_scan_dt": "2020-12-14 19:58:05",
        "lab_id": 2,
        "lab_submission_batch_id": None,
        "lab_physical_submission_dt": None,
        "lab_electronic_submission_dt": None,
        "lab_result_receive_dt": None,
        "test_result": None,
        "notification_status": None,
        "notification_method": None,
        "notification_acknowledgement_dt": None,
        "consultation_status": "pending",
        "consultation_notes": None,
        "consultation_categorization": None,
        "location_id": None,
        "status": "ready_to_tx",
        "test_type": "oral",
        "initial_billed_status": 0,
        "post_test_billed_status": 0,
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 3,
        "appointment_id": 3,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "provider_id": None,
        "vial_id": "TEST",
        "sample_collection_location_id": 1,
        "sample_collection_start_dt": None,
        "sample_collection_end_dt": None,
        "pre_ship_label_scan_dt": "2020-12-14 19:58:05",
        "lab_id": 3,
        "lab_submission_batch_id": None,
        "lab_physical_submission_dt": None,
        "lab_electronic_submission_dt": None,
        "lab_result_receive_dt": None,
        "test_result": None,
        "notification_status": None,
        "notification_method": None,
        "notification_acknowledgement_dt": None,
        "consultation_status": "pending",
        "consultation_notes": None,
        "consultation_categorization": None,
        "location_id": None,
        "status": "ready_to_tx",
        "test_type": "oral",
        "initial_billed_status": 0,
        "post_test_billed_status": 0,
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 4,
        "appointment_id": 4,
        "group_code": None,
        "patient_id": 1,
        "patient_questionnaire_id": 1,
        "provider_id": None,
        "vial_id": "TEST",
        "sample_collection_location_id": 1,
        "sample_collection_start_dt": None,
        "sample_collection_end_dt": None,
        "pre_ship_label_scan_dt": "2020-12-14 19:58:05",
        "lab_id": 4,
        "lab_submission_batch_id": None,
        "lab_physical_submission_dt": None,
        "lab_electronic_submission_dt": None,
        "lab_result_receive_dt": None,
        "test_result": None,
        "notification_status": None,
        "notification_method": None,
        "notification_acknowledgement_dt": None,
        "consultation_status": "pending",
        "consultation_notes": None,
        "consultation_categorization": None,
        "location_id": None,
        "status": "ready_to_tx",
        "test_type": "oral",
        "initial_billed_status": 0,
        "post_test_billed_status": 0,
        "create_dt": today,
        "update_dt": today
    }
]

states = [
    {
        "id": 1,
        "key": "AL",
        "state": "Alabama",
        "active": 1
    },
    {
        "id": 2,
        "key": "AK",
        "state": "Alaska",
        "active": 1
    }
]

services_catalog = [
    {
        "id": 1,
        "service_code": "COVID_19_TEST",
        "service_name": "Covid-19 Test",
        "price": 175.00,
        "selfpay_amount": 0.00,
        "copay_amount": 0.00,
        "insurance_amount": 0.00,
        "currency": None
    },
    {
        "id": 2,
        "service_code": "FLU_SHOT",
        "service_name": "Flu Shot",
        "price": 30.00,
        "selfpay_amount": 30.00,
        "copay_amount": 0.00,
        "insurance_amount": 0.00,
        "currency": None
    },
    {
        "id": 3,
        "service_code": "CONSULT",
        "service_name": "Consultation",
        "price": 0.00,
        "selfpay_amount": 0.00,
        "copay_amount": 0.00,
        "insurance_amount": 0.00,
        "currency": None
    }
]

services_to_locations_mapping = [
    {
        "id": 1,
        "location_id": 1,
        "service_id": 1
    },
    {
        "id": 2,
        "location_id": 1,
        "service_id": 2
    },

]

workstations = [
    {
        "id": 1,
        "label": "METOHH1",
        "description": None,
        "printer_info": None,
        "token": "f25ee64b-4d6d-4619-8c26-37a9e3ea0095",
        "create_dt": "2020-09-01 07:38:07",
        "update_dt": "2020-09-01 07:38:07"
    }
]

users = [
    {
        "id": 1,
        "name": "Raquel Manzaneres",
        "phone_number": "",
        "email": "raquel@wellhealth.studio",
        "role": "billing"
    }
]

appointment_services = [
    {
        "id": 1,
        "appointment_id": 1,
        "service_id": 1,
        "service_description": "Covid-19 Test",
        "price": 175.00,
        "selfpay_amount": 0.00,
        "copay_amount": 0.00,
        "insurance_amount": 0.00,
        "create_dt": "2020-10-06 11:01:13",
        "update_dt": "2020-10-06 11:01:13"
    }
]

organizations = [
    {
        "id": 1,
        "name": "TEST_ORG",
        "email": "test@gmail.com",
        "owner_ext_id": "1",
        "is_active": 1,
        "update_dt": today,
        "create_dt": today
    }
]

locations_metrics_cache = [
    {
        "location_id": 1,
        "next_appointment_available": tomorrow,
        "average_processing_time": 3,
        "wait_time": 2,
        "update_dt": today
    }
]

schedules_metrics_cache = [
    {
        "location_id": 1,
        "local_scheduled_date": tomorrow,
        "available_slots_count": 100,
        "booked_slots_count": 20,
        "blocked_slots_count": 2,
        "total_slots_count": 122,
        "open_time": today,
        "close_time": tomorrow,
        "first_available_slot": today,
        "last_available_slot": df_tomorrow,
        "update_dt": today,
        "rule_id": None
    }
]

patient_consultations = [
    {
        "id": 1,
        "provider_external_id": 1,
        "appointment_id": 1,
        "consultation_type_code": "pre_covid_consultation",
        "resolution_code": "pos_stable",
        "start_dt": today,
        "end_dt": tomorrow,
        "notes": "This patient is in a good condition",
        "create_dt": today,
        "update_dt": today
    }
]

ggt_users = [
    {
        "id": 1,
        "external_id": 1,
        "org_id": 1,
        "email": "test@test.com",
        "email_verified": 0,
        "family_name": "Wijesinghe",
        "given_name": "Visitha",
        "name": "test@test.com",
        "picture": "https://s.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fte.png",
        "roles": "billing_admin,care_provider,Care Provider,clinical_provider,Clinical Provider,Contact Center,customer_contact,Default,Portal Provider,site_admin,Site Admin,super_admin,Super Admin",
        "is_active": 1,
        "permissions": "add_schedule_generation_rule,add_schedule_generation_rule,api,api,archive_processed_notifications,archive_processed_notifications,assign_group,assign_group,assign_service,assign_service,call_patient,call_patient,create_group,create_group,create_insurance_record,create_insurance_record,create_location,create_location,delete_insurance_record,delete_insurance_record,delete_schedule,delete_schedule,delete_schedule_generation_rule,delete_schedule_generation_rule,edit_schedule_generation_rule,edit_schedule_generation_rule,general_search,general_search,generate_all_schedules,generate_all_schedules,generate_schedule,generate_schedule,get_all_groups,get_all_groups,get_all_services,get_all_services,get_all_test_results,get_all_test_results,get_billing_list,get_billing_list,get_locations,get_locations,get_provider_processing_list,get_provider_processing_list,get_schedule_generation_rules,get_schedule_generation_rules,get_workstations,get_workstations,location_search,location_search",
        "update_dt": "2021-01-31 09:58:04",
        "create_dt": "2020-12-31 00:54:10"
    },
    {
        "id": 2,
        "external_id": "auth0|5f98b2bede6fa700752b628f",
        "org_id": 1,
        "email": "test2@test.com",
        "email_verified": 0,
        "family_name": "Wijesinghe",
        "given_name": "Visitha",
        "name": "test@test.com",
        "picture": "https://s.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fte.png",
        "roles": "billing_admin,care_provider,Care Provider,clinical_provider,Clinical Provider,Contact Center,customer_contact,Default,Portal Provider,site_admin,Site Admin,super_admin,Super Admin",
        "is_active": 1,
        "permissions": "add_schedule_generation_rule,add_schedule_generation_rule,api,api,archive_processed_notifications,archive_processed_notifications,assign_group,assign_group,assign_service,assign_service,call_patient,call_patient,create_group,create_group,create_insurance_record,create_insurance_record,create_location,create_location,delete_insurance_record,delete_insurance_record,delete_schedule,delete_schedule,delete_schedule_generation_rule,delete_schedule_generation_rule,edit_schedule_generation_rule,edit_schedule_generation_rule,general_search,general_search,generate_all_schedules,generate_all_schedules,generate_schedule,generate_schedule,get_all_groups,get_all_groups,get_all_services,get_all_services,get_all_test_results,get_all_test_results,get_billing_list,get_billing_list,get_locations,get_locations,get_provider_processing_list,get_provider_processing_list,get_schedule_generation_rules,get_schedule_generation_rules,get_workstations,get_workstations,location_search,location_search",
        "update_dt": "2021-01-31 09:58:04",
        "create_dt": "2020-12-31 00:54:10"
    }
]

result_notification_campaigns = [
    {
        "test_id": 1,
        "patient_id": 1,
        "token": "4fa341f3-8338-4ae4-8515-c9a915625a3f",
        "phone_number": "+18018602474",
        "email": "sureshd@gmail.com",
        "first_name": "Suresh",
        "last_name": "Subasinghe",
        "dob": "10311980",
        "sms_sent": 1,
        "sms_dt": None,
        "email_sent": 1,
        "email_dt": "2020-08-02 15:22:28",
        "voice_sent": 1,
        "voice_dt": None,
        "group_notify": None,
        "overall_status": "pending",
        "create_dt": "2020-07-19 14:05:23",
        "update_dt": "2020-08-02 15:22:28"
    }
]

patient_questionnaires = [
    {
        "id": 1,
        "patient_id": 1,
        "token": None,
        "group_code": None,
        "symptom_fever": 0,
        "symptom_shortness_breath": 1,
        "symptom_cough": 0,
        "symptom_chest_pain": 0,
        "symptom_lack_of_smell": None,
        "symptom_other_breathing": 0,
        "covid_contact": 1,
        "prescription_use": 0,
        "heart_disease": 0,
        "diabetes": 0,
        "respiratory_diseases": 0,
        "autoimmune_disease": 0,
        "other_chronic": 0,
        "allergies": 0,
        "consent_signature": "1",
        "consent_date": None,
        "insurance_details": None,
        "has_insurance_photo": 0,
        "is_patient": None,
        "provider_consent_signature": None,
        "provider_consent_custom_field_1": None,
        "provider_consent_custom_field_2": None,
        "provider_consent_custom_field_3": None,
        "influenza_consent_signature": None,
        "public_places_bars_restaurants_cafes": None,
        "public_places_gas_stations": None,
        "public_places_medical_offices": None,
        "public_places_place_of_work": None,
        "public_places_retail_grocery_stores": None,
        "public_places_places_of_worship": None,
        "public_places_public_parks": None,
        "public_places_other": None,
        "service_covid19_test": None,
        "service_flu_shot": None,
        "service_consult": None,
        "flu_screen_severely_ill": None,
        "flu_screen_guillain_barre_syndrome": None,
        "flu_screen_life_threatening_reaction": None,
        "flu_screen_egg_allergy": None,
        "symptoms_vax": None,
        "pregnancy": None,
        "allergic_reaction": None,
        "covid19_confirmed_case": None,
        "egg_allergy": None,
        "guillian_barre": None,
        "create_dt": "2020-06-30 15:58:11",
        "update_dt": "2020-06-30 15:58:11",
        "recent_vaccinations": None,
        "blood_transfusion": None,
        "nervous_system": None,
        "immune_system_medications": None,
        "immune_system": None,
        "long_term_health": None,
        "ggv_allergies": None,
        "serious_reaction": None
    }
]

labs = [
    {
        "id": 1,
        "lab_name": "AIT/HealthTrackRx",
        "lab_code": "AIT",
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 2,
        "lab_name": "MAWD Pathology Group",
        "lab_code": "MAWD",
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 3,
        "lab_name": "Clinical Reference Laboratory",
        "lab_code": "CRL",
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 4,
        "lab_name": "LAB3A",
        "lab_code": "LAB3A",
        "create_dt": today,
        "update_dt": today
    },
    {
        "id": 5,
        "lab_name": "CHOPO Labs",
        "lab_code": "CHOPO",
        "create_dt": today,
        "update_dt": today
    },
]


sample_rpt = """
PID|x|x|{0}
OBR|x|{1}
OBX|x|x|x|x|{2}
"""

sample_idx = """
FILENAME={0}
REFERENCE_ID={1}
SID={2}
"""
