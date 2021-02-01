from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)

from ggt.models.data_models.data_types import (
    ConsultationNotesEnum,
    PositiveCall,
    ConsultationStatusEnum
)

########################################################################################################
# [Public] functions
########################################################################################################


def get_provider_processing_list_db(offset, consultation_status, consultation_notes, positive_call, limit=20, test_id=None):
    try:
        where_conditions = '1=1'
        # where_conditions = '(TO_DAYS(NOW()) - TO_DAYS(t.create_dt)) <= 25'
        if consultation_status != ConsultationStatusEnum.any:
            if consultation_status == ConsultationStatusEnum.pending:
                where_conditions = "{} AND ( t.consultation_status = '{}' OR t.consultation_status is null)".format(
                    where_conditions, consultation_status)
            else:
                where_conditions = "{} AND t.consultation_status = '{}'".format(
                    where_conditions, consultation_status)
        if consultation_notes == ConsultationNotesEnum.with_notes:
            where_conditions = "{} AND c.notes is not null".format(
                where_conditions)
        if consultation_notes == ConsultationNotesEnum.without_notes:
            where_conditions = "{} AND c.notes is null".format(
                where_conditions)
        if positive_call == PositiveCall.must_call:
            where_conditions = "{} AND t.test_result = 'pos' AND (t.consultation_status is null OR " \
                               "t.consultation_status = " \
                               "'{}')".format(where_conditions,
                                              ConsultationStatusEnum.pending)
        if positive_call == PositiveCall.already_called:
            where_conditions = "{} AND t.test_result ='pos' AND t.consultation_status = '{}'".format(
                where_conditions, ConsultationStatusEnum.completed)
        if test_id is not None:
            where_conditions = "{} AND t.id = {}".format(
                where_conditions, test_id)

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
        WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
        WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
        WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
        ELSE 'Unknown'
    END) AS ethnicity,
    (CASE
        WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
        WHEN (p.race = 'race_asian') THEN 'Asian'
        WHEN (p.race = 'race_black') THEN 'Black or African American'
        WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
        WHEN (p.race = 'race_other') THEN 'Other'
        WHEN (p.race = 'race_white') THEN 'White'
        ELSE 'Unknown'
    END) AS race,
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
            u.picture AS provider_image_url
    FROM
        test_samples t
            INNER JOIN
        appointments a ON t.appointment_id = a.id
            INNER JOIN
        patients p ON t.patient_id = p.id
            INNER JOIN
        patient_questionnaires q ON q.patient_id = p.id
            LEFT JOIN
        locations l ON (a.location_id = l.id)
            LEFT JOIN
        result_notification_campaigns r ON (t.id = r.test_id)
            LEFT JOIN
        patient_consultations  c ON a.id = c.appointment_id
            LEFT JOIN
        ggt_users u ON u.external_id = c.provider_external_id
    WHERE
        {}
    ORDER BY t.create_dt ASC
    LIMIT {} OFFSET {};
