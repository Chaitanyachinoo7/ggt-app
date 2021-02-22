from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, constr
from pprint import pprint


class MSH(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/MSH
    msh_1_field_separator = ''
    msh_2_encoding_characters = ''
    msh_3_sending_application = ''
    msh_4_sending_facility = ''
    msh_5_receiving_application = ''
    msh_6_receiving_facility = ''
    msh_7_datetime_of_message = ''  # Timestamp
    msh_8_security = ''
    msh_9_message_type = ''
    msh_10_message_control_id = ''
    msh_11_processing_id = ''
    msh_12_version_id = ''
    msh_13_sequence_number = ''
    msh_14_continuation_pointer = ''
    msh_15_accept_acknowledgment_type = ''
    msh_16_application_acknowledgment_type = ''
    msh_17_country_code = ''
    msh_18_character_set = ''
    msh_19_principal_language_of_message = ''
    msh_20_alternate_character_set_handling_scheme = ''
    msh_21_message_profile_identifier = ''

    def __str__(self):
        return 'MSH|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.msh_1_field_separator,
            self.msh_2_encoding_characters,
            self.msh_3_sending_application,
            self.msh_4_sending_facility,
            self.msh_5_receiving_application,
            self.msh_6_receiving_facility,
            self.msh_7_datetime_of_message,
            self.msh_8_security,
            self.msh_9_message_type,
            self.msh_10_message_control_id,
            self.msh_11_processing_id,
            self.msh_12_version_id,
            self.msh_13_sequence_number,
            self.msh_14_continuation_pointer,
            self.msh_15_accept_acknowledgment_type,
            self.msh_16_application_acknowledgment_type,
            self.msh_17_country_code,
            self.msh_18_character_set,
            self.msh_19_principal_language_of_message,
            self.msh_20_alternate_character_set_handling_scheme,
            self.msh_21_message_profile_identifier
        )


