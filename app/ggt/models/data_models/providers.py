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
from ggt.models.data_models.data_types import ConsultationNotesEnum, PositiveCall, ConsultationStatusEnum


def get_provider_processing_list(offset, consultation_status, consultation_notes, positive_call):
    try:
        where_conditions = '(TO_DAYS(NOW()) - TO_DAYS(t.create_dt)) <= 15'
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
                               "'{}')".format(where_conditions, ConsultationStatusEnum.pending)
        if positive_call == PositiveCall.already_called:
            where_conditions = "{} AND t.test_result ='pos' AND t.consultation_status = '{}'".format(
                where_conditions, ConsultationStatusEnum.completed)

        sql = """SELECT 
    t.group_code AS group_code,
    t.lab_id,
    t.lab_submission_batch_id,
    t.test_result,
    t.notification_status,
    t.notification_method,
    t.notification_acknowledgement_dt,
    t.consultation_status,
    t.status AS test_status,
    t.test_type,
    p.id AS patient_id,
    p.first_name,
    p.middle_name,
    p.last_name,
    p.gender,
    p.height_ft,
    p.height_in,
    p.weight_lb,
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
    p.addr1,
    p.addr2,
    p.city,
    p.st,
    p.zip,
    p.dob,
    p.phone_number AS phone_number,
    p.phone_number_verified AS phone_number_verified,
    p.email AS patient_email,
    p.email_verified AS email_verified,
    p.token AS token,
    q.id AS patient_questionnaire_id,
    q.symptom_fever,
    q.symptom_shortness_breath,
    q.symptom_cough,
    q.symptom_chest_pain,
    q.symptom_lack_of_smell,
    q.symptom_other_breathing,
    q.covid_contact,
    q.prescription_use,
    q.heart_disease,
    q.diabetes,
    q.respiratory_diseases,
    q.autoimmune_disease,
    q.other_chronic,
    q.allergies,
    c.id AS consultaion_id,
    c.notes AS consultation_notes,
    c.id_start_dt AS id_start_dt,
    c.id_end_dt AS id_end_dt,
    c.provider_external_ids AS provider_ids,
    c.consultation_type_codes AS consultation_type_codes,
    c.resolution_codes AS resolution_codes,
    c.id_provider_names AS id_provider_names,
    c.id_given_names AS id_given_names,
    c.id_family_names AS id_family_names,
    c.id_email AS id_email,
    c.id_email_verified AS id_email_verified,
    c.id_pictures AS id_pictures,
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
    a.status AS appointment_status
FROM
    test_samples t
        INNER JOIN
    appointments a ON t.appointment_id = a.id
        INNER JOIN
    patients p ON t.patient_id = p.id
        INNER JOIN
    patient_questionnaires q ON q.patient_id = p.id
        LEFT JOIN
    (SELECT 
        appointment_id,
            GROUP_CONCAT(provider_external_id, ":", notes) AS notes,
            GROUP_CONCAT(provider_external_id) AS provider_external_ids,
            GROUP_CONCAT(provider_external_id, "__", pc.start_dt) AS id_start_dt,
            GROUP_CONCAT(provider_external_id, "__", pc.end_dt) AS id_end_dt,
            GROUP_CONCAT(pc.id) AS id,
            GROUP_CONCAT(pc.consultation_type_code) AS consultation_type_codes,
            GROUP_CONCAT(pc.resolution_code) AS resolution_codes,
            GROUP_CONCAT(u.external_id, ":", u.name) AS id_provider_names,
            GROUP_CONCAT(u.external_id, ":", u.family_name) AS id_family_names,
            GROUP_CONCAT(u.external_id, ":", u.given_name) AS id_given_names,
            GROUP_CONCAT(u.external_id, ":", u.email) AS id_email,
            GROUP_CONCAT(u.external_id, ":", u.email_verified) AS id_email_verified,
            GROUP_CONCAT(u.external_id, "__", u.picture) AS id_pictures
    FROM
        patient_consultations pc
    LEFT JOIN appointments ap ON pc.appointment_id = ap.id
    LEFT JOIN  ggt_users u ON u.external_id = pc.provider_external_id
    GROUP BY appointment_id) c ON a.id = c.appointment_id
    WHERE
        {} and t.id = 526036
    ORDER BY t.create_dt ASC
    LIMIT 20 OFFSET {};
""".format(where_conditions, offset)
        rows = read_rows(sql)
        return __process_task_list_response(rows)
    except Exception as err:
        log_generic(
            type=ERROR,
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
                     id = %s AND consultation_status != %s;
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
            type=ERROR,
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
            type=ERROR,
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
                     resolution_code = %s
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
            type=ERROR,
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
            type=ERROR,
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
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


########################################################################################################
# [Protected] functions
########################################################################################################

def __process_task_list_response(tasks):
    for task in tasks:
        task['insurance_photo'] = 'Insurance Photo'
        provider_ids = task['provider_ids'].split(',') if task['provider_ids'] else []
        task.pop('provider_ids', None)
        consultation_notes = task['consultation_notes'].split(',') if task['consultation_notes'] else []
        task.pop('consultation_notes', None)
        consultation_type_codes = task['consultation_type_codes'].split(',') if task['consultation_type_codes'] else []
        task.pop('consultation_type_codes', None)
        resolution_codes = task['resolution_codes'].split(',') if task['resolution_codes'] else []
        task.pop('resolution_codes', None)
        id_provider_names = task['id_provider_names'].split(',') if task['id_provider_names'] else []
        task.pop('id_provider_names', None)
        id_given_names = task['id_given_names'].split(',') if task['id_given_names'] else []
        task.pop('id_given_names', None)
        id_family_names = task['id_family_names'].split(',') if task['id_family_names'] else []
        task.pop('id_family_names', None)
        id_email = task['id_email'].split(',') if task['id_email'] else []
        task.pop('id_email', None)
        id_email_verified = task['id_email_verified'].split(',') if task['id_email_verified'] else []
        task.pop('id_email_verified', None)
        id_pictures = task['id_pictures'].split(',') if task['id_pictures'] else []
        task.pop('id_pictures', None)
        start_dt = task['id_start_dt'].split(',') if task['id_start_dt'] else []
        task.pop('id_start_dt', None)
        end_dt = task['id_end_dt'].split(',') if task['id_end_dt'] else []
        task.pop('id_end_dt', None)

        consultations = []

        for idx, id in enumerate(provider_ids):
            provider_id = id
            consultation_code = consultation_type_codes[idx] if len(consultation_type_codes) > idx else None
            consultation_note = consultation_notes[idx].split(":")[1] if len(consultation_notes) > idx else None
            resolution_code = resolution_codes[idx] if len(resolution_codes) > idx else None
            provider_name = id_provider_names[idx].split(":")[1] if len(id_provider_names) > idx else None
            provider_given_name = id_given_names[idx].split(":")[1] if len(id_given_names) > idx else None
            provider_family_name = id_family_names[idx].split(":")[1] if len(id_family_names) > idx else None
            provider_email = id_email[idx].split(":")[1] if len(id_email) > idx else None
            provider_email_verified = id_email_verified[idx].split(":")[1] if len(id_email_verified) > idx else None
            provider_photo = id_pictures[idx].split("__")[1] if len(id_pictures) > idx else None
            consultation_start_dt = start_dt[idx].split("__")[1] if len(start_dt) > idx else None
            consultation_end_dt = end_dt[idx].split("__")[1] if len(end_dt) > idx else None

            consultations.append({
                "provider_id": provider_id,
                "consultation_note": consultation_note,
                "consultation_code": consultation_code,
                "resolution_code": resolution_code,
                "provider_name": provider_name,
                "provider_given_name": provider_given_name,
                "provider_family_name": provider_family_name,
                "provider_email": provider_email,
                "provider_email_verified": provider_email_verified,
                "provider_photo": provider_photo,
                "consultation_start_dt": consultation_start_dt,
                "consultation_end_dt": consultation_end_dt
            })
        task['consultations'] = consultations

    return tasks


