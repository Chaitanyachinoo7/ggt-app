from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)

import ggt.lib.constants as c

from ggt.lib.utils import (
    log_generic,
    whoami
)

########################################################################################################
# [Public] functions
########################################################################################################
from ggt.models.data_models.data_types import BillingStatusEnum, TestResultsEnum, ProviderReviewedEnum, \
    PreConsultationEnum, TestStatusEnum, AppointmentStatusEnum
from ggt.models.data_models.providers import process_consultations


def get_billing_list(offset, status=None, from_dt=None, to_dt=None,
                           limit=20, sort='DESC', pre_consulted='any', provider_reviewed='any', test_status='any',
                           appointment_status='any'):
    try:

        where_conditions = ''
        if from_dt:
            where_conditions = "{} AND t.create_dt >= '{}'".format(
                where_conditions, from_dt)
        if to_dt:
            where_conditions = "{} AND  t.create_dt <= '{}'".format(
                where_conditions, to_dt)
        if status:
            if status == BillingStatusEnum.pending:
                where_conditions = "{} AND (t.initial_billed_status = {} OR a.billing_status is NULL)".format(
                    where_conditions, 0)
            elif status == BillingStatusEnum.initial_billed_status:
                where_conditions = "{} AND t.initial_billed_status = {}".format(
                    where_conditions, 1)
            elif status == BillingStatusEnum.post_test_billed_status:
                where_conditions = "{} AND t.post_test_billed_status = {}".format(
                    where_conditions, 1)
        if pre_consulted != PreConsultationEnum.any:
            where_conditions = "{} AND (select (CASE WHEN c.consultation_type_codes LIKE '%pre%' THEN 1 ELSE 0 END) " \
                               "AS pre_consulted) = {}".format(
                                   where_conditions, pre_consulted)
        if provider_reviewed != ProviderReviewedEnum.any:
            if provider_reviewed == ProviderReviewedEnum.provider_reviewed:
                where_conditions = "{} AND t.consultation_status = '{}'".format(
                    where_conditions, ProviderReviewedEnum.provider_reviewed)
            if provider_reviewed == ProviderReviewedEnum.not_provider_reviewed:
                where_conditions = "{} AND (t.consultation_status = '{}' OR a.billing_status is NULL)".format(
                    where_conditions, ProviderReviewedEnum.not_provider_reviewed)
        if test_status != TestStatusEnum.any:
            where_conditions = "{} AND t.status = '{}'".format(
                where_conditions, test_status)
        if appointment_status != AppointmentStatusEnum.any:
            where_conditions = "{} AND a.status = '{}'".format(
                where_conditions, appointment_status)

        sql = """SELECT 
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
    q.serious_reaction,
    q.ggv_allergies,
    q.long_term_health,
    q.immune_system,
    q.immune_system_medications,
    q.nervous_system,
    q.blood_transfusion,
    q.recent_vaccinations,
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
    a.billing_status AS billing_status,
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
    t.initial_billed_status AS initial_billed_status,
    t.post_test_billed_status AS post_test_billed_status,
    l.id AS location_id,
    l.site_code AS site_code,
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
    (CASE
        WHEN
            (a.status = 'test_completed'
                AND mq.pmh LIKE '%1%'
                AND t.test_result = 'neg'
                AND c.consultation_type_codes LIKE '%pre%')
        THEN
            '99203,99072,99000,99423'
        WHEN
            (a.status = 'test_completed'
                AND t.test_result = 'pos'
                AND c.consultation_type_codes LIKE '%pre%')
        THEN
            '99203,99072,99000,99214'
        WHEN
            (a.status = 'test_completed'
                AND mq.pmh NOT LIKE '%1%'
                AND t.test_result = 'neg'
                AND c.consultation_type_codes LIKE '%pre%')
        THEN
            '99203,99072,99000,99422'
        WHEN
            (a.status = 'test_completed'
                AND mq.pmh LIKE '%1%'
                AND t.test_result = 'neg'
                AND (c.consultation_type_codes NOT LIKE '%pre%'
                OR c.consultation_type_codes IS NULL))
        THEN
            '99211,99072,99000,99423'
        WHEN
            (a.status = 'test_completed'
                AND t.test_result = 'pos'
                AND (c.consultation_type_codes NOT LIKE '%pre%'
                OR c.consultation_type_codes IS NULL))
        THEN
            '99211,99072,99000,99204'
        WHEN
            (a.status = 'test_completed'
                AND mq.pmh NOT LIKE '%1%'
                AND t.test_result = 'neg'
                AND (c.consultation_type_codes NOT LIKE '%pre%'
                OR c.consultation_type_codes IS NULL))
        THEN
            '99211,99072,99000,99422'
        WHEN
            (a.status = 'test_completed'
                AND c.consultation_type_codes LIKE '%pre%')
        THEN
            '99203,99072,99000'
        WHEN
            (a.status = 'test_completed'
                AND (c.consultation_type_codes NOT LIKE '%pre%'
                OR c.consultation_type_codes IS NULL))
        THEN
            '99211,99072,99000'
        ELSE null 
    END) AS billing_codes,
    (CASE
        WHEN
            c.consultation_type_codes LIKE '%pre%'
        THEN
             1
        ELSE 0 
    END) AS pre_consulted
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
    (SELECT 
        appointment_id,
        GROUP_CONCAT(DISTINCT pc.consultation_type_code) AS consultation_type_codes
    FROM
        patient_consultations pc
    LEFT JOIN appointments ap ON pc.appointment_id = ap.id
    GROUP BY appointment_id) c ON a.id = c.appointment_id
        LEFT JOIN
    (SELECT 
        ps.id AS patient_id,
                    CONCAT(COALESCE(pq.symptom_shortness_breath,''), COALESCE(pq.symptom_fever,''), COALESCE(pq.symptom_cough,''), COALESCE(pq.symptom_chest_pain,''), COALESCE(pq.symptom_lack_of_smell,''), COALESCE(pq.symptom_other_breathing,''), COALESCE(pq.prescription_use,''), COALESCE(pq.heart_disease,''), COALESCE(pq.diabetes,''), COALESCE(pq.respiratory_diseases,''), COALESCE(pq.autoimmune_disease,''), COALESCE(pq.other_chronic,''), COALESCE(pq.allergies,'')) as pmh
    FROM
        patients ps
    LEFT JOIN patient_questionnaires pq ON pq.patient_id = ps.id) mq ON mq.patient_id = p.id
        WHERE  1=1 
        {}
        ORDER BY register_dt {}
        LIMIT {}  offset {};
        """.format(where_conditions, sort, limit, offset)
        rows = replica_read_rows(sql)
        return __process_billing_response(rows)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_billing_status(appointment_id):
    try:
        sql = """UPDATE appointments
                  SET
                      billing_status = %s
                  WHERE
                      id = %s AND (billing_status = %s OR billing_status is null);
                 """
        pending = BillingStatusEnum.pending
        billed = BillingStatusEnum.billed
        vals = (
            billed,
            appointment_id,
            pending
        )
        updated = exec_update(sql, vals)
        return updated

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_insurance_record(insurance_record):
    try:
        sql = """INSERT INTO `insurance_info`
            (
            `patient_id`,
            `insurance_carrier`,
            `group_number`,
            `member_number`,
            `validated`)
                VALUES
                    (%s, %s, %s, %s, %s);"""
        vals = (insurance_record.patient_id,
                insurance_record.insurance_carrier,
                insurance_record.group_number,
                insurance_record.member_number,
                insurance_record.validated)
        res = exec_insert(sql, vals)
        return res

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def update_insurance_record(insurance_record):
    try:
        sql = """UPDATE `insurance_info` 
                    SET
                    `insurance_carrier` = %s,
                    `group_number` = %s,
                    `member_number` = %s,
                    `validated` = %s
                     WHERE `id` = %s"""
        vals = (
            insurance_record.insurance_carrier,
            insurance_record.group_number,
            insurance_record.member_number,
            insurance_record.validated,
            insurance_record.id)
        res = exec_update(sql, vals)
        return res

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def validate_insurance_record(insurance_record):
    try:
        sql = """UPDATE `insurance_info` 
                SET
                    `validated` = 1
                 WHERE `id` = %s"""
        vals = (insurance_record.id,)
        res = exec_update(sql, vals)
        return res

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def delete_insurance_record(insurance_record):
    try:
        sql = """DELETE FROM `insurance_info` 
                 WHERE `id` = %s"""
        vals = (insurance_record.id,)
        res = exec_update(sql, vals)
        return res

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def __process_billing_response(tasks):
    for task in tasks:
        appointment_id = task['appointment_id']
        task['billing_codes'] = task['billing_codes'].split(
            ',') if task['billing_codes'] else []
        task['insurance_card_url'] = '/api/billing/image/{}.png'.format(
            appointment_id)
        task['test_report_url'] = '/api/billing/report/{}.pdf'.format(
            appointment_id)
        if len(task['billing_codes']) < 3:
            task['billing_codes'] = []

    return {"list": tasks}