class MSG(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/MSG
    msg_1_message_code = ''
    msg_2_trigger_event = ''
    msg_3_message_structure = ''

    def __str__(self):
        return '{}|{}|{}'.format(
            self.msg_1_message_code,
            self.msg_2_trigger_event,
            self.msg_3_message_structure
        )


class PID(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/PID
    pid_1_set_id = ''
    pid_2_patient_id = ''
    pid_3_patient_identifier_list = ''
    pid_4_alternate_patient_id_pid = ''
    pid_5_patient_name = ''
    pid_6_mothers_maiden_name = ''
    pid_7_date_time_of_birth = ''
    pid_8_administrative_sex = ''
    pid_9_patient_alias = ''
    pid_10_race = ''
    pid_11_patient_address = ''
    pid_12_county_code = ''
    pid_13_phone_number_home = ''
    pid_14_phone_number_business = ''
    pid_15_primary_language = ''
    pid_16_marital_status = ''
    pid_17_religion = ''
    pid_18_patient_account_number = ''
    pid_19_ssn_number_patient = ''
    pid_20_drivers_license_number_patient = ''
    pid_21_mothers_identifier = ''
    pid_22_ethnic_group = ''
    pid_23_birth_place = ''
    pid_24_multiple_birth_indicator = ''
    pid_25_birth_order = ''
    pid_26_citizenship = ''
    pid_27_veterans_military_status = ''
    pid_28_nationality = ''
    pid_29_patient_death_date_and_time = ''
    pid_30_patient_death_indicator = ''
    pid_31_identity_unknown_indicator = ''
    pid_32_identity_reliability_code = ''
    pid_33_last_update_datetime = ''
    pid_34_last_update_facility = ''
    pid_35_species_code = ''
    pid_36_breed_code = ''
    pid_37_strain = ''
    pid_38_production_class_code = ''
    pid_39_tribal_citizenship = ''

    def __str__(self):
        return 'PID|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.pid_1_set_id,
            self.pid_2_patient_id,
            self.pid_3_patient_identifier_list,
            self.pid_4_alternate_patient_id_pid,
            self.pid_5_patient_name,
            self.pid_6_mothers_maiden_name,
            self.pid_7_date_time_of_birth,
            self.pid_8_administrative_sex,
            self.pid_9_patient_alias,
            self.pid_10_race,
            self.pid_11_patient_address,
            self.pid_12_county_code,
            self.pid_13_phone_number_home,
            self.pid_14_phone_number_business,
            self.pid_15_primary_language,
            self.pid_16_marital_status,
            self.pid_17_religion,
            self.pid_18_patient_account_number,
            self.pid_19_ssn_number_patient,
            self.pid_20_drivers_license_number_patient,
            self.pid_21_mothers_identifier,
            self.pid_22_ethnic_group,
            self.pid_23_birth_place,
            self.pid_24_multiple_birth_indicator,
            self.pid_25_birth_order,
            self.pid_26_citizenship,
            self.pid_27_veterans_military_status,
            self.pid_28_nationality,
            self.pid_29_patient_death_date_and_time,
            self.pid_30_patient_death_indicator,
            self.pid_31_identity_unknown_indicator,
            self.pid_32_identity_reliability_code,
            self.pid_33_last_update_datetime,
            self.pid_34_last_update_facility,
            self.pid_35_species_code,
            self.pid_36_breed_code,
            self.pid_37_strain,
            self.pid_38_production_class_code,
            self.pid_39_tribal_citizenship
        )


class IN1(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/IN1
    in1_1_set_id = ''
    in1_2_insurance_plan_id = ''
    in1_3_insurance_company_id = ''
    in1_4_insurance_company_name = ''
    in1_5_insurance_company_address = ''
    in1_6_insurance_co_contact_person = ''
    in1_7_insurance_co_phone_number = ''
    in1_8_group_number = ''
    in1_9_group_name = ''
    in1_10_insureds_group_emp_id = ''
    in1_11_insureds_group_emp_name = ''
    in1_12_plan_effective_date = ''
    in1_13_plan_expiration_date = ''
    in1_14_authorization_information = ''
    in1_15_plan_type = ''
    in1_16_name_of_insured = ''
    in1_17_insureds_relationship_to_patient = ''
    in1_18_insureds_date_of_birth = ''
    in1_19_insureds_address = ''
    in1_20_assignment_of_benefits = ''
    in1_21_coordination_of_benefits = ''
    in1_22_coord_of_ben_priority = ''
    in1_23_notice_of_admission_flag = ''
    in1_24_notice_of_admission_date = ''
    in1_25_report_of_eligibility_flag = ''
    in1_26_report_of_eligibility_date = ''
    in1_27_release_information_code = ''
    in1_28_pre_admit_cert_pac = ''
    in1_29_verification_datetime = ''
    in1_30_verification_by = ''
    in1_31_type_of_agreement_code = ''
    in1_32_billing_status: \
        Optional[str] = ''
    in1_33_lifetime_reserve_days = ''
    in1_34_delay_before_l_r_day = ''
    in1_35_company_plan_code = ''
    in1_36_policy_number = ''
    in1_37_policy_deductible = ''
    in1_38_policy_limit_amount = ''
    in1_39_policy_limit_days = ''
    in1_40_room_rate_semi_private = ''
    in1_41_room_rate_private = ''
    in1_42_insureds_employment_status = ''
    in1_43_insureds_administrative_sex = ''
    in1_44_insureds_employers_address = ''
    in1_45_verification_status = ''
    in1_46_prior_insurance_plan_id = ''
    in1_47_coverage_type = ''
    in1_48_handicap = ''
    in1_49_insureds_id_number = ''
    in1_50_signature_code = ''
    in1_51_signature_code_date = ''
    in1_52_insureds_birth_place = ''
    in1_53_vip_indicator = ''

    def __str__(self):
        return 'IN1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.in1_1_set_id,
            self.in1_2_insurance_plan_id,
            self.in1_3_insurance_company_id,
            self.in1_4_insurance_company_name,
            self.in1_5_insurance_company_address,
            self.in1_6_insurance_co_contact_person,
            self.in1_7_insurance_co_phone_number,
            self.in1_8_group_number,
            self.in1_9_group_name,
            self.in1_10_insureds_group_emp_id,
            self.in1_11_insureds_group_emp_name,
            self.in1_12_plan_effective_date,
            self.in1_13_plan_expiration_date,
            self.in1_14_authorization_information,
            self.in1_15_plan_type,
            self.in1_16_name_of_insured,
            self.in1_17_insureds_relationship_to_patient,
            self.in1_18_insureds_date_of_birth,
            self.in1_19_insureds_address,
            self.in1_20_assignment_of_benefits,
            self.in1_21_coordination_of_benefits,
            self.in1_22_coord_of_ben_priority,
            self.in1_23_notice_of_admission_flag,
            self.in1_24_notice_of_admission_date,
            self.in1_25_report_of_eligibility_flag,
            self.in1_26_report_of_eligibility_date,
            self.in1_27_release_information_code,
            self.in1_28_pre_admit_cert_pac,
            self.in1_29_verification_datetime,
            self.in1_30_verification_by,
            self.in1_31_type_of_agreement_code,
            self.in1_32_billing_status,
            self.in1_33_lifetime_reserve_days,
            self.in1_34_delay_before_l_r_day,
            self.in1_35_company_plan_code,
            self.in1_36_policy_number,
            self.in1_37_policy_deductible,
            self.in1_38_policy_limit_amount,
            self.in1_39_policy_limit_days,
            self.in1_40_room_rate_semi_private,
            self.in1_41_room_rate_private,
            self.in1_42_insureds_employment_status,
            self.in1_43_insureds_administrative_sex,
            self.in1_44_insureds_employers_address,
            self.in1_45_verification_status,
            self.in1_46_prior_insurance_plan_id,
            self.in1_47_coverage_type,
            self.in1_48_handicap,
            self.in1_49_insureds_id_number,
            self.in1_50_signature_code,
            self.in1_51_signature_code_date,
            self.in1_52_insureds_birth_place,
            self.in1_53_vip_indicator
        )


class PV1(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/PV1
    pv1_1_set_id = ''
    pv1_2_patient_class = ''
    pv1_3_assigned_patient_location = ''
    pv1_4_admission_type = ''
    pv1_5_preadmit_number = ''
    pv1_6_prior_patient_location = ''
    pv1_7_attending_doctor = ''
    pv1_8_referring_doctor = ''
    pv1_9_consulting_doctor = ''
    pv1_10_hospital_service = ''
    pv1_11_temporary_location = ''
    pv1_12_preadmit_test_indicator = ''
    pv1_13_re_admission_indicator = ''
    pv1_14_admit_source = ''
    pv1_15_ambulatory_status = ''
    pv1_16_vip_indicator = ''
    pv1_17_admitting_doctor = ''
    pv1_18_patient_type = ''
    pv1_19_visit_number = ''
    pv1_20_financial_class = ''
    pv1_21_charge_price_indicator = ''
    pv1_22_courtesy_code = ''
    pv1_23_credit_rating = ''
    pv1_24_contract_code = ''
    pv1_25_contract_effective_date = ''
    pv1_26_contract_amount = ''
    pv1_27_contract_period = ''
    pv1_28_interest_code = ''
    pv1_29_transfer_to_bad_debt_code = ''
    pv1_30_transfer_to_bad_debt_date = ''
    pv1_31_bad_debt_agency_code = ''
    pv1_32_bad_debt_transfer_amount = ''
    pv1_33_bad_debt_recovery_amount = ''
    pv1_34_delete_account_indicator = ''
    pv1_35_delete_account_date = ''
    pv1_36_discharge_disposition = ''
    pv1_37_discharged_to_location = ''
    pv1_38_diet_type = ''
    pv1_39_servicing_facility = ''
    pv1_40_bed_status = ''
    pv1_41_account_status = ''
    pv1_42_pending_location = ''
    pv1_43_prior_temporary_location = ''
    pv1_44_admit_datetime = ''
    pv1_45_discharge_datetime = ''
    pv1_46_current_patient_balance = ''
    pv1_47_total_charges = ''
    pv1_48_total_adjustments = ''
    pv1_49_total_payments = ''
    pv1_50_alternate_visit_id = ''
    pv1_51_visit_indicator = ''
    pv1_52_other_healthcare_provider = ''

    def __str__(self):
        return 'PV1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.pv1_1_set_id,
            self.pv1_2_patient_class,
            self.pv1_3_assigned_patient_location,
            self.pv1_4_admission_type,
            self.pv1_5_preadmit_number,
            self.pv1_6_prior_patient_location,
            self.pv1_7_attending_doctor,
            self.pv1_8_referring_doctor,
            self.pv1_9_consulting_doctor,
            self.pv1_10_hospital_service,
            self.pv1_11_temporary_location,
            self.pv1_12_preadmit_test_indicator,
            self.pv1_13_re_admission_indicator,
            self.pv1_14_admit_source,
            self.pv1_15_ambulatory_status,
            self.pv1_16_vip_indicator,
            self.pv1_17_admitting_doctor,
            self.pv1_18_patient_type,
            self.pv1_19_visit_number,
            self.pv1_20_financial_class,
            self.pv1_21_charge_price_indicator,
            self.pv1_22_courtesy_code,
            self.pv1_23_credit_rating,
            self.pv1_24_contract_code,
            self.pv1_25_contract_effective_date,
            self.pv1_26_contract_amount,
            self.pv1_27_contract_period,
            self.pv1_28_interest_code,
            self.pv1_29_transfer_to_bad_debt_code,
            self.pv1_30_transfer_to_bad_debt_date,
            self.pv1_31_bad_debt_agency_code,
            self.pv1_32_bad_debt_transfer_amount,
            self.pv1_33_bad_debt_recovery_amount,
            self.pv1_34_delete_account_indicator,
            self.pv1_35_delete_account_date,
            self.pv1_36_discharge_disposition,
            self.pv1_37_discharged_to_location,
            self.pv1_38_diet_type,
            self.pv1_39_servicing_facility,
            self.pv1_40_bed_status,
            self.pv1_41_account_status,
            self.pv1_42_pending_location,
            self.pv1_43_prior_temporary_location,
            self.pv1_44_admit_datetime,
            self.pv1_45_discharge_datetime,
            self.pv1_46_current_patient_balance,
            self.pv1_47_total_charges,
            self.pv1_48_total_adjustments,
            self.pv1_49_total_payments,
            self.pv1_50_alternate_visit_id,
            self.pv1_51_visit_indicator,
            self.pv1_52_other_healthcare_provider
        )


class OBX(BaseModel):
    # https://hl7-definition.caristix.com/v2/hl7v2.5.1/segments/obx
    obx_1_set_id = ''
    obx_2_value_type = ''
    obx_3_observation_identifier = ''
    obx_4_observation_sub_id = ''
    obx_5_observation_value = ''
    obx_6_units = ''
    obx_7_references_range = ''
    obx_8_abnormal_flags = ''
    obx_9_probability = ''
    obx_10_nature_of_abnormal_test = ''
    obx_11_observation_result_status = ''
    obx_12_effective_date_of_reference_range = ''
    obx_13_user_defined_access_checks = ''
    obx_14_datetime_of_the_observation = ''
    obx_15_producers_id = ''
    obx_16_responsible_observer = ''
    obx_17_observation_method = ''
    obx_18_equipment_instance_identifier = ''
    obx_19_datetime_of_the_analysis = ''
    obx_20_reserved_for_harmonization_with_v2_6 = ''
    obx_21_reserved_for_harmonization_with_v2_6 = ''
    obx_22_reserved_for_harmonization_with_v2_6 = ''
    obx_23_performing_organization_name = ''
    obx_24_performing_organization_address = ''
    obx_25_performing_organization_medical_director = ''

    def __str__(self):
        return 'OBX|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.obx_1_set_id,
            self.obx_2_value_type,
            self.obx_3_observation_identifier,
            self.obx_4_observation_sub_id,
            self.obx_5_observation_value,
            self.obx_6_units,
            self.obx_7_references_range,
            self.obx_8_abnormal_flags,
            self.obx_9_probability,
            self.obx_10_nature_of_abnormal_test,
            self.obx_11_observation_result_status,
            self.obx_12_effective_date_of_reference_range,
            self.obx_13_user_defined_access_checks,
            self.obx_14_datetime_of_the_observation,
            self.obx_15_producers_id,
            self.obx_16_responsible_observer,
            self.obx_17_observation_method,
            self.obx_18_equipment_instance_identifier,
            self.obx_19_datetime_of_the_analysis,
            self.obx_20_reserved_for_harmonization_with_v2_6,
            self.obx_21_reserved_for_harmonization_with_v2_6,
            self.obx_22_reserved_for_harmonization_with_v2_6,
            self.obx_23_performing_organization_name,
            self.obx_24_performing_organization_address,
            self.obx_25_performing_organization_medical_director
        )


