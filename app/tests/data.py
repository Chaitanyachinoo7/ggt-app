"""
Mock Data for tests
"""

locations = [
	{
		"id" : 1,
		"site_code" : "TEST_SITE_CODE",
		"org_id": 1,
		"name" : "TEST_LOCATION",
		"addr1" : "123 Any Street",
		"addr2" : None,
		"addr3" : None,
		"city" : "Any City",
		"st" : "ST",
		"zip" : "99999",
		"lat" : 33.160919,
		"lng" : -96.832382,
		"time_zone" : "CST",
		"time_zone_offset" : "-05:00",
		"test_type_offered" : "oral",
		"status" : "enabled",
		"type" : "drive_thru",
		"billing_type" : "insurance",
		"collect_insurance_info" : 1,
		"allow_insurance_skip" : 1,
		"collect_upfront_payment" : 0,
		"image_thumbnail" : "temp",
		"accepts_bookings" : None,
		"accepts_walkins" : None,
		"operator" : None,
		"phone_number" : None,
		"website" : None,
		"open_hours" : None,
		"misc" : None,
		"is_external" : 0,
		"create_dt" : "2020-07-21 14:40:53",
		"update_dt" : "2020-10-02 11:12:41"
	}
]

groups = [
	{
		"id" : 1,
		"account" : "_DEFAULT_",
		"group_code" : "_DEFAULT_",
		"is_referral_code" : 0,
		"consent_req" : 0,
		"collect_insurance" : 0,
		"insurance_req" : 0,
		"allow_insurance_skip" : 1,
		"upfront_payment_req" : 0,
		"screen_seq" : "is-patient,gender,race,ethnicity,symptoms,contact-tracing,public-places,patient-details,patient-address,patient-contact,patient-vitals,pre-existing-conditions,consent,date,location,time,insurance-card",
		"required_screens" : "insurance-card",
		"display_group_consent" : None,
		"consent_party_name" : None,
		"intro_text" : None,
		"consent_url" : None,
		"logo_1" : None,
		"logo_2" : None,
		"optional_screens" : None,
		"additional_fields" : None,
		"create_dt" : "2020-09-16 16:22:45",
		"update_dt" : "2020-09-16 16:22:45"
	}
]

group_codes_to_locations_mapping = [
	{
		"id" : 1,
		"group_id" : 1,
		"location_id" : 1
	}
]

schedules = [
	{
		"id" : 1,
		"location_id" : 1,
		"start_dt" : "2020-12-10 08:00:00",
		"end_dt" : "2020-12-10 08:10:00",
		"time_zone" : "CST",
		"time_zone_offset" : "-05:00",
		"duration" : 600,
		"status" : "available",
		"appointment_id" : None
	},
	{
		"id" : 2,
		"location_id" : 1,
		"start_dt" : "2025-12-15 08:00:00",
		"end_dt" : "2025-12-15 08:10:00",
		"time_zone" : "CST",
		"time_zone_offset" : "-05:00",
		"duration" : 600,
		"status" : "available",
		"appointment_id" : None
	}
]

patients = [
	{
		"id" : 1,
		"first_name" : "Roman",
		"middle_name" : "",
		"last_name" : "Dhimal",
		"gender" : "male",
		"height_ft" : "5”8",
		"height_in" : None,
		"weight_lb" : "120",
		"ethnicity" : "false",
		"race" : "race_asian",
		"addr1" : "5816 Hickoryhill Rd",
		"addr2" : None,
		"addr3" : None,
		"city" : "Watauga",
		"county" : "Tarrant",
		"st" : "TX",
		"zip" : "76148",
		"dob" : "2000-10-01",
		"phone_number" : "+16822022920",
		"phone_number_verified" : "1",
		"email" : "dhimalroman@gmail.com",
		"email_verified" : None,
		"token" : "8aa37097-2762-431f-b78c-1e9e582c4a19",
		"create_dt" : "2020-06-30 16:55:05",
		"update_dt" : "2020-06-30 16:55:05"
	}
]

