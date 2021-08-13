from pydantic import BaseModel
from typing import Dict, List, Optional

from ggt.lib.utils import (
    get_config_val as cfg,
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

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)


########################################################################################################
# [Public] functions
########################################################################################################
from ggt.models.data_models.providers import process_consultations
from ggt.models.data_models.data_types import VaxPreRegStatusEnum

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


#tz = cfg(default_timezone)
def find_patients(org_id, first_name='', middle_name='', last_name='', dob='', phone_number='',
                  email='', appointment_id='', group_code='', appointment_date='', location_id='', vial_id='', sort_field="register_dt", sort_type="desc",
                  token=None, is_patient=False):
    try:
        where_clause = "1=1"
        vals = ()

        if not is_patient:
            where_clause += " AND o.id = %s AND o.is_active = 1"
            vals = vals + (org_id,)
        if first_name != '':
            where_clause += " AND p.first_name LIKE %s"
            vals = vals + ("%" + first_name + "%",)
        if middle_name != '':
            where_clause += " AND p.middle_name LIKE %s"
            vals = vals + ("%" + middle_name + "%",)
        if last_name != '':
            where_clause += " AND p.last_name LIKE %s"
            vals = vals + ("%" + last_name + "%",)
        if dob != '':
            where_clause += " AND p.dob = %s"
            vals = vals + (dob,)
        if phone_number != '':
            where_clause += " AND p.phone_number LIKE %s"
            vals = vals + ("%" + phone_number + "%",)
        if email != '':
            where_clause += " AND p.email LIKE %s"
            vals = vals + ("%" + email + "%",)
        if appointment_id != '':
            where_clause += " AND a.id = %s"
            vals = vals + (appointment_id,)
        if group_code != '':
            where_clause += " AND a.group_code LIKE %s"
            vals = vals + ("%" + group_code + "%",)
        if appointment_date != '':
            where_clause += " AND DATE(a.scheduled_dt) = %s"
            vals = vals + (appointment_date,)
        if location_id != '':
            where_clause += " AND a.location_id = %s"
            vals = vals + (location_id,)
        if vial_id != '' and vial_id:
            where_clause += " AND a.vial_id = %s"
            vals = vals + (vial_id,)
        if token:
            where_clause += " AND p.result_token = %s AND p.token_expire > NOW()"
            vals = vals + (token,)

        limit = 500

        sql = """
        SELECT
            q.id AS q_id,
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
            q.symptom_fatigue AS symptom_fatigue,
            q.symptom_muscle_body_aches AS symptom_muscle_body_aches,
            q.symptom_headache AS symptom_headache,
            q.symptom_sore_throat AS symptom_sore_throat,
            q.symptom_congestion_runny_nose AS symptom_congestion_runny_nose,
            q.symptom_nausea_vomitting AS symptom_nausea_vomitting,
            q.symptom_diarrhea AS symptom_diarrhea,
            q.covid_contact AS covid_contact,
            q.prescription_use AS prescription_use,
            q.heart_disease AS heart_disease,
            q.diabetes AS diabetes,
            q.respiratory_diseases AS respiratory_diseases,
            q.autoimmune_disease AS autoimmune_disease,
            q.other_chronic AS other_chronic,
            q.allergies AS allergies,
            '' AS insurance_photo,
            q.insurance_details,
            q.serious_reaction AS ggv_serious_reaction,
            q.ggv_allergies AS ggv_allergies,
            q.long_term_health AS ggv_long_term_health,
            q.immune_system AS ggv_immune_system,
            q.immune_system_medications AS ggv_immune_system_medications,
            q.nervous_system AS ggv_nervous_system,
            q.blood_transfusion AS ggv_blood_transfusion,
            q.recent_vaccinations AS ggv_recent_vaccinations,
            a.id AS appointment_id,
            a.scheduled_dt AS scheduled_dt,
            a.check_in_dt AS check_in_dt,
            a.location_id AS location_id,
            a.group_code AS group_code,
            a.test_start_dt AS test_start_dt,
            a.test_end_dt AS test_end_dt,
            a.vial_id,
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
            l.name as loc_name,
            l.name AS account,
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
            r.overall_status,
            c.id AS consultation_id,
            c.notes AS consultation_notes,
            c.start_dt AS consultation_start_dt,
            c.end_dt AS consultation_end_dt,
            c.provider_external_id AS provider_id,
            c.consultation_type_code AS consultation_type_code,
            c.resolution_code AS resolution_code,
            u.name AS provider_name,
            u.given_name AS provider_given_name,
            u.family_name AS provider_family_name,
            u.email AS provider_email,
            u.email_verified AS provider_email_verified,
            u.picture AS provider_image_url,
            i.id AS insurance_id,
            i.relationship AS insurance_relationship,
            i.group_no AS insurance_group_number,
            i.member_id AS insurance_member_id,
            i.payer AS insurance_payer,
            i.level AS insurance_level,
            sc.service_code AS service_code
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
                LEFT JOIN
            patient_consultations  c ON a.id = c.appointment_id
                LEFT JOIN
            ggt_users u ON u.external_id = c.provider_external_id
                LEFT JOIN 
            patient_insurance_details i ON p.id = i.patient_id
                LEFT JOIN
            appointment_services aps ON a.id = aps.appointment_id
                LEFT JOIN
            services_catalog sc ON sc.id = aps.service_id
                LEFT JOIN
			organizations o ON o.id = l.org_id
        WHERE
            {}
        order by {} {}
        LIMIT %s
        """.format(where_clause, sort_field, sort_type)

        vals = vals + (limit,)
        rows = replica_read_rows(sql, vals)
        return process_consultations(rows)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def find_patients_for_vaccineation(appointment_ids):
    # empty array is not allowed
    try:
        where_clause = " a.id in (" + (','.join(['%s'] * len(appointment_ids))) + ")"
        vals = tuple(appointment_ids)
        sql = """
            SELECT 
            a.id,
            a.scheduled_dt,
            a.injection_site,
            a.vax_end_dt,
            p.first_name,
            p.last_name,
            p.middle_name,
            p.gender,
            p.dob,
            p.phone_number,
            p.email,
            p.addr1,
            p.city,
            p.st,
            p.zip,
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
            END) AS ethnicity
        FROM
			appointments a
                JOIN
            patients p ON (a.patient_id = p.id)
        Where {}
        """.format(where_clause)

        rows = replica_read_rows(sql, vals)
        return rows
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def find_patients_by_patient_ids(patient_ids):
    try:
        where_clause = " p.id in (" + (','.join(['%s'] * len(patient_ids))) + ")"
        vals = tuple(patient_ids)
        sql = """
        SELECT 
            p.first_name,
            p.last_name,
            p.dob
        FROM patients p
        WHERE {};
        """.format(where_clause)
        
        rows = replica_read_rows(sql, vals)
        return rows
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def find_patients_in_vax_waitlist(data):
    try:
        where_conditions = "1=1"
        vals = ()
        if data.first_name != '':
            where_conditions += " AND p.first_name LIKE %s"
            vals += ("%" + data.first_name + "%",)
        if data.middle_name != '':
            where_conditions += " AND p.middle_name LIKE %s"
            vals += ("%" + data.middle_name + "%",)
        if data.last_name != '':
            where_conditions += " AND p.last_name LIKE %s"
            vals += ("%" + data.last_name + "%",)
        if data.dob != '':
            where_conditions += " AND p.dob = %s"
            vals += (data.dob,)
        if data.phone_number != '':
            where_conditions += " AND p.phone_number LIKE %s"
            vals += ("%" + data.phone_number + "%",)
        if data.email != '':
            where_conditions += " AND p.email LIKE %s"
            vals += ("%" + data.email + "%",)
        if data.heart_disease:
            where_conditions += " AND q.heart_disease=1"
        if data.diabetes:
            where_conditions += " AND q.diabetes=1"
        if data.respiratory_diseases:
            where_conditions += " AND q.respiratory_diseases=1"
        if data.autoimmune_disease:
            where_conditions += " AND q.autoimmune_disease=1"
        if data.other_chronic:
            where_conditions += " AND q.other_chronic=1"
        if data.allergies:
            where_conditions += " AND q.allergies=1"
        if data.prescription_use:
            where_conditions += " AND q.prescription_use=1"
        if data.status != VaxPreRegStatusEnum.any:
            where_conditions += " AND vpr.status=%s"
            vals += (data.status,)

        having_conditions = "1=1"
        if data.min_age:
            having_conditions += " AND age >= %s"
            vals += (data.min_age,)
        if data.max_age:
            having_conditions += " AND age <= %s"
            vals += (data.max_age,)

        if data.sort_field in ["first_name", "middle_name", "last_name", "age", "signed_up_dt"]:
            sort_field = data.sort_field
        else:
            sort_field = "signed_up_dt"

        sql = """
        SELECT
            vpr.id as vax_pre_reg_id,
            q.id AS q_id,
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
            '' AS insurance_photo,
            q.insurance_details,
            q.serious_reaction AS ggv_serious_reaction,
            q.ggv_allergies AS ggv_allergies,
            q.long_term_health AS ggv_long_term_health,
            q.immune_system AS ggv_immune_system,
            q.immune_system_medications AS ggv_immune_system_medications,
            q.nervous_system AS ggv_nervous_system,
            q.blood_transfusion AS ggv_blood_transfusion,
            q.recent_vaccinations AS ggv_recent_vaccinations,
            FLOOR(DATEDIFF(NOW(), p.dob) / 365.25) as age,
            vpr.create_dt as signed_up_dt,
            vpr.status
        FROM
            patients p
                INNER JOIN
            vax_pre_registrations vpr ON (p.id = vpr.patient_id)
                INNER JOIN
            patient_questionnaires q ON (q.id = vpr.patient_questionnaire_id)
        WHERE
            {}
        HAVING
            {}
        order by {} {}
        LIMIT {} OFFSET {}
        """.format(where_conditions, having_conditions, sort_field, data.sort, data.limit, data.offset)
        
        return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_vax_registered_waitlist_around_location(location_id, radius):

    try:
        sql1 = "SELECT lat, lng FROM locations WHERE id=%s"
        location = replica_read_row(sql1, (location_id,))

        if location is None:
            return []

        lat = location["lat"]
        lng = location["lng"]

        sql2 = """
        SELECT
            vpr.id as vax_pre_reg_id,
            q.id AS q_id,
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
            '' AS insurance_photo,
            q.insurance_details,
            q.serious_reaction AS ggv_serious_reaction,
            q.ggv_allergies AS ggv_allergies,
            q.long_term_health AS ggv_long_term_health,
            q.immune_system AS ggv_immune_system,
            q.immune_system_medications AS ggv_immune_system_medications,
            q.nervous_system AS ggv_nervous_system,
            q.blood_transfusion AS ggv_blood_transfusion,
            q.recent_vaccinations AS ggv_recent_vaccinations,
            (3963 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(z.Latitude)) * COS(RADIANS(z.Longitude) - RADIANS(%s)) + SIN(RADIANS(%s)) * SIN(RADIANS(z.Latitude)))) AS distance
        FROM
            patients p
        INNER JOIN
            vax_pre_registrations vpr on p.id = vpr.patient_id
        INNER JOIN
            patient_questionnaires q ON q.id = vpr.patient_questionnaire_id
        INNER JOIN
            z_zipcodes z on p.zip = z.Zip
        WHERE
            vpr.status = "registered"
            AND (3963 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(z.Latitude)) * COS(RADIANS(z.Longitude) - RADIANS(%s)) + SIN(RADIANS(%s)) * SIN(RADIANS(z.Latitude)))) < %s
        ORDER BY
            distance
        """
        vals = (lat, lng, lat, lat, lng, lat, radius)
        return replica_read_rows(sql2, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None