class GT1(BaseModel): \
        # https://hl7-definition.caristix.com/v2/hl7v2.5.1/segments/gt1
    gt1_1_set_id_gt1 = ''
    gt1_2_guarantor_number = ''
    gt1_3_guarantor_name = ''
    gt1_4_guarantor_spouse_name = ''
    gt1_5_guarantor_address = ''
    gt1_6_guarantor_ph_num_home = ''
    gt1_7_guarantor_ph_num_business = ''
    gt1_8_guarantor_datetime_of_birth = ''
    gt1_9_guarantor_administrative_sex = ''
    gt1_10_guarantor_type = ''
    gt1_11_guarantor_relationship = ''
    gt1_12_guarantor_ssn = ''
    gt1_13_guarantor_date_begin = ''
    gt1_14_guarantor_date_end = ''
    gt1_15_guarantor_priority = ''
    gt1_16_guarantor_employer_name = ''
    gt1_17_guarantor_employer_address = ''
    gt1_18_guarantor_employer_phone_number = ''
    gt1_19_guarantor_employee_id_number = ''
    gt1_20_guarantor_employment_status = ''
    gt1_21_guarantor_organization_name = ''
    gt1_22_guarantor_billing_hold_flag = ''
    gt1_23_guarantor_credit_rating_code = ''
    gt1_24_guarantor_death_date_and_time = ''
    gt1_25_guarantor_death_flag = ''
    gt1_26_guarantor_charge_adjustment_code = ''
    gt1_27_guarantor_household_annual_income = ''
    gt1_28_guarantor_household_size = ''
    gt1_29_guarantor_employer_id_number = ''
    gt1_30_guarantor_marital_status_code = ''
    gt1_31_guarantor_hire_effective_date = ''
    gt1_32_employment_stop_date = ''
    gt1_33_living_dependency = ''
    gt1_34_ambulatory_status = ''
    gt1_35_citizenship = ''
    gt1_36_primary_language = ''
    gt1_37_living_arrangement = ''
    gt1_38_publicity_code = ''
    gt1_39_protection_indicator = ''
    gt1_40_student_indicator = ''
    gt1_41_religion = ''
    gt1_42_mothers_maiden_name = ''
    gt1_43_nationality = ''
    gt1_44_ethnic_group = ''
    gt1_45_contact_persons_name = ''
    gt1_46_contact_persons_telephone_number = ''
    gt1_47_contact_reason = ''
    gt1_48_contact_relationship = ''
    gt1_49_job_title = ''
    gt1_50_job_code_class = ''
    gt1_51_guarantor_employers_organization_name = ''
    gt1_52_handicap = ''
    gt1_53_job_status = ''
    gt1_54_guarantor_financial_class = ''
    gt1_55_guarantor_race = ''
    gt1_56_guarantor_birth_place = ''
    gt1_57_vip_indicator = ''

    def __str__(self):
        return 'GT1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.gt1_1_set_id_gt1,
            self.gt1_2_guarantor_number,
            self.gt1_3_guarantor_name,
            self.gt1_4_guarantor_spouse_name,
            self.gt1_5_guarantor_address,
            self.gt1_6_guarantor_ph_num_home,
            self.gt1_7_guarantor_ph_num_business,
            self.gt1_8_guarantor_datetime_of_birth,
            self.gt1_9_guarantor_administrative_sex,
            self.gt1_10_guarantor_type,
            self.gt1_11_guarantor_relationship,
            self.gt1_12_guarantor_ssn,
            self.gt1_13_guarantor_date_begin,
            self.gt1_14_guarantor_date_end,
            self.gt1_15_guarantor_priority,
            self.gt1_16_guarantor_employer_name,
            self.gt1_17_guarantor_employer_address,
            self.gt1_18_guarantor_employer_phone_number,
            self.gt1_19_guarantor_employee_id_number,
            self.gt1_20_guarantor_employment_status,
            self.gt1_21_guarantor_organization_name,
            self.gt1_22_guarantor_billing_hold_flag,
            self.gt1_23_guarantor_credit_rating_code,
            self.gt1_24_guarantor_death_date_and_time,
            self.gt1_25_guarantor_death_flag,
            self.gt1_26_guarantor_charge_adjustment_code,
            self.gt1_27_guarantor_household_annual_income,
            self.gt1_28_guarantor_household_size,
            self.gt1_29_guarantor_employer_id_number,
            self.gt1_30_guarantor_marital_status_code,
            self.gt1_31_guarantor_hire_effective_date,
            self.gt1_32_employment_stop_date,
            self.gt1_33_living_dependency,
            self.gt1_34_ambulatory_status,
            self.gt1_35_citizenship,
            self.gt1_36_primary_language,
            self.gt1_37_living_arrangement,
            self.gt1_38_publicity_code,
            self.gt1_39_protection_indicator,
            self.gt1_40_student_indicator,
            self.gt1_41_religion,
            self.gt1_42_mothers_maiden_name,
            self.gt1_43_nationality,
            self.gt1_44_ethnic_group,
            self.gt1_45_contact_persons_name,
            self.gt1_46_contact_persons_telephone_number,
            self.gt1_47_contact_reason,
            self.gt1_48_contact_relationship,
            self.gt1_49_job_title,
            self.gt1_50_job_code_class,
            self.gt1_51_guarantor_employers_organization_name,
            self.gt1_52_handicap,
            self.gt1_53_job_status,
            self.gt1_54_guarantor_financial_class,
            self.gt1_55_guarantor_race,
            self.gt1_56_guarantor_birth_place,
            self.gt1_57_vip_indicator
        )


