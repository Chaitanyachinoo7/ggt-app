from ggt.lib.utils import (
    log_generic
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
def create_appointment(scheduled_dt, location_id, patient_id, patient_questionnaire_id, group_code):
    try:
        sql = "INSERT INTO appointments (scheduled_dt, location_id, patient_id, patient_questionnaire_id, group_code) VALUES (%s, %s, %s, %s, %s)"
        val = (scheduled_dt, location_id, patient_id,
               patient_questionnaire_id, group_code)
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(type="error", function='create_appointment', scheduled_dt=scheduled_dt, location_id=location_id,
                    patient_id=patient_id, patient_questionnaire_id=patient_questionnaire_id, group_code=group_code, error=err)
        return None


def get_appointment(appointment_id):
    try:
        sql = """SELECT 
                    a.id,
                    a.scheduled_dt,
                    a.group_code,
                    a.status,
                    l.addr1,
                    l.addr2,
                    l.city,
                    l.st,
                    l.zip,
                    p.dob,
                    p.first_name,
                    p.middle_name,
                    p.last_name,
                    p.addr1 as patient_addr1,
                    p.city as patient_city,
                    p.st as patient_st,
                    p.zip as patient_zip

                FROM
                    appointments a
                        JOIN
                    patients p ON a.patient_id = p.id
                        JOIN
                    locations l ON a.location_id = l.id
                WHERE
                    a.id = %s"""

        val = (appointment_id,)
        return read_row(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='get_appointment', error=err)
        return None


def get_monthy_calendar(from_date, to_date, location_id):
    try:
        sql = """SELECT 
                 * FROM appointment_with_patient
                WHERE
                    scheduled_dt between %s and %s
                    and location_id = %s
                    """

        val = (from_date, to_date, location_id)
        return read_rows(sql, val)
    except Exception as err:
        log_generic(type="error", location_id=location_id, from_date=from_date, to_date=to_date,
                    function='get_monthy_calendar', error=err)
        return None


def positive_result_followup():
    try:
        sql = """SELECT 
                    pos.patient_id,
                    pos.test_id,
                    pos.dob,
                    pos.first_name, 
                    pos.last_name, 
                    pos.phone_number, 
                    pos.email,
                    pat.gender,
                    pat.addr1,
                    patq.heart_disease,
                    patq.diabetes,
                    patq.respiratory_diseases,
                    patq.autoimmune_disease,
                    patq.other_chronic,
                    patq.allergies,
                    patq.prescription_use,
                    patq.symptom_fever,
                    patq.symptom_shortness_breath,
                    patq.symptom_cough,
                    patq.symptom_chest_pain,
                    patq.symptom_lack_of_smell,
                    patq.symptom_lack_of_smell,
                    patq.symptom_other_breathing,
                    patq.covid_contact
                FROM
                    positive_result_followup_queue pos
                INNER JOIN patients pat
                    ON pos.patient_id = pat.id
                INNER JOIN patient_questionnaires patq
                    ON patq.patient_id = pat.id
                WHERE
                    overall_status = %s LIMIT 1
                    """

        val = ("scheduled",)
        return read_row(sql, val)
    except Exception as err:
        log_generic(type="error", location_id=None,
                    function='get_monthy_calendar', error=err)
        return None


def get_user_role(email):
    try:
        sql = """SELECT role 
                FROM users 
                WHERE
                    email = %s
                    """

        val = (email,)
        return read_row(sql, val)
    except Exception as err:
        log_generic(type="error", email=email,
                    function='get_user_role', error=err)
        return None


def get_test_results():
    try:
        sql = """SELECT 
                    pos.id as patient_id,
                    ts.id as test_id,
                    pos.dob,
                    pos.first_name, 
                    pos.last_name, 
                    pos.phone_number, 
                    pos.email,
                    pat.gender,
                    pat.addr1,
                    ts.test_result,
                    ts.status
                FROM
                    ggt_dev.patients pos
                INNER JOIN ggt_dev.patients pat
                    ON pos.id = pat.id
                INNER JOIN ggt_dev.test_samples ts
                    ON pos.id = ts.patient_id
                    """
        # val = ()
        return read_rows(sql, )
    except Exception as err:
        log_generic(type="error", location_id=None,
                    function='get_monthy_calendar', error=err)
        return None


def update_positive_result_followup(id, datetime):
    try:
        sql = """UPDATE positive_result_followup_queue
                 SET overall_status = %s, update_dt = %s
                WHERE
                    test_id = %s
                    """

        val = ("pending", datetime, id)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", location_id=None,
                    function='get_monthy_calendar', error=err)
        return None


def update_appointment_with_checkin(appointment_id):
    try:
        sql = """
            UPDATE appointments 
                SET 
                    check_in_dt = NOW(),
                    status = 'checked_in'
                WHERE
                    id = %s
        """
        val = (appointment_id,)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='update_appointment_with_checkin', error=err)
        return None


def update_appointment_with_test_start(appointment_id):
    try:
        sql = """
            UPDATE appointments 
                SET 
                    test_start_dt = NOW(),
                    status = 'test_in_progress'
                WHERE
                    id = %s
        """
        val = (appointment_id,)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='update_appointment_with_test_start', error=err)
        return None


def update_appointment_with_test_completed(appointment_id):
    try:
        sql = """
            UPDATE appointments 
                SET 
                    test_end_dt = NOW(),
                    status = 'test_completed'
                WHERE
                    id = %s
            """
        val = (appointment_id,)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='update_appointment_with_test_completed', error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