appointments = [
	{
		"id" : 1,
		"scheduled_dt" : "2020-07-06 10:20:00",
		"check_in_dt" : None,
		"pre_consultation_provider_id" : None,
		"pre_consultation_notes" : None,
		"pre_consultaiton_start_dt" : None,
		"pre_consultation_end_dt" : None,
		"location_id" : 1,
		"group_code" : None,
		"patient_id" : 1,
		"patient_questionnaire_id" : 796,
		"vial_id" : None,
		"test_start_dt" : None,
		"test_end_dt" : None,
		"wp_receipt_token" : None,
		"wp_customer_info_id" : None,
		"total_cost" : None,
		"billed_amount" : None,
		"status" : "scheduled",
		"billing_status" : "pending",
		"create_dt" : "2020-07-06 16:40:09",
		"update_dt" : "2020-07-06 16:40:09"
	}
]

test_samples = [
	{
		"id" : 1,
		"appointment_id" : 1,
		"group_code" : None,
		"patient_id" : 1,
		"patient_questionnaire_id" : None,
		"provider_id" : None,
		"vial_id" : None,
		"sample_collection_location_id" : 1,
		"sample_collection_start_dt" : None,
		"sample_collection_end_dt" : None,
		"pre_ship_label_scan_dt" : "2020-12-14 19:58:05",
		"lab_id" : None,
		"lab_submission_batch_id" : None,
		"lab_physical_submission_dt" : None,
		"lab_electronic_submission_dt" : None,
		"lab_result_receive_dt" : None,
		"test_result" : "neg",
		"notification_status" : None,
		"notification_method" : None,
		"notification_acknowledgement_dt" : None,
		"consultation_status" : "pending",
		"consultation_notes" : None,
		"consultation_categorization" : None,
		"status" : None,
		"test_type" : "oral",
		"initial_billed_status" : 0,
		"post_test_billed_status" : 0,
		"create_dt" : "2020-11-23 13:09:35",
		"update_dt" : "2020-11-23 13:09:35"
	}
]

states = [
	{
		"id" : 1,
		"key" : "AL",
		"state" : "Alabama",
		"active" : 1
	},
	{
		"id" : 2,
		"key" : "AK",
		"state" : "Alaska",
		"active" : 1
	}
]

services_catalog = [
	{
		"id" : 1,
		"service_code" : "COVID_19_TEST",
		"service_name" : "Covid-19 Test",
		"price" : 175.00,
		"selfpay_amount" : 0.00,
		"copay_amount" : 0.00,
		"insurance_amount" : 0.00
	},
	{
		"id" : 2,
		"service_code" : "FLU_SHOT",
		"service_name" : "Flu Shot",
		"price" : 30.00,
		"selfpay_amount" : 30.00,
		"copay_amount" : 0.00,
		"insurance_amount" : 0.00
	},
	{
		"id" : 3,
		"service_code" : "CONSULT",
		"service_name" : "Consultation",
		"price" : 0.00,
		"selfpay_amount" : 0.00,
		"copay_amount" : 0.00,
		"insurance_amount" : 0.00
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
		"id" : 1,
		"label" : "METOHH1",
		"description" : None,
		"printer_info" : None,
		"token" : "f25ee64b-4d6d-4619-8c26-37a9e3ea0095",
		"create_dt" : "2020-09-01 07:38:07",
		"update_dt" : "2020-09-01 07:38:07"
	}
]

users = [
	{
		"id" : 1,
		"name" : "Raquel Manzaneres",
		"phone_number" : "",
		"email" : "raquel@wellhealth.studio",
		"role" : "billing"
	}
]

appointment_services = [
	{
		"id" : 1,
		"appointment_id" : 1,
		"service_id" : 1,
		"service_description" : "Covid-19 Test",
		"price" : 175.00,
		"selfpay_amount" : 0.00,
		"copay_amount" : 0.00,
		"insurance_amount" : 0.00,
		"create_dt" : "2020-10-06 11:01:13",
		"update_dt" : "2020-10-06 11:01:13"
	}
]

organizations = [
	{
		"id" : 1,
		"name" : "TEST_ORG",
		"email" : "test@gmail.com",
		"owner_ext_id" : "auth0|5fefdbd3066c72006804043c",
		"is_active" : 1,
		"update_dt" : "2021-01-10 21:09:47",
		"create_dt" : "2021-01-02 02:35:04"
	}
]