class OBR(BaseModel): \
        # https://hl7-definition.caristix.com/v2/hl7v2.5.1/segments/obr
    obr_1_set_id = ''
    obr_2_placer_order_number = ''
    obr_3_filler_order_number = ''
    obr_4_universal_service_identifier = ''
    obr_5_priority_obr = ''
    obr_6_requested_datetime = ''
    obr_7_observation_datetime = ''
    obr_8_observation_end_datetime = ''
    obr_9_collection_volume = ''
    obr_10_collector_identifier = ''
    obr_11_specimen_action_code = ''
    obr_12_danger_code = ''
    obr_13_relevant_clinical_information = ''
    obr_14_specimen_received_datetime = ''
    obr_15_specimen_source = ''
    obr_16_ordering_provider = ''
    obr_17_order_callback_phone_number = ''
    obr_18_placer_field_1 = ''
    obr_19_placer_field_2 = ''
    obr_20_filler_field_1 = ''
    obr_21_filler_field_2 = ''
    obr_22_results_rpt_status_chng_datetime = ''
    obr_23_charge_to_practice = ''
    obr_24_diagnostic_serv_sect_id = ''
    obr_25_result_status = ''
    obr_26_parent_result = ''
    obr_27_quantity_timing = ''
    obr_28_result_copies_to = ''
    obr_29_parent = ''
    obr_30_transportation_mode = ''
    obr_31_reason_for_study = ''
    obr_32_principal_result_interpreter = ''
    obr_33_assistant_result_interpreter = ''
    obr_34_technician = ''
    obr_35_transcriptionist = ''
    obr_36_scheduled_datetime = ''
    obr_37_number_of_sample_containers = ''
    obr_38_transport_logistics_of_collected_sample = ''
    obr_39_collectors_comment = ''
    obr_40_transport_arrangement_responsibility = ''
    obr_41_transport_arranged = ''
    obr_42_escort_required = ''
    obr_43_planned_patient_transport_comment = ''
    obr_44_procedure_code = ''
    obr_45_procedure_code_modifier = ''
    obr_46_placer_supplemental_service_information = ''
    obr_47_filler_supplemental_service_information = ''
    obr_48_medically_necessary_duplicate_procedure_reason_ = ''
    obr_49_result_handling = ''
    obr_50_parent_universal_service_identifier = ''

    def __str__(self):
        return 'OBR|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.obr_1_set_id,
            self.obr_2_placer_order_number,
            self.obr_3_filler_order_number,
            self.obr_4_universal_service_identifier,
            self.obr_5_priority_obr,
            self.obr_6_requested_datetime,
            self.obr_7_observation_datetime,
            self.obr_8_observation_end_datetime,
            self.obr_9_collection_volume,
            self.obr_10_collector_identifier,
            self.obr_11_specimen_action_code,
            self.obr_12_danger_code,
            self.obr_13_relevant_clinical_information,
            self.obr_14_specimen_received_datetime,
            self.obr_15_specimen_source,
            self.obr_16_ordering_provider,
            self.obr_17_order_callback_phone_number,
            self.obr_18_placer_field_1,
            self.obr_19_placer_field_2,
            self.obr_20_filler_field_1,
            self.obr_21_filler_field_2,
            self.obr_22_results_rpt_status_chng_datetime,
            self.obr_23_charge_to_practice,
            self.obr_24_diagnostic_serv_sect_id,
            self.obr_25_result_status,
            self.obr_26_parent_result,
            self.obr_27_quantity_timing,
            self.obr_28_result_copies_to,
            self.obr_29_parent,
            self.obr_30_transportation_mode,
            self.obr_31_reason_for_study,
            self.obr_32_principal_result_interpreter,
            self.obr_33_assistant_result_interpreter,
            self.obr_34_technician,
            self.obr_35_transcriptionist,
            self.obr_36_scheduled_datetime,
            self.obr_37_number_of_sample_containers,
            self.obr_38_transport_logistics_of_collected_sample,
            self.obr_39_collectors_comment,
            self.obr_40_transport_arrangement_responsibility,
            self.obr_41_transport_arranged,
            self.obr_42_escort_required,
            self.obr_43_planned_patient_transport_comment,
            self.obr_44_procedure_code,
            self.obr_45_procedure_code_modifier,
            self.obr_46_placer_supplemental_service_information,
            self.obr_47_filler_supplemental_service_information,
            self.obr_48_medically_necessary_duplicate_procedure_reason_,
            self.obr_49_result_handling,
            self.obr_50_parent_universal_service_identifier
        )


