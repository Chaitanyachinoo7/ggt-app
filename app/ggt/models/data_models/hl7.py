from datetime import datetime
import time
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, constr
from pprint import pprint

'''
MSH|^~\&|WELLHEALTH|WELLHLD|AIT|AIT|20201215171758||ORM^O01|(1608070668,)|P|2.3|||||||||
PID|1|494800|||salguero^krystel^^^||11/24/1997|F||Unknown|2075 stillwater pl^^Lewisville^TX^75067^^^^||14695447901|||||494800^^^P||||2135-2|||||||||||||||||
PV1|1||||||1780944496^Khan^Samad|||||||||||||SP||||||||||||||||||||||||||||||||
ORC||594164|^||||||12/15/20|||1780944496^Khan^Samad|||||||||||||||||||
DG1|1||Z20.828^Contact with and (suspected) exposure to other viral communicable diseases||||||||||||||||||
OBR|1|594164|^|RESPI507^COVID-19 Test|||202008051234||||||||^^^NASOPHARYNGEAL SWAB|1982044657^Ramirez^Diana^MD/PMEMR|(561)360-2034||||^^^^^^|||||||||||||||||||||||||||||
OBX|2|ST|COVID-PT-1^Is this the patient's first COVID-19 test?||U^Unknown||||||||||||||||||||
OBX|3|ST|COVID-PT-2^Is the patient employed in healthcare with direct patient contact?||U^Unknown||||||||||||||||||||
OBX|4|ST|COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?||U^Unknown||||||||||||||||||||
OBX|5|ST|COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)||||||||||||||||||||||
OBX|6|ST|COVID-PT-4^Has the patient been hospalized?||U^Unknown||||||||||||||||||||
OBX|7|ST|COVID-PT-5^Has the patient been hospalized in the ICU?||U^Unknown||||||||||||||||||||
OBX|8|ST|COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?||U^Unknown||||||||||||||||||||
OBX|9|ST|COVID-PT-7^Is the patient pregnant?||U^Unknown||||||||||||||||||||

'''

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


