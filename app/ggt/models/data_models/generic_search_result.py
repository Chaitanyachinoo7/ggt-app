from pydantic import BaseModel
from typing import Dict, List, Optional

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)


########################################################################################################
# [Public] functions
########################################################################################################

class PatientDetails(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    dob: str


class PatientVitals(BaseModel):
    height: str
    weight: str
    medications: bool


class PatientDemographics(BaseModel):
    gender: str
    race: str
    ethnicity: str


class PatientAddress(BaseModel):
    addr1: str
    addr2: str
    city: str
    st: str
    zip_code: str


class PatientContactInfo(BaseModel):
    email: str
    email_verified: bool
    phone_number: str
    phone_verified: bool


class PreExistingConditions(BaseModel):
    heart_disease: bool
    diabetes: bool
    respiratory_disease: bool
    autoimmune_disease: bool
    other_chronic_disease: bool
    allergies: bool


class Symptoms(BaseModel):
    symptom_fever: bool
    symptom_short_breath: bool
    symptom_cough: bool
    symptom_chest_pains: bool
    symptom_other: bool
    symptom_lack_of_smell_taste: bool
    covid_contact: bool


class BillingInfo(BaseModel):
    total_amount: str
    insurance_billed: str
    client_billed: str
    patient_billed: str
    insurance_photo: str


class Activity(BaseModel):
    activity_type: str
    activity_dt: str
    details: str


class ActivityList(BaseModel):
    activity_list: List[Activity] = None


class TestLocation(BaseModel):
    id: str
    site_code: str
    group_code: str
    acount: str
    addr1: str
    addr2: str
    addr3: str
    city: str
    st: str
    zip: str
    time_zone: str
    test_offered: str


class ClinicalProvider(BaseModel):
    id: str
    first_name: str
    last_name: str


class TestSample(BaseModel):
    test_id: str
    clinical_provider: Optional[ClinicalProvider] = None
    sample_collection_dt: str
    lab_submission_dt: str
    lab_result_receive_dt: str
    test_result: str
    status: str


class Appointment(BaseModel):
    appointment_id: str
    scheduled_dt: str
    test_ocation: TestLocation


class GenericSearchResult(BaseModel):
    details: PatientDetails
    demographics: PatientDemographics
    address: PatientAddress
    contact: PatientContactInfo
    vitals: PatientVitals
    pre_existing_conditions: PreExistingConditions
    symptoms: Symptoms
    billing_info: BillingInfo


class GenericSearchResults(BaseModel):
    search_results: Optional[GenericSearchResult] = None


def find_patients(first_name='', middle_name='', last_name='', dob='', phone_number='',
                  email='', appointment_id='', group_code='', appointment_date='', location_id=''):
    try:
        where_conditions = ''
        if first_name != '':
            where_conditions = "{} AND p.first_name LIKE '%{}%'".format(
                where_conditions, first_name)
        if middle_name != '':
            where_conditions = "{} AND p.middle_name LIKE '%{}%'".format(
                where_conditions, middle_name)
        if last_name != '':
            where_conditions = "{} AND p.last_name LIKE '%{}%'".format(
                where_conditions, last_name)
        if dob != '':
            where_conditions = "{} AND p.dob = '{}'".format(
                where_conditions, dob)
        if phone_number != '':
            where_conditions = "{} AND p.phone_number LIKE '%{}%'".format(
                where_conditions, phone_number)
        if email != '':
            where_conditions = "{} AND p.email LIKE '%{}%'".format(
                where_conditions, email)
        if appointment_id != '':
            where_conditions = "{} AND a.id = '{}'".format(
                where_conditions, appointment_id)
        if group_code != '':
            where_conditions = "{} AND a.group_code LIKE '%{}%'".format(
                where_conditions, group_code)
        if appointment_date != '':
            where_conditions = "{} AND DATE(a.scheduled_dt) = '{}'".format(
                where_conditions, appointment_date)
        if location_id != '':
            where_conditions = "{} AND a.location_id = '{}'".format(
                where_conditions, location_id)

        limit = 250

        sql = """
        SELECT 
              p.id AS patient_id,
            p.first_name AS first_name,
            p.middle_name AS middle_name,
            p.last_name AS last_name,
            p.gender AS gender,
            p.height_ft AS height_ft,
            p.height_in AS height_in,
            p.weight_lb AS weight_lb,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
                WHEN (p.race = 'race_asian') THEN 'Asian'
                WHEN (p.race = 'race_black') THEN 'Black or African American'
                WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
                WHEN (p.race = 'race_other') THEN 'Other'
                WHEN (p.race = 'race_white') THEN 'White'
                ELSE 'Unknown'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
                WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
                ELSE 'Unknown'
            END) AS ethnicity,
            p.addr1 AS addr1,
            p.addr2 AS addr2,
            p.addr3 AS addr3,
            p.city AS city,
            p.county AS county,
            p.st AS st,
            p.zip AS zip,
            p.dob AS dob,
            p.phone_number AS phone_number,
            p.phone_number_verified AS phone_number_verified,
            p.email AS email,
            p.email_verified AS email_verified,
            p.create_dt AS register_dt,
            p.token AS token,
            q.symptom_fever AS symptom_fever,
            q.symptom_shortness_breath AS symptom_shortness_breath,
            q.symptom_cough AS symptom_cough,
            q.symptom_chest_pain AS symptom_chest_pain,
            q.symptom_lack_of_smell AS symptom_lack_of_smell,
            q.symptom_other_breathing AS symptom_other_breathing,
            q.covid_contact AS covid_contact,
            q.prescription_use AS prescription_use,
            q.heart_disease AS heart_disease,
            q.diabetes AS diabetes,
            q.respiratory_diseases AS respiratory_diseases,
            q.autoimmune_disease AS autoimmune_disease,
            q.other_chronic AS other_chronic,
            q.allergies AS allergies,
            q.insurance_photo,
            q.insurance_details,
            a.id AS appointment_id,
            a.scheduled_dt AS scheduled_dt,
            a.check_in_dt AS check_in_dt,
            a.location_id AS location_id,
            a.group_code AS group_code,
            a.test_start_dt AS test_start_dt,
            a.test_end_dt AS test_end_dt,
            a.total_cost AS total_cost,
            a.billed_amount AS billed_amount,
            a.wp_customer_info_id AS wp_customer_info_id,
            a.status AS appointment_status,
            t.provider_id AS provider_id,
            t.sample_collection_location_id AS sample_collection_location_id,
            t.sample_collection_start_dt AS sample_collection_start_dt,
            t.sample_collection_end_dt AS sample_collection_end_dt,
            t.lab_physical_submission_dt AS lab_pysical_submission_dt,
            t.lab_electronic_submission_dt AS lab_electronic_submission_dt,
            t.lab_result_receive_dt AS lab_result_receive_dt,
            t.test_result AS test_result,
            t.consultation_status AS consultation_status,
            t.consultation_notes AS consultation_notes,
            t.status AS test_status,
            l.id AS location_id,
            l.site_code AS site_code,
            l.account AS account,
            l.addr1 AS loc_addr1,
            l.addr2 AS loc_addr2,
            l.city AS loc_city,
            l.st AS loc_st,
            l.zip AS loc_zip,
            l.time_zone AS time_zone,
            l.test_type_offered AS test_type_offered,
            r.sms_sent,
            r.sms_dt,
            r.email_sent,
            r.email_dt,
            r.voice_sent,
            r.voice_dt,
            r.group_notify,
            r.overall_status
        FROM
            patients p
                LEFT JOIN
            patient_questionnaires q ON (p.id = q.patient_id)
                LEFT JOIN
            appointments a ON (p.id = a.patient_id)
                LEFT JOIN
            test_samples t ON (a.id = t.id)
                LEFT JOIN
            locations l ON (a.location_id = l.id)
                LEFT JOIN
            result_notification_campaigns r ON (t.id = r.test_id)
        WHERE 1=1
            {}
        ORDER BY register_dt DESC
        LIMIT {}
        """.format(where_conditions, limit)
        rows = read_rows(sql)
        return rows

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None