class DG1(BaseModel): \
        # https://hl7-definition.caristix.com/v2/hl7v2.5.1/segments/dg1
    dg1_1_set_id_dg1 = ''
    dg1_2_diagnosis_coding_method = ''
    dg1_3_diagnosis_code_dg1 = ''
    dg1_4_diagnosis_description = ''
    dg1_5_diagnosis_datetime = ''
    dg1_6_diagnosis_type = ''
    dg1_7_major_diagnostic_category = ''
    dg1_8_diagnostic_related_group = ''
    dg1_9_drg_approval_indicator = ''
    dg1_10_drg_grouper_review_code = ''
    dg1_11_outlier_type = ''
    dg1_12_outlier_days = ''
    dg1_13_outlier_cost = ''
    dg1_14_grouper_version_and_type = ''
    dg1_15_diagnosis_priority = ''
    dg1_16_diagnosing_clinician = ''
    dg1_17_diagnosis_classification = ''
    dg1_18_confidential_indicator = ''
    dg1_19_attestation_datetime = ''
    dg1_20_diagnosis_identifier = ''
    dg1_21_diagnosis_action_code = ''

    def __str__(self):
        return 'DG1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.dg1_1_set_id_dg1,
            self.dg1_2_diagnosis_coding_method,
            self.dg1_3_diagnosis_code_dg1,
            self.dg1_4_diagnosis_description,
            self.dg1_5_diagnosis_datetime,
            self.dg1_6_diagnosis_type,
            self.dg1_7_major_diagnostic_category,
            self.dg1_8_diagnostic_related_group,
            self.dg1_9_drg_approval_indicator,
            self.dg1_10_drg_grouper_review_code,
            self.dg1_11_outlier_type,
            self.dg1_12_outlier_days,
            self.dg1_13_outlier_cost,
            self.dg1_14_grouper_version_and_type,
            self.dg1_15_diagnosis_priority,
            self.dg1_16_diagnosing_clinician,
            self.dg1_17_diagnosis_classification,
            self.dg1_18_confidential_indicator,
            self.dg1_19_attestation_datetime,
            self.dg1_20_diagnosis_identifier,
            self.dg1_21_diagnosis_action_code
        )