""".format(where_conditions, limit, offset)
        rows = replica_read_rows(sql)
        return process_consultations(rows)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def _get_provider_processing_list_db(offset, consultation_status, consultation_notes, positive_call, limit, start_date, end_date, org_id):
    try:
        where_conditions = "o.id = {} AND o.is_active = 1 AND t.create_dt >= '{}' AND t.create_dt <= '{}'".format(org_id, start_date, end_date)
        if consultation_status != ConsultationStatusEnum.any:
            if consultation_status == ConsultationStatusEnum.pending:
                where_conditions = "{} AND ( t.consultation_status = '{}' OR t.consultation_status is null)".format(
                    where_conditions, consultation_status)
            else:
                where_conditions = "{} AND t.consultation_status = '{}'".format(
                    where_conditions, consultation_status)
        if consultation_notes == ConsultationNotesEnum.with_notes:
            where_conditions = "{} AND c.notes is not null".format(
                where_conditions)
        if consultation_notes == ConsultationNotesEnum.without_notes:
            where_conditions = "{} AND c.notes is null".format(
                where_conditions)
        if positive_call == PositiveCall.must_call:
            where_conditions = "{} AND t.test_result = 'pos' AND (t.consultation_status is null OR " \
                               "t.consultation_status = " \
                               "'{}')".format(where_conditions,
                                              ConsultationStatusEnum.pending)
        if positive_call == PositiveCall.already_called:
            where_conditions = "{} AND t.test_result ='pos' AND t.consultation_status = '{}'".format(
                where_conditions, ConsultationStatusEnum.completed)
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
        WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
        WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
        WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
        ELSE 'Unknown'
    END) AS ethnicity,
    (CASE
        WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
        WHEN (p.race = 'race_asian') THEN 'Asian'
        WHEN (p.race = 'race_black') THEN 'Black or African American'
        WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
        WHEN (p.race = 'race_other') THEN 'Other'
        WHEN (p.race = 'race_white') THEN 'White'
        ELSE 'Unknown'
    END) AS race,
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
    c.id AS consultation_id,
    c.notes AS consultation_notes,
    c.start_dt AS consultation_start_dt,
    c.end_dt AS consultation_end_dt,
    c.consultation_type_code AS consultation_type_code,
    c.resolution_code AS resolution_code,
    u.name AS provider_name,
    u.given_name AS provider_given_name,
    u.family_name AS provider_family_name,
    u.email AS provider_email,
    u.email_verified AS provider_email_verified,
    u.picture AS provider_image_url
FROM
    test_samples t
        JOIN
    appointments a ON t.appointment_id = a.id
        JOIN
    patients p ON t.patient_id = p.id
        JOIN
    patient_questionnaires q ON q.patient_id = p.id
        LEFT JOIN
    locations l ON (a.location_id = l.id)
        LEFT JOIN
    result_notification_campaigns r ON (t.id = r.test_id)
        LEFT JOIN
    patient_consultations c ON a.id = c.appointment_id
        LEFT JOIN
    ggt_users u ON u.external_id = c.provider_external_id
    	LEFT JOIN
	organizations o ON o.id = l.org_id
    WHERE
        {}
    ORDER BY t.create_dt ASC
    LIMIT {} OFFSET {}""".format(where_conditions, limit, offset)
        rows = replica_read_rows(sql)
        return process_consultations(rows)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def provider_lock_task(test_id):
    """
    Update the test sample table 1st, if updated then update patient consultation table
    """
    try:
        sql = """UPDATE test_samples
                 SET
                     consultation_status = %s
                 WHERE
                     id = %s AND (consultation_status != %s OR consultation_status is null);
                """
        in_progress = ConsultationStatusEnum.in_progress
        vals = (
            in_progress,
            test_id,
            in_progress
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


def create_patient_test_consultation(appointment_id, user_id):
    try:
        sql = """INSERT INTO `patient_consultations`
                        (
                        `provider_external_id`,
                        `appointment_id`,
                        `start_dt`
                        )
                    VALUES
                        (%s, %s, NOW()); """
        vals = (
            user_id,
            appointment_id,
        )
        id = exec_insert(sql, vals)

        if id:
            return {"consultation_id": id}
        else:
            return None

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_consultation_note(consultation_id, notes, consultation_type_code, resolution_code):
    """
    Update the test sample table 1st, if updated then update patient consultation table
    """
    try:
        sql = """UPDATE patient_consultations
                 SET
                     notes = %s,
                     consultation_type_code = %s,
                     resolution_code = %s,
                     end_dt = NOW()
                 WHERE
                     id = %s;
                """
        vals = (
            notes,
            consultation_type_code,
            resolution_code,
            consultation_id
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


def provider_complete_task(test_id):
    try:
        sql = """UPDATE test_samples
                     SET
                         consultation_status = %s
                     WHERE
                         id = %s AND consultation_status = %s;
                    """
        completed = ConsultationStatusEnum.completed
        in_progress = ConsultationStatusEnum.in_progress
        vals = (
            completed,
            test_id,
            in_progress
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


def provider_rollback_to_pending_task(test_id):
    try:
        sql = """UPDATE test_samples
                     SET
                         consultation_status = %s
                     WHERE
                         id = %s;
                    """
        pending = ConsultationStatusEnum.pending
        vals = (
            pending,
            test_id
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


def process_consultations(tasks):
    response = {}
    for idx, task in enumerate(tasks):

        consultation_notes = task['consultation_notes']
        task.pop('consultation_notes', None)
        consultation_id = task['consultation_id']
        task.pop('consultation_id', None)
        consultation_start_dt = task['consultation_start_dt']
        task.pop('consultation_start_dt', None)
        consultation_end_dt = task['consultation_end_dt']
        task.pop('consultation_end_dt', None)
        register_dt = task['register_dt']
        # task.pop('register_dt', None)
        provider_name = task['provider_name']
        task.pop('provider_name', None)
        provider_given_name = task['provider_given_name']
        task.pop('provider_given_name', None)
        provider_family_name = task['provider_family_name']
        task.pop('provider_family_name', None)
        provider_email = task['provider_email']
        task.pop('provider_email', None)
        provider_email_verified = task['provider_email_verified']
        task.pop('provider_email_verified', None)
        provider_image_url = task['provider_image_url']
        task.pop('provider_image_url', None)
        resolution_code = task['resolution_code']
        task.pop('resolution_code', None)
        consultation_type_code = task['consultation_type_code']
        task.pop('consultation_type_code', None)

        appointment_id = task['appointment_id']
        task['insurance_card_url'] = '/billing/image/{}.png'.format(
            appointment_id)
        task['test_report_url'] = '/billing/report/{}.pdf'.format(
            appointment_id)
        consultation = {
            "consultation_id": consultation_id,
            "consultation_notes": consultation_notes,
            "consultation_start_dt": consultation_start_dt,
            "consultation_end_dt": consultation_end_dt,
            "provider_name": provider_name,
            "provider_given_name": provider_given_name,
            "provider_family_name": provider_family_name,
            "provider_email": provider_email,
            "provider_email_verified": provider_email_verified,
            "provider_image_url": provider_image_url,
            "consultation_type_code": consultation_type_code,
            "resolution_code": resolution_code,
            "register_dt": register_dt
        }

        if appointment_id in list(response.keys()):
            if consultation_id:
                response[appointment_id]['consultations'].append(consultation)
        else:
            response[appointment_id] = task
            response[appointment_id]['consultations'] = []
            if consultation_id:
                response[appointment_id]['consultations'].append(consultation)
    return __sort_consultations(list(response.values()))


########################################################################################################
# [Protected] functions
########################################################################################################


def __sort_consultations(tasks):
    for task in tasks:
        consultations = task['consultations']
        task['consultations'] = __sort_by_field(consultations)
    return tasks


def __sort_by_field(consultations):
    new_list = sorted(
        consultations, key=lambda x: x['register_dt'], reverse=True)
    return new_list
