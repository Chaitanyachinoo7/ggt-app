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
        if consultation_status:
            where_conditions = "{} AND t.consultation_status = '{}'".format(
                where_conditions, consultation_status)
        if consultation_notes == ConsultationNotesEnum.with_notes:
            where_conditions = "{} AND t.consultation_notes is not null".format(
                where_conditions)
        if consultation_notes == ConsultationNotesEnum.without_notes:
            where_conditions = "{} AND t.consultation_notes is null".format(
                where_conditions)
        if positive_call == PositiveCall.must_call:
            where_conditions = "{} AND t.test_result = 'pos' AND (t.consultation_status is null OR " \
                               "t.consultation_status = " \
                               "'{}')".format(where_conditions, ConsultationStatusEnum.pending)
        if positive_call == PositiveCall.already_called:
            where_conditions = "{} AND t.test_result ='pos' AND t.consultation_status = '{}'".format(
                where_conditions, ConsultationStatusEnum.completed)

        sql = """SELECT 
    appointment_id,
    t.group_code AS group_code,
    p.id AS patient_id,
    pq.id AS patient_questionnaire_id,
    provider_id,
    lab_id,
    lab_submission_batch_id,
    test_result,
    notification_status,
    notification_method,
    notification_acknowledgement_dt,
    consultation_status,
    consultation_notes,
    t.status AS test_status,
    test_type,
    first_name,
    middle_name,
    last_name,
    gender,
    height_ft,
    height_in,
    weight_lb,
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
    addr1,
    addr2,
    city,
    st,
    zip,
    dob,
    phone_number,
    phone_number_verified,
    email,
    email_verified,
    p.token AS token,
    symptom_fever,
    symptom_shortness_breath,
    symptom_cough,
    symptom_chest_pain,
    symptom_lack_of_smell,
    symptom_other_breathing,
    covid_contact,
    prescription_use,
    heart_disease,
    diabetes,
    respiratory_diseases,
    autoimmune_disease,
    other_chronic,
    allergies
FROM
    test_samples t
        INNER JOIN
    appointments a ON t.appointment_id = a.id
        INNER JOIN
    patients p ON t.patient_id = p.id
        INNER JOIN
    patient_questionnaires pq ON pq.patient_id = p.id
WHERE
    {}
ORDER BY t.create_dt ASC
LIMIT 10 OFFSET {};
""".format(where_conditions, offset)
        rows = read_rows(sql)
        return rows

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