class ORC(BaseModel):
    orc_1_order_control = ''
    orc_2_placer_order_number = ''
    orc_3_filler_order_number = ''
    orc_4_placer_group_number = ''
    orc_5_order_status = ''
    orc_6_response_flag = ''
    orc_7_quantitytiming = ''
    orc_8_parent_order = ''
    orc_9_datetime_of_transaction = ''
    orc_10_entered_by = ''
    orc_11_verified_by = ''
    orc_12_ordering_provider = ''
    orc_13_enterers_location = ''
    orc_14_call_back_phone_number = ''
    orc_15_order_effective_datetime = ''
    orc_16_order_control_code_reason = ''
    orc_17_entering_organization = ''
    orc_18_entering_device = ''
    orc_19_action_by = ''
    orc_20_advanced_beneficiary_notice_code = ''
    orc_21_ordering_facility_name = ''
    orc_22_ordering_facility_address = ''
    orc_23_ordering_facility_phone_number = ''
    orc_24_ordering_provider_address = ''
    orc_25_order_status_modifier = ''
    orc_26_advanced_beneficiary_notice_override_reason = ''
    orc_27_fillers_expected_availability_datetime = ''
    orc_28_confidentiality_code = ''
    orc_29_order_type = ''
    orc_30_enterer_authorization_mode = ''
    orc_31_parent_universal_service_identifier = ''
    
    def __str__(self):
        return 'ORC|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.orc_1_order_control,
            self.orc_2_placer_order_number,
            self.orc_3_filler_order_number,
            self.orc_4_placer_group_number,
            self.orc_5_order_status,
            self.orc_6_response_flag,
            self.orc_7_quantitytiming,
            self.orc_8_parent_order,
            self.orc_9_datetime_of_transaction,
            self.orc_10_entered_by,
            self.orc_11_verified_by,
            self.orc_12_ordering_provider,
            self.orc_13_enterers_location,
            self.orc_14_call_back_phone_number,
            self.orc_15_order_effective_datetime,
            self.orc_16_order_control_code_reason,
            self.orc_17_entering_organization,
            self.orc_18_entering_device,
            self.orc_19_action_by,
            self.orc_20_advanced_beneficiary_notice_code,
            self.orc_21_ordering_facility_name,
            self.orc_22_ordering_facility_address,
            self.orc_23_ordering_facility_phone_number,
            self.orc_24_ordering_provider_address,
            self.orc_25_order_status_modifier,
            self.orc_26_advanced_beneficiary_notice_override_reason,
            self.orc_27_fillers_expected_availability_datetime,
            self.orc_28_confidentiality_code,
            self.orc_29_order_type,
            self.orc_30_enterer_authorization_mode,
            self.orc_31_parent_universal_service_identifier
        )



class Message(BaseModel):
    msh: MSH = ''
    pid: Optional[PID] = ''
    pv1: Optional[PV1] = ''
    in1: Optional[IN1] = ''
    orc: Optional[ORC] = ''
    obr: Optional[OBR] = ''
    dg1: Optional[DG1] = ''
    obx_list: Optional[List[OBX]] = ''
    def __str__(self):
        _str = ''
        for obx in self.obx_list:
            _str = _str + str(obx) + '\n'
            
        return '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
            str(self.msh),
            str(self.pid),
            str(self.pv1),
            str(self.in1),
            str(self.orc),
            str(self.dg1),
            str(self.obr),
            _str
        )


'''
msh = MSH(
    msh_1_field_separator='|',
    msh_2_encoding_characters='^~\&',
    msh_3_sending_application='DEMOFAC',
    msh_4_sending_facility='DEMOFAC',
    msh_5_receiving_application='AIT',
    msh_6_receiving_facility='AIT',
    msh_7_datetime_of_message=datetime.now().strftime("%Y%m%d%H%M%S"),
    msh_8_security='XXX',
    msh_9_message_type='ORM^O01',
    msh_10_message_control_id=31705156,
    msh_11_processing_id='P',
    msh_12_version_id='2.3'
)

pid = PID(
    pid_1_set_id=1,
    pid_2_patient_id='27927IN',
    pid_3_patient_identifier_list='27927IN',
    pid_4_alternate_patient_id_pid='Test123IN',
    pid_5_patient_name='Htrxtest^TestIN^^^',
    pid_6_mothers_maiden_name='',
    pid_7_date_time_of_birth='19900101',
    pid_8_administrative_sex='M',
    pid_9_patient_alias='^',
    pid_10_race='2054-5',
    pid_11_patient_address='123 Main Ln.^^Allen^TX^75002^^^^',
    pid_12_county_code='',
    pid_13_phone_number_home='(469)987-6521',
    pid_18_patient_account_number='Test123^^^P',
    pid_19_ssn_number_patient='',
    pid_20_drivers_license_number_patient='',
    pid_22_ethnic_group='H'
)

pv1 = PV1(
    pv1_1_set_id=1,
    pv1_3_assigned_patient_location='2',
    pv1_7_attending_doctor='1982044657^Ramirez^Diana^MD/PMEMR',
    pv1_17_admitting_doctor='1982044657^Ramirez^Diana^MD/PMEMR'
)

in1 = IN1(
    in1_1_set_id=1,
    in1_3_insurance_company_id='MMP',
    in1_4_insurance_company_name='MEDICARE MASTER PAYER',
    in1_16_name_of_insured='DOE^JOHN^M',
    in1_17_insureds_relationship_to_patient='01',
    in1_18_insureds_date_of_birth='195208150000',
    in1_19_insureds_address='1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US',
    in1_22_coord_of_ben_priority='1',
    in1_32_billing_status='INSURANCE',
    in1_36_policy_number='8J89UD3HR59',
    in1_43_insureds_administrative_sex='F'

)


obx2 = OBX(
    obx_1_set_id=2,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-1^Is this the patient\'s first COVID-19 test?',
    obx_5_observation_value='U^Unknown'
)

obx3 = OBX(
    obx_1_set_id=3,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-2^Is the patient employed in healthcare with direct patient contact?',
    obx_5_observation_value='U^Unknown'
)

obx4 = OBX(
    obx_1_set_id=4,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?',
    obx_5_observation_value='Y^Yes'
)

obx5 = OBX(
    obx_1_set_id=5,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)',
    obx_5_observation_value='20200731'
)

obx6 = OBX(
    obx_1_set_id=6,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-4^Has the patient been hospalized?',
    obx_5_observation_value='N^No'
)

obx7 = OBX(
    obx_1_set_id=7,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-5^Has the patient been hospalized in the ICU?',
    obx_5_observation_value='N^No'
)
obx8 = OBX(
    obx_1_set_id=8,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?',
    obx_5_observation_value='N^No'
)

obx9 = OBX(
    obx_1_set_id=9,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-7^Is the patient pregnant?',
    obx_5_observation_value='N^No',
    obx_13_user_defined_access_checks='COVID-PT-5'
)


gt1 = GT1(
    gt1_1_set_id_gt1='',
    gt1_3_guarantor_name='DOE^JOHN^M',
    gt1_5_guarantor_address='1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US',
    gt1_6_guarantor_ph_num_home='(303)371-0073',
    gt1_7_guarantor_ph_num_business='',
    gt1_8_guarantor_datetime_of_birth='195208150000',
    gt1_9_guarantor_administrative_sex='F',
    gt1_11_guarantor_relationship='01'
)

gt2 = GT1(
    gt1_1_set_id_gt1='1',
    gt1_3_guarantor_name='Htrxtest^Test',
    gt1_5_guarantor_address='123 Main Ln.^^Allen^TX^75002',
    gt1_6_guarantor_ph_num_home='4699876521',
    gt1_7_guarantor_ph_num_business='',
    gt1_8_guarantor_datetime_of_birth='',
    gt1_9_guarantor_administrative_sex='M',
    gt1_11_guarantor_relationship='18'
)


obr = OBR(
    obr_1_set_id='1',
    obr_2_placer_order_number='NBT-000010139494',
    obr_4_universal_service_identifier='RESPI507^COVID-19 Test',
    obr_7_observation_datetime='202008051234',
    obr_15_specimen_source='^^^NASOPHARYNGEAL SWAB',
    obr_16_ordering_provider='1982044657^Ramirez^Diana^MD/PMEMR',
    obr_17_order_callback_phone_number='(561)360-2034',
    obr_21_filler_field_2='^^^^^^'
)

dg1 = DG1(
    dg1_1_set_id_dg1=1,
    dg1_3_diagnosis_code_dg1='I10^Essential (primary) hypertension'
)
'''