class MSH(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/MSH
    msh_1_field_separator = ''
    msh_2_encoding_characters: constr(max_length=4)
    msh_3_sending_application: Optional[constr(max_length=227)] = ''
    msh_4_sending_facility: Optional[constr(max_length=227)] = ''
    msh_5_receiving_application: Optional[constr(max_length=227)] = ''
    msh_6_receiving_facility: Optional[constr(max_length=227)] = ''
    msh_7_datetime_of_message: constr(max_length=26)  # Timestamp
    msh_8_security: Optional[constr(max_length=40)] = ''
    msh_9_message_type: Optional[constr(max_length=15)] = ''
    msh_10_message_control_id: constr(max_length=20)
    msh_11_processing_id: constr(max_length=3)
    msh_12_version_id: constr(max_length=60)
    msh_13_sequence_number: Optional[constr(max_length=15)] = ''
    msh_14_continuation_pointer: Optional[constr(max_length=180)] = ''
    msh_15_accept_acknowledgment_type: Optional[constr(max_length=2)] = ''
    msh_16_application_acknowledgment_type: Optional[constr(
        max_length=2)] = ''
    msh_17_country_code: Optional[constr(max_length=3)] = ''
    msh_18_character_set: Optional[constr(max_length=16)] = ''
    msh_19_principal_language_of_message: Optional[constr(
        max_length=250)] = ''
    msh_20_alternate_character_set_handling_scheme: Optional[constr(
        max_length=20)] = ''
    msh_21_message_profile_identifier: Optional[constr(max_length=427)] = ''
    msh_22: Optional[constr(max_length=100)] = ''

    def __str__(self):
        return 'MSH|{}{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
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
    msg_1_message_code: constr(max_length=3)
    msg_2_trigger_event: constr(max_length=3)
    msg_3_message_structure: constr(max_length=7)

    def __str__(self):
        return '{}|{}|{}'.format(
            self.msg_1_message_code,
            self.msg_2_trigger_event,
            self.msg_3_message_structure
        )


class PID(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5.1/Segments/PID
    pid_1_set_id: \
        Optional[constr(max_length=4)] = ''
    pid_2_patient_id: \
        Optional[constr(max_length=20)] = ''
    pid_3_patient_identifier_list: \
        Optional[constr(max_length=250)]
    pid_4_alternate_patient_id_pid: \
        Optional[constr(max_length=20)] = ''
    pid_5_patient_name: \
        constr(max_length=250)
    pid_6_mothers_maiden_name: \
        Optional[constr(max_length=250)] = ''
    pid_7_date_time_of_birth: \
        Optional[constr(max_length=26)] = ''
    pid_8_administrative_sex: \
        Optional[constr(max_length=1)] = ''
    pid_9_patient_alias: \
        Optional[constr(max_length=250)] = ''
    pid_10_race: \
        Optional[constr(max_length=250)] = ''
    pid_11_patient_address: \
        Optional[constr(max_length=250)] = ''
    pid_12_county_code: \
        Optional[constr(max_length=4)] = ''
    pid_13_phone_number_home: \
        Optional[constr(max_length=250)] = ''
    pid_14_phone_number_business: \
        Optional[constr(max_length=250)] = ''
    pid_15_primary_language: \
        Optional[constr(max_length=250)] = ''
    pid_16_marital_status: \
        Optional[constr(max_length=250)] = ''
    pid_17_religion: \
        Optional[constr(max_length=250)] = ''
    pid_18_patient_account_number: \
        Optional[constr(max_length=250)] = ''
    pid_19_ssn_number_patient: \
        Optional[constr(max_length=16)] = ''
    pid_20_drivers_license_number_patient: \
        Optional[constr(max_length=25)] = ''
    pid_21_mothers_identifier: \
        Optional[constr(max_length=250)] = ''
    pid_22_ethnic_group: \
        Optional[constr(max_length=250)] = ''
    pid_23_birth_place: \
        Optional[constr(max_length=250)] = ''
    pid_24_multiple_birth_indicator: \
        Optional[constr(max_length=1)] = ''
    pid_25_birth_order: \
        Optional[constr(max_length=2)] = ''
    pid_26_citizenship: \
        Optional[constr(max_length=250)] = ''
    pid_27_veterans_military_status: \
        Optional[constr(max_length=250)] = ''
    pid_28_nationality: \
        Optional[constr(max_length=250)] = ''
    pid_29_patient_death_date_and_time: \
        Optional[constr(max_length=26)] = ''
    pid_30_patient_death_indicator: \
        Optional[constr(max_length=1)] = ''
    pid_31_identity_unknown_indicator: \
        Optional[constr(max_length=1)] = ''
    pid_32_identity_reliability_code: \
        Optional[constr(max_length=20)] = ''
    pid_33_last_update_datetime: \
        Optional[constr(max_length=26)] = ''
    pid_34_last_update_facility: \
        Optional[constr(max_length=241)] = ''
    pid_35_species_code: \
        Optional[constr(max_length=250)] = ''
    pid_36_breed_code: \
        Optional[constr(max_length=250)] = ''
    pid_37_strain: \
        Optional[constr(max_length=80)] = ''
    pid_38_production_class_code: \
        Optional[constr(max_length=250)] = ''
    pid_39_tribal_citizenship: \
        Optional[constr(max_length=250)] = ''

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
    in1_1_set_id: \
        constr(max_length=4)
    in1_2_insurance_plan_id: \
        constr(max_length=250) = ''
    in1_3_insurance_company_id: \
        constr(max_length=250)
    in1_4_insurance_company_name: \
        Optional[constr(max_length=250)] = ''
    in1_5_insurance_company_address: \
        Optional[constr(max_length=250)] = ''
    in1_6_insurance_co_contact_person: \
        Optional[constr(max_length=250)] = ''
    in1_7_insurance_co_phone_number: \
        Optional[constr(max_length=250)] = ''
    in1_8_group_number: \
        Optional[constr(max_length=12)] = ''
    in1_9_group_name: \
        Optional[constr(max_length=250)] = ''
    in1_10_insureds_group_emp_id: \
        Optional[constr(max_length=250)] = ''
    in1_11_insureds_group_emp_name: \
        Optional[constr(max_length=250)] = ''
    in1_12_plan_effective_date: \
        Optional[constr(max_length=8)] = ''
    in1_13_plan_expiration_date: \
        Optional[constr(max_length=8)] = ''
    in1_14_authorization_information: \
        Optional[constr(max_length=239)] = ''
    in1_15_plan_type: \
        Optional[constr(max_length=3)] = ''
    in1_16_name_of_insured: \
        Optional[constr(max_length=250)] = ''
    in1_17_insureds_relationship_to_patient: \
        Optional[constr(max_length=250)] = ''
    in1_18_insureds_date_of_birth: \
        Optional[constr(max_length=26)] = ''
    in1_19_insureds_address: \
        Optional[constr(max_length=250)] = ''
    in1_20_assignment_of_benefits: \
        Optional[constr(max_length=2)] = ''
    in1_21_coordination_of_benefits: \
        Optional[constr(max_length=2)] = ''
    in1_22_coord_of_ben_priority: \
        Optional[constr(max_length=2)] = ''
    in1_23_notice_of_admission_flag: \
        Optional[constr(max_length=1)] = ''
    in1_24_notice_of_admission_date: \
        Optional[constr(max_length=8)] = ''
    in1_25_report_of_eligibility_flag: \
        Optional[constr(max_length=1)] = ''
    in1_26_report_of_eligibility_date: \
        Optional[constr(max_length=8)] = ''
    in1_27_release_information_code: \
        Optional[constr(max_length=2)] = ''
    in1_28_pre_admit_cert_pac: \
        Optional[constr(max_length=15)] = ''
    in1_29_verification_datetime: \
        Optional[constr(max_length=26)] = ''
    in1_30_verification_by: \
        Optional[constr(max_length=250)] = ''
    in1_31_type_of_agreement_code: \
        Optional[constr(max_length=2)] = ''
    in1_32_billing_status: \
        Optional[str] = ''
    in1_33_lifetime_reserve_days: \
        Optional[constr(max_length=4)] = ''
    in1_34_delay_before_l_r_day: \
        Optional[constr(max_length=4)] = ''
    in1_35_company_plan_code: \
        Optional[constr(max_length=8)] = ''
    in1_36_policy_number: \
        Optional[constr(max_length=15)] = ''
    in1_37_policy_deductible: \
        Optional[constr(max_length=12)] = ''
    in1_38_policy_limit_amount: \
        Optional[constr(max_length=12)] = ''
    in1_39_policy_limit_days: \
        Optional[constr(max_length=4)] = ''
    in1_40_room_rate_semi_private: \
        Optional[constr(max_length=12)] = ''
    in1_41_room_rate_private: \
        Optional[constr(max_length=12)] = ''
    in1_42_insureds_employment_status: \
        Optional[constr(max_length=250)] = ''
    in1_43_insureds_administrative_sex: \
        Optional[constr(max_length=1)] = ''
    in1_44_insureds_employers_address: \
        Optional[constr(max_length=250)] = ''
    in1_45_verification_status: \
        Optional[constr(max_length=2)] = ''
    in1_46_prior_insurance_plan_id: \
        Optional[constr(max_length=8)] = ''
    in1_47_coverage_type: \
        Optional[constr(max_length=3)] = ''
    in1_48_handicap: \
        Optional[constr(max_length=2)] = ''
    in1_49_insureds_id_number: \
        Optional[constr(max_length=250)] = ''
    in1_50_signature_code: \
        Optional[constr(max_length=1)] = ''
    in1_51_signature_code_date: \
        Optional[constr(max_length=8)] = ''
    in1_52_insureds_birth_place: \
        Optional[constr(max_length=250)] = ''
    in1_53_vip_indicator: \
        Optional[constr(max_length=2)] = ''

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
    pv1_1_set_id: \
        Optional[constr(max_length=4)] = ''
    pv1_2_patient_class: \
        constr(max_length=1) = ''
    pv1_3_assigned_patient_location: \
        Optional[constr(max_length=80)] = ''
    pv1_4_admission_type: \
        Optional[constr(max_length=2)] = ''
    pv1_5_preadmit_number: \
        Optional[constr(max_length=250)] = ''
    pv1_6_prior_patient_location: \
        Optional[constr(max_length=80)] = ''
    pv1_7_attending_doctor: \
        Optional[constr(max_length=250)] = ''
    pv1_8_referring_doctor: \
        Optional[constr(max_length=250)] = ''
    pv1_9_consulting_doctor: \
        Optional[constr(max_length=250)] = ''
    pv1_10_hospital_service: \
        Optional[constr(max_length=3)] = ''
    pv1_11_temporary_location: \
        Optional[constr(max_length=80)] = ''
    pv1_12_preadmit_test_indicator: \
        Optional[constr(max_length=2)] = ''
    pv1_13_re_admission_indicator: \
        Optional[constr(max_length=2)] = ''
    pv1_14_admit_source: \
        Optional[constr(max_length=6)] = ''
    pv1_15_ambulatory_status: \
        Optional[constr(max_length=2)] = ''
    pv1_16_vip_indicator: \
        Optional[constr(max_length=2)] = ''
    pv1_17_admitting_doctor: \
        Optional[constr(max_length=250)] = ''
    pv1_18_patient_type: \
        Optional[constr(max_length=2)] = ''
    pv1_19_visit_number: \
        Optional[constr(max_length=250)] = ''
    pv1_20_financial_class: \
        Optional[constr(max_length=50)] = ''
    pv1_21_charge_price_indicator: \
        Optional[constr(max_length=2)] = ''
    pv1_22_courtesy_code: \
        Optional[constr(max_length=2)] = ''
    pv1_23_credit_rating: \
        Optional[constr(max_length=2)] = ''
    pv1_24_contract_code: \
        Optional[constr(max_length=2)] = ''
    pv1_25_contract_effective_date: \
        Optional[constr(max_length=8)] = ''
    pv1_26_contract_amount: \
        Optional[constr(max_length=12)] = ''
    pv1_27_contract_period: \
        Optional[constr(max_length=3)] = ''
    pv1_28_interest_code: \
        Optional[constr(max_length=2)] = ''
    pv1_29_transfer_to_bad_debt_code: \
        Optional[constr(max_length=4)] = ''
    pv1_30_transfer_to_bad_debt_date: \
        Optional[constr(max_length=8)] = ''
    pv1_31_bad_debt_agency_code: \
        Optional[constr(max_length=10)] = ''
    pv1_32_bad_debt_transfer_amount: \
        Optional[constr(max_length=12)] = ''
    pv1_33_bad_debt_recovery_amount: \
        Optional[constr(max_length=12)] = ''
    pv1_34_delete_account_indicator: \
        Optional[constr(max_length=1)] = ''
    pv1_35_delete_account_date: \
        Optional[constr(max_length=8)] = ''
    pv1_36_discharge_disposition: \
        Optional[constr(max_length=3)] = ''
    pv1_37_discharged_to_location: \
        Optional[constr(max_length=47)] = ''
    pv1_38_diet_type: \
        Optional[constr(max_length=250)] = ''
    pv1_39_servicing_facility: \
        Optional[constr(max_length=2)] = ''
    pv1_40_bed_status: \
        Optional[constr(max_length=1)] = ''
    pv1_41_account_status: \
        Optional[constr(max_length=2)] = ''
    pv1_42_pending_location: \
        Optional[constr(max_length=80)] = ''
    pv1_43_prior_temporary_location: \
        Optional[constr(max_length=80)] = ''
    pv1_44_admit_datetime: \
        Optional[constr(max_length=26)] = ''
    pv1_45_discharge_datetime: \
        Optional[constr(max_length=26)] = ''
    pv1_46_current_patient_balance: \
        Optional[constr(max_length=12)] = ''
    pv1_47_total_charges: \
        Optional[constr(max_length=12)] = ''
    pv1_48_total_adjustments: \
        Optional[constr(max_length=12)] = ''
    pv1_49_total_payments: \
        Optional[constr(max_length=12)] = ''
    pv1_50_alternate_visit_id: \
        Optional[constr(max_length=250)] = ''
    pv1_51_visit_indicator: \
        Optional[constr(max_length=1)] = ''
    pv1_52_other_healthcare_provider: \
        Optional[constr(max_length=250)] = ''

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
    obx_1_set_id: \
        Optional[constr(max_length=4)] = ''
    obx_2_value_type: \
        Optional[constr(max_length=2)] = ''
    obx_3_observation_identifier: \
        constr(max_length=250)
    obx_4_observation_sub_id: \
        Optional[constr(max_length=20)] = ''
    obx_5_observation_value: Optional[str] = ''
    obx_6_units: \
        Optional[constr(max_length=250)] = ''
    obx_7_references_range: \
        Optional[constr(max_length=60)] = ''
    obx_8_abnormal_flags: \
        Optional[constr(max_length=5)] = ''
    obx_9_probability: \
        Optional[constr(max_length=5)] = ''
    obx_10_nature_of_abnormal_test: \
        Optional[constr(max_length=2)] = ''
    obx_11_observation_result_status: \
        Optional[constr(max_length=1)] = ''
    obx_12_effective_date_of_reference_range: \
        Optional[constr(max_length=26)] = ''
    obx_13_user_defined_access_checks: \
        Optional[constr(max_length=20)] = ''
    obx_14_datetime_of_the_observation: \
        Optional[constr(max_length=26)] = ''
    obx_15_producers_id: \
        Optional[constr(max_length=250)] = ''
    obx_16_responsible_observer: \
        Optional[constr(max_length=250)] = ''
    obx_17_observation_method: \
        Optional[constr(max_length=250)] = ''
    obx_18_equipment_instance_identifier: \
        Optional[constr(max_length=22)] = ''
    obx_19_datetime_of_the_analysis: \
        Optional[constr(max_length=26)] = ''
    obx_20_reserved_for_harmonization_with_v2_6: \
        Optional[constr(max_length=0)] = ''
    obx_21_reserved_for_harmonization_with_v2_6: \
        Optional[constr(max_length=0)] = ''
    obx_22_reserved_for_harmonization_with_v2_6: \
        Optional[constr(max_length=0)] = ''
    obx_23_performing_organization_name: \
        Optional[constr(max_length=567)] = ''
    obx_24_performing_organization_address: \
        Optional[constr(max_length=631)] = ''
    obx_25_performing_organization_medical_director: \
        Optional[constr(max_length=3002)] = ''

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
    gt1_1_set_id_gt1: \
        constr(max_length=4)
    gt1_2_guarantor_number: \
        Optional[constr(max_length=250)] = ''
    gt1_3_guarantor_name: \
        constr(max_length=250)
    gt1_4_guarantor_spouse_name: \
        Optional[constr(max_length=250)] = ''
    gt1_5_guarantor_address: \
        Optional[constr(max_length=250)] = ''
    gt1_6_guarantor_ph_num_home: \
        Optional[constr(max_length=250)] = ''
    gt1_7_guarantor_ph_num_business: \
        Optional[constr(max_length=250)] = ''
    gt1_8_guarantor_datetime_of_birth: \
        Optional[constr(max_length=26)] = ''
    gt1_9_guarantor_administrative_sex: \
        Optional[constr(max_length=1)] = ''
    gt1_10_guarantor_type: \
        Optional[constr(max_length=2)] = ''
    gt1_11_guarantor_relationship: \
        Optional[constr(max_length=250)] = ''
    gt1_12_guarantor_ssn: \
        Optional[constr(max_length=11)] = ''
    gt1_13_guarantor_date_begin: \
        Optional[constr(max_length=8)] = ''
    gt1_14_guarantor_date_end: \
        Optional[constr(max_length=8)] = ''
    gt1_15_guarantor_priority: \
        Optional[constr(max_length=2)] = ''
    gt1_16_guarantor_employer_name: \
        Optional[constr(max_length=250)] = ''
    gt1_17_guarantor_employer_address: \
        Optional[constr(max_length=250)] = ''
    gt1_18_guarantor_employer_phone_number: \
        Optional[constr(max_length=250)] = ''
    gt1_19_guarantor_employee_id_number: \
        Optional[constr(max_length=250)] = ''
    gt1_20_guarantor_employment_status: \
        Optional[constr(max_length=2)] = ''
    gt1_21_guarantor_organization_name: \
        Optional[constr(max_length=250)] = ''
    gt1_22_guarantor_billing_hold_flag: \
        Optional[constr(max_length=1)] = ''
    gt1_23_guarantor_credit_rating_code: \
        Optional[constr(max_length=250)] = ''
    gt1_24_guarantor_death_date_and_time: \
        Optional[constr(max_length=26)] = ''
    gt1_25_guarantor_death_flag: \
        Optional[constr(max_length=1)] = ''
    gt1_26_guarantor_charge_adjustment_code: \
        Optional[constr(max_length=250)] = ''
    gt1_27_guarantor_household_annual_income: \
        Optional[constr(max_length=10)] = ''
    gt1_28_guarantor_household_size: \
        Optional[constr(max_length=3)] = ''
    gt1_29_guarantor_employer_id_number: \
        Optional[constr(max_length=250)] = ''
    gt1_30_guarantor_marital_status_code: \
        Optional[constr(max_length=250)] = ''
    gt1_31_guarantor_hire_effective_date: \
        Optional[constr(max_length=8)] = ''
    gt1_32_employment_stop_date: \
        Optional[constr(max_length=8)] = ''
    gt1_33_living_dependency: \
        Optional[constr(max_length=2)] = ''
    gt1_34_ambulatory_status: \
        Optional[constr(max_length=2)] = ''
    gt1_35_citizenship: \
        Optional[constr(max_length=250)] = ''
    gt1_36_primary_language: \
        Optional[constr(max_length=250)] = ''
    gt1_37_living_arrangement: \
        Optional[constr(max_length=2)] = ''
    gt1_38_publicity_code: \
        Optional[constr(max_length=250)] = ''
    gt1_39_protection_indicator: \
        Optional[constr(max_length=1)] = ''
    gt1_40_student_indicator: \
        Optional[constr(max_length=2)] = ''
    gt1_41_religion: \
        Optional[constr(max_length=250)] = ''
    gt1_42_mothers_maiden_name: \
        Optional[constr(max_length=250)] = ''
    gt1_43_nationality: \
        Optional[constr(max_length=250)] = ''
    gt1_44_ethnic_group: \
        Optional[constr(max_length=250)] = ''
    gt1_45_contact_persons_name: \
        Optional[constr(max_length=250)] = ''
    gt1_46_contact_persons_telephone_number: \
        Optional[constr(max_length=250)] = ''
    gt1_47_contact_reason: \
        Optional[constr(max_length=250)] = ''
    gt1_48_contact_relationship: \
        Optional[constr(max_length=3)] = ''
    gt1_49_job_title: \
        Optional[constr(max_length=20)] = ''
    gt1_50_job_code_class: \
        Optional[constr(max_length=20)] = ''
    gt1_51_guarantor_employers_organization_name: \
        Optional[constr(max_length=250)] = ''
    gt1_52_handicap: \
        Optional[constr(max_length=2)] = ''
    gt1_53_job_status: \
        Optional[constr(max_length=2)] = ''
    gt1_54_guarantor_financial_class: \
        Optional[constr(max_length=50)] = ''
    gt1_55_guarantor_race: \
        Optional[constr(max_length=250)] = ''
    gt1_56_guarantor_birth_place: \
        Optional[constr(max_length=250)] = ''
    gt1_57_vip_indicator: \
        Optional[constr(max_length=2)] = ''

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
    obr_1_set_id: \
        Optional[constr(max_length=4)] = ''
    obr_2_placer_order_number: \
        Optional[constr(max_length=22)] = ''
    obr_3_filler_order_number = ''
    obr_4_universal_service_identifier: \
        constr(max_length=250)
    obr_5_priority_obr: \
        Optional[constr(max_length=2)] = ''
    obr_6_requested_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_7_observation_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_8_observation_end_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_9_collection_volume: \
        Optional[constr(max_length=20)] = ''
    obr_10_collector_identifier: \
        Optional[constr(max_length=250)] = ''
    obr_11_specimen_action_code: \
        Optional[constr(max_length=1)] = ''
    obr_12_danger_code: \
        Optional[constr(max_length=250)] = ''
    obr_13_relevant_clinical_information: \
        Optional[constr(max_length=300)] = ''
    obr_14_specimen_received_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_15_specimen_source: \
        Optional[constr(max_length=300)] = ''
    obr_16_ordering_provider: \
        Optional[constr(max_length=250)] = ''
    obr_17_order_callback_phone_number: \
        Optional[constr(max_length=250)] = ''
    obr_18_placer_field_1: \
        Optional[constr(max_length=60)] = ''
    obr_19_placer_field_2: \
        Optional[constr(max_length=60)] = ''
    obr_20_filler_field_1: \
        Optional[constr(max_length=60)] = ''
    obr_21_filler_field_2: \
        Optional[constr(max_length=60)] = ''
    obr_22_results_rpt_status_chng_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_23_charge_to_practice: \
        Optional[constr(max_length=40)] = ''
    obr_24_diagnostic_serv_sect_id: \
        Optional[constr(max_length=10)] = ''
    obr_25_result_status: \
        Optional[constr(max_length=1)] = ''
    obr_26_parent_result: \
        Optional[constr(max_length=400)] = ''
    obr_27_quantity_timing: \
        Optional[constr(max_length=200)] = ''
    obr_28_result_copies_to: \
        Optional[constr(max_length=250)] = ''
    obr_29_parent: \
        Optional[constr(max_length=200)] = ''
    obr_30_transportation_mode: \
        Optional[constr(max_length=20)] = ''
    obr_31_reason_for_study: \
        Optional[constr(max_length=250)] = ''
    obr_32_principal_result_interpreter: \
        Optional[constr(max_length=200)] = ''
    obr_33_assistant_result_interpreter: \
        Optional[constr(max_length=200)] = ''
    obr_34_technician: \
        Optional[constr(max_length=200)] = ''
    obr_35_transcriptionist: \
        Optional[constr(max_length=200)] = ''
    obr_36_scheduled_datetime: \
        Optional[constr(max_length=26)] = ''
    obr_37_number_of_sample_containers: \
        Optional[constr(max_length=4)] = ''
    obr_38_transport_logistics_of_collected_sample: \
        Optional[constr(max_length=250)] = ''
    obr_39_collectors_comment: \
        Optional[constr(max_length=250)] = ''
    obr_40_transport_arrangement_responsibility: \
        Optional[constr(max_length=250)] = ''
    obr_41_transport_arranged: \
        Optional[constr(max_length=30)] = ''
    obr_42_escort_required: \
        Optional[constr(max_length=1)] = ''
    obr_43_planned_patient_transport_comment: \
        Optional[constr(max_length=250)] = ''
    obr_44_procedure_code: \
        Optional[constr(max_length=250)] = ''
    obr_45_procedure_code_modifier: \
        Optional[constr(max_length=250)] = ''
    obr_46_placer_supplemental_service_information: \
        Optional[constr(max_length=250)] = ''
    obr_47_filler_supplemental_service_information: \
        Optional[constr(max_length=250)] = ''
    obr_48_medically_necessary_duplicate_procedure_reason_: \
        Optional[constr(max_length=250)] = ''
    obr_49_result_handling: \
        Optional[constr(max_length=2)] = ''
    obr_50_parent_universal_service_identifier: \
        Optional[constr(max_length=250)] = ''

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
    dg1_1_set_id_dg1: \
        constr(max_length=4)
    dg1_2_diagnosis_coding_method: \
        Optional[constr(max_length=2)] = ''
    dg1_3_diagnosis_code_dg1: \
        Optional[constr(max_length=250)] = ''
    dg1_4_diagnosis_description: \
        Optional[constr(max_length=40)] = ''
    dg1_5_diagnosis_datetime: \
        Optional[constr(max_length=26)] = ''
    dg1_6_diagnosis_type: \
        constr(max_length=2) = ''
    dg1_7_major_diagnostic_category: \
        Optional[constr(max_length=250)] = ''
    dg1_8_diagnostic_related_group: \
        Optional[constr(max_length=250)] = ''
    dg1_9_drg_approval_indicator: \
        Optional[constr(max_length=1)] = ''
    dg1_10_drg_grouper_review_code: \
        Optional[constr(max_length=2)] = ''
    dg1_11_outlier_type: \
        Optional[constr(max_length=250)] = ''
    dg1_12_outlier_days: \
        Optional[constr(max_length=3)] = ''
    dg1_13_outlier_cost: \
        Optional[constr(max_length=12)] = ''
    dg1_14_grouper_version_and_type: \
        Optional[constr(max_length=4)] = ''
    dg1_15_diagnosis_priority: \
        Optional[constr(max_length=2)] = ''
    dg1_16_diagnosing_clinician: \
        Optional[constr(max_length=250)] = ''
    dg1_17_diagnosis_classification: \
        Optional[constr(max_length=3)] = ''
    dg1_18_confidential_indicator: \
        Optional[constr(max_length=1)] = ''
    dg1_19_attestation_datetime: \
        Optional[constr(max_length=26)] = ''
    dg1_20_diagnosis_identifier: \
        Optional[constr(max_length=427)] = ''
    dg1_21_diagnosis_action_code: \
        Optional[constr(max_length=1)] = ''

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
    orc_1_order_control: \
        Optional[constr(max_length=2)] = ''
    orc_2_placer_order_number: \
        Optional[constr(max_length=22)] = ''
    orc_3_filler_order_number = ''
    orc_4_placer_group_number: \
        Optional[constr(max_length=22)] = ''
    orc_5_order_status: \
        Optional[constr(max_length=2)] = ''
    orc_6_response_flag: \
        Optional[constr(max_length=1)] = ''
    orc_7_quantitytiming: \
        Optional[constr(max_length=200)] = ''
    orc_8_parent_order: \
        Optional[constr(max_length=200)] = ''
    orc_9_datetime_of_transaction: \
        Optional[constr(max_length=26)] = ''
    orc_10_entered_by: \
        Optional[constr(max_length=250)] = ''
    orc_11_verified_by: \
        Optional[constr(max_length=250)] = ''
    orc_12_ordering_provider: \
        Optional[constr(max_length=250)] = ''
    orc_13_enterers_location: \
        Optional[constr(max_length=80)] = ''
    orc_14_call_back_phone_number: \
        Optional[constr(max_length=250)] = ''
    orc_15_order_effective_datetime: \
        Optional[constr(max_length=26)] = ''
    orc_16_order_control_code_reason: \
        Optional[constr(max_length=250)] = ''
    orc_17_entering_organization: \
        Optional[constr(max_length=250)] = ''
    orc_18_entering_device: \
        Optional[constr(max_length=250)] = ''
    orc_19_action_by: \
        Optional[constr(max_length=250)] = ''
    orc_20_advanced_beneficiary_notice_code: \
        Optional[constr(max_length=250)] = ''
    orc_21_ordering_facility_name: \
        Optional[constr(max_length=250)] = ''
    orc_22_ordering_facility_address: \
        Optional[constr(max_length=250)] = ''
    orc_23_ordering_facility_phone_number: \
        Optional[constr(max_length=250)] = ''
    orc_24_ordering_provider_address: \
        Optional[constr(max_length=250)] = ''
    orc_25_order_status_modifier: \
        Optional[constr(max_length=250)] = ''
    orc_26_advanced_beneficiary_notice_override_reason: \
        Optional[constr(max_length=60)] = ''
    orc_27_fillers_expected_availability_datetime: \
        Optional[constr(max_length=26)] = ''
    orc_28_confidentiality_code: \
        Optional[constr(max_length=250)] = ''
    orc_29_order_type: \
        Optional[constr(max_length=250)] = ''
    orc_30_enterer_authorization_mode: \
        Optional[constr(max_length=250)] = ''
    orc_31_parent_universal_service_identifier: \
        Optional[constr(max_length=250)] = ''

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


class RXA(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5/Segments/RXA
    rxa_1_give_sub_id_counter = ''
    rxa_2_administration_sub_id_counter = ''
    rxa_3_date_time_start_of_administration = ''
    rxa_4_date_time_end_of_administration = ''
    rxa_5_administered_code = ''
    rxa_6_administered_amount = ''
    rxa_7_administered_units = ''
    rxa_8_administered_dosage_form = ''
    rxa_9_administration_notes = ''
    rxa_10_administering_provider = ''
    rxa_11_administered_at_location = ''
    rxa_12_administered_per_time_unit = ''
    rxa_13_administered_strength = ''
    rxa_14_administered_strength_units = ''
    rxa_15_substance_lot_number = ''
    rxa_16_substance_expiration_date = ''
    rxa_17_substance_manufacturer_name = ''
    rxa_18_substance_treatment_refusal_reason = ''
    rxa_19_indication = ''
    rxa_20_completion_status = ''
    rxa_21_action_code_rxa = ''
    rxa_22_system_entry_date_time = ''
    rxa_23_administered_drug_strength_volume = ''
    rxa_24_administered_drug_strength_volume_units = ''
    rxa_25_administered_barcode_identifier = ''
    rxa_26_pharmacy_order_type = ''

    def __str__(self):
        return 'RXA|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.rxa_1_give_sub_id_counter,
            self.rxa_2_administration_sub_id_counter,
            self.rxa_3_date_time_start_of_administration,
            self.rxa_4_date_time_end_of_administration,
            self.rxa_5_administered_code,
            self.rxa_6_administered_amount,
            self.rxa_7_administered_units,
            self.rxa_8_administered_dosage_form,
            self.rxa_9_administration_notes,
            self.rxa_10_administering_provider,
            self.rxa_11_administered_at_location,
            self.rxa_12_administered_per_time_unit,
            self.rxa_13_administered_strength,
            self.rxa_14_administered_strength_units,
            self.rxa_15_substance_lot_number,
            self.rxa_16_substance_expiration_date,
            self.rxa_17_substance_manufacturer_name,
            self.rxa_18_substance_treatment_refusal_reason,
            self.rxa_19_indication,
            self.rxa_20_completion_status,
            self.rxa_21_action_code_rxa,
            self.rxa_22_system_entry_date_time,
            self.rxa_23_administered_drug_strength_volume,
            self.rxa_24_administered_drug_strength_volume_units,
            self.rxa_25_administered_barcode_identifier,
            self.rxa_26_pharmacy_order_type
        )


class RXR(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5/Segments/RXR
    rxr_1_route = ''
    rxr_2_administration_site = ''
    rxr_3_administration_device = ''
    rxr_4_administration_method = ''
    rxr_5_routing_instruction = ''
    rxr_6_administration_site_modifier = ''

    def __str__(self):
        return 'RXR|{}|{}|{}|{}|{}|{}'.format(
            self.rxr_1_route,
            self.rxr_2_administration_site,
            self.rxr_3_administration_device,
            self.rxr_4_administration_method,
            self.rxr_5_routing_instruction,
            self.rxr_6_administration_site_modifier
        )


class PD1(BaseModel):
    # https://hl7-definition.caristix.com/v2/HL7v2.5/Segments/PD1
    pd1_1_living_dependency = ''
    pd1_2_living_arrangement = ''
    pd1_3_patient_primary_facility = ''
    pd1_4_patient_primary_care_provider_name_and_id_no = ''
    pd1_5_student_indicator = ''
    pd1_6_handicap = ''
    pd1_7_living_will_code = ''
    pd1_8_organ_donor_code = ''
    pd1_9_separate_bill = ''
    pd1_10_duplicate_patient = ''
    pd1_11_publicity_code = ''
    pd1_12_protection_indicator = ''
    pd1_13_protection_indicator_effective_date = ''
    pd1_14_place_of_worship = ''
    pd1_15_advance_directive_code = ''
    pd1_16_immunization_registry_status = ''
    pd1_17_immunization_registry_status_effective_date = ''
    pd1_18_publicity_code_effective_date = ''
    pd1_19_military_branch = ''
    pd1_20_military_rank_grade = ''
    pd1_21_military_status = ''

    def __str__(self):
        return 'PD1|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
            self.pd1_1_living_dependency,
            self.pd1_2_living_arrangement,
            self.pd1_3_patient_primary_facility,
            self.pd1_4_patient_primary_care_provider_name_and_id_no,
            self.pd1_5_student_indicator,
            self.pd1_6_handicap,
            self.pd1_7_living_will_code,
            self.pd1_8_organ_donor_code,
            self.pd1_9_separate_bill,
            self.pd1_10_duplicate_patient,
            self.pd1_11_publicity_code,
            self.pd1_12_protection_indicator,
            self.pd1_13_protection_indicator_effective_date,
            self.pd1_14_place_of_worship,
            self.pd1_15_advance_directive_code,
            self.pd1_16_immunization_registry_status,
            self.pd1_17_immunization_registry_status_effective_date,
            self.pd1_18_publicity_code_effective_date,
            self.pd1_19_military_branch,
            self.pd1_20_military_rank_grade,
            self.pd1_21_military_status
        )


class Message(BaseModel):
    msh: MSH = ''
    pid: Optional[PID] = ''
    pv1: Optional[PV1] = ''
    gt1: Optional[GT1] = ''
    in1: Optional[IN1] = ''
    dg1: Optional[DG1] = ''
    orc: Optional[ORC] = ''
    obr: Optional[OBR] = ''
    obx_list: Optional[List[OBX]] = ''

    def __str__(self):
        _str = ''
        for obx in self.obx_list:
            _str = _str + str(obx) + '\n'

        return '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
            str(self.msh),
            str(self.pid),
            str(self.pv1),
            str(self.gt1),
            str(self.dg1),
            str(self.orc),
            str(self.obr),
            _str
        ).replace('None', '').replace('\n\n', '\n').replace('\n\n', '\n').replace('b\'', '').replace('\'|', '|')


class VaxMessage(BaseModel):
    msh: MSH = ''
    pid: Optional[PID] = ''
    orc: Optional[ORC] = ''
    pd1: Optional[PD1] = ''
    rxr: Optional[RXR] = ''
    rxa: Optional[RXA] = ''
    obx_list: Optional[List[OBX]] = ''

    def __str__(self):
        _str = ''

        for obx in self.obx_list:
            _str = _str + str(obx) + '\n'

        return '{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
            str(self.msh),
            str(self.pid),
            str(self.pd1),
            str(self.orc),            
            str(self.rxa),
            str(self.rxr),
            _str
        ).replace('None', '').replace('\n\n', '\n').replace('\n\n', '\n').replace('b\'', '').replace('\'|', '|')