msh = MSH(
    msh_1_field_separator='|',
    msh_2_encoding_characters='^~\&',
    msh_3_sending_application='WELLHEALTH',
    msh_4_sending_facility='WELLHLTX',    #"For Client Bill MSH 4 will be ""WELLHLTX // For Insured or Unisured MSH 4 will be ""WELLHLD"" // If IN1 or GT1 are blank, mark as Self Pay"
    msh_5_receiving_application='AIT',
    msh_6_receiving_facility='AIT',
    msh_7_datetime_of_message=datetime.now().strftime("%Y%m%d%H%M%S"),
    msh_9_message_type='ORM^O01',
    msh_10_message_control_id=31705156,
    msh_11_processing_id='P',
    msh_12_version_id='2.3'
)

pid = PID(
    pid_1_set_id=1,
    pid_2_patient_id='475421', #External Code
    pid_3_patient_identifier_list='27927IN',
    pid_4_alternate_patient_id_pid='Test123IN',
    pid_5_patient_name='Chi^Angela^^^', #Last Name^First Name
    pid_7_date_time_of_birth='19900101', #Date of Birth
    pid_8_administrative_sex='M', #Gender
    pid_9_patient_alias='^',
    pid_10_race='2054-5', #Race
    pid_11_patient_address='123 Main Ln.^^Allen^TX^75002^^^^', #Address^Address2^City^State^Zip Code
    pid_12_county_code='',
    pid_13_phone_number_home='(469)987-6521', #Phone
    pid_18_patient_account_number='Test123^^^P',
    pid_19_ssn_number_patient='',
    pid_20_drivers_license_number_patient='',
    pid_22_ethnic_group='H' #Ethnicity
)

pv1 = PV1(
    pv1_1_set_id=1,
    pv1_3_assigned_patient_location='2',
    pv1_7_attending_doctor='1982044657^Ramirez^Diana^MD/PMEMR' #Physician NPI^Provider Last Name^Provider First name
)

in1 = IN1(
    in1_1_set_id=1,
    in1_3_insurance_company_id='MMP',
    in1_4_insurance_company_name='MEDICARE MASTER PAYER',
    in1_16_name_of_insured='DOE^JOHN^M',
    in1_17_insureds_relationship_to_patient='01',
    in1_18_insureds_date_of_birth='195208150000',
    in1_19_insureds_address='1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US',
    in1_22_coord_of_ben_priority='1',
    in1_32_billing_status='INSURANCE',
    in1_36_policy_number='8J89UD3HR59',
    in1_43_insureds_administrative_sex='F'

)

orc = ORC(
    orc_1_order_control = '',
    orc_2_placer_order_number = '', #Client Order Number^
    orc_3_filler_order_number = '', #Sample Code^Lab Vial Owner
    orc_4_placer_group_number = '',
    orc_5_order_status = '',
    orc_6_response_flag = '',
    orc_7_quantitytiming = '',
    orc_8_parent_order = '',
    orc_9_datetime_of_transaction = '', #Date of Collection
    orc_10_entered_by = '',
    orc_11_verified_by = '',
    orc_12_ordering_provider = '', #Physician NPI^Provider Last Name^Provider First name
)

gt1 = GT1(
    gt1_1_set_id_gt1='',
    gt1_3_guarantor_name='DOE^JOHN^M',
    gt1_5_guarantor_address='1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US',
    gt1_6_guarantor_ph_num_home='(303)371-0073',
    gt1_7_guarantor_ph_num_business='',
    gt1_8_guarantor_datetime_of_birth='195208150000',
    gt1_9_guarantor_administrative_sex='F',
    gt1_11_guarantor_relationship='01'
)

gt2 = GT1(
    gt1_1_set_id_gt1='1',
    gt1_3_guarantor_name='Htrxtest^Test',
    gt1_5_guarantor_address='123 Main Ln.^^Allen^TX^75002',
    gt1_6_guarantor_ph_num_home='4699876521',
    gt1_7_guarantor_ph_num_business='',
    gt1_8_guarantor_datetime_of_birth='',
    gt1_9_guarantor_administrative_sex='M',
    gt1_11_guarantor_relationship='18'
)


obr = OBR(
    obr_1_set_id='1',
    obr_2_placer_order_number='NBT-000010139494', #Client Order Number
    obr_3_filler_order_number='', #Sample Code^Lab Vial Owner
    obr_4_universal_service_identifier='RESPI507^COVID-19 Test', #Panel Code^Panel Name
    obr_6_requested_datetime='', #Date of Collection
    obr_7_observation_datetime='202008051234', #Date of Collection
    obr_15_specimen_source='^^^NASOPHARYNGEAL SWAB', #Sample Source
    obr_16_ordering_provider='1982044657^Ramirez^Diana^MD/PMEMR', #Physician NPI^Provider Last Name
    obr_17_order_callback_phone_number='(561)360-2034',
    obr_21_filler_field_2='^^^^^^'
)

dg1 = DG1(
    dg1_1_set_id_dg1=1,
    dg1_3_diagnosis_code_dg1='I10^Essential (primary) hypertension' #ICD Code
)

obx2 = OBX(
    obx_1_set_id=2,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-1^Is this the patient\'s first COVID-19 test?',
    obx_5_observation_value='U^Unknown'
)

obx3 = OBX(
    obx_1_set_id=3,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-2^Is the patient employed in healthcare with direct patient contact?',
    obx_5_observation_value='U^Unknown'
)

obx4 = OBX(
    obx_1_set_id=4,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?',
    obx_5_observation_value='Y^Yes'
)

obx5 = OBX(
    obx_1_set_id=5,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)',
    obx_5_observation_value='20200731'
)

obx6 = OBX(
    obx_1_set_id=6,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-4^Has the patient been hospalized?',
    obx_5_observation_value='N^No'
)

obx7 = OBX(
    obx_1_set_id=7,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-5^Has the patient been hospalized in the ICU?',
    obx_5_observation_value='N^No'
)
obx8 = OBX(
    obx_1_set_id=8,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?',
    obx_5_observation_value='N^No'
)

obx9 = OBX(
    obx_1_set_id=9,
    obx_2_value_type='ST',
    obx_3_observation_identifier='COVID-PT-7^Is the patient pregnant?',
    obx_5_observation_value='N^No',
    obx_13_user_defined_access_checks='COVID-PT-5'
)





'''
print(msh)
print(pid)
print(pv1)
print(in1)
print(gt1)
print(obr)
print(dg1)
print(obx2)
print(obx3)
print(obx4)
print(obx5)
print(obx6)
print(obx7)
print(obx8)
print(obx9)
'''



hl7_message = Message()
hl7_message.msh = msh
hl7_message.pid = pid
hl7_message.pv1 = pv1
hl7_message.in1 = in1
hl7_message.orc = orc
hl7_message.obr = obr
hl7_message.dg1 = dg1
hl7_message.obx_list = [obx2, obx3, obx4, obx5, obx6, obx7, obx8, obx9]
print(hl7_message)

'''

MSH|^~\&|DEMOFAC|DEMOFAC|AIT|AIT|20200805133511||ORM^O01|31705156|P|2.3
PID|1|27927IN|27927IN|Test123IN|Htrxtest^TestIN^^^||19900101|M|^|2054-5|123 Main Ln.^^Allen^TX^75002^^^^||(469)987-6521|||||Test123^^^P||||H
PV1|1||2||||1982044657^Ramirez^Diana^MD/PMEMR||||||||||1982044657^Ramirez^Diana^MD/PMEMR||
IN1|1||MMP|MEDICARE MASTER PAYER||||||||||||DOE^JOHN^M|01|195208150000|1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US|||1||||||||||INSURANCE||||8J89UD3HR59|||||||F||||||||
GT1|||DOE^JOHN^M||1700 ONION CREEK PARKWAY^^AUSTIN^TX^78748^US|(303)371-0073||195208150000|F||01|||||||||||||||||||||||||||||||||||||||||||||GT1|1||Htrxtest^Test||123 Main Ln.^^Allen^TX^75002|4699876521|||M||18
ORC|NW|NBT-000010139494|||||||202008051234|||1982044657^Ramirez^Diana^MD/PMEMR||
OBR|1|NBT-000010139494||RESPI507^COVID-19 Test|||202008051234||||||||^^^NASOPHARYNGEAL SWAB|1982044657^Ramirez^Diana^MD/PMEMR|(561)360-2034||||^^^^^^
DG1|1||I10^Essential (primary) hypertension
OBX|2|ST|COVID-PT-1^Is this the patient's first COVID-19 test?||U^Unknown||||||||
OBX|3|ST|COVID-PT-2^Is the patient employed in healthcare with direct patient contact?||U^Unknown||||||||
OBX|4|ST|COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?||Y^Yes||||||||
OBX|5|ST|COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)||20200731||||||||
OBX|6|ST|COVID-PT-4^Has the patient been hospalized?||N^No||||||||
OBX|7|ST|COVID-PT-5^Has the patient been hospalized in the ICU?||N^No||||||||COVID-PT-5
OBX|8|ST|COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?||N^No||||||||
OBX|9|ST|COVID-PT-7^Is the patient pregnant?||N^No||||||||
'''
