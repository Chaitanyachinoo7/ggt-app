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
def get_test_result(id):
    try:
        sql = """
                SELECT * 
                FROM ggt.detailed_test_results 
                WHERE id = %s
                LIMIT 1
                """
        val = (id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", id=id, function='get_test_result', error=err)
        return False


def get_test_result_by_token(token):
    try:
        sql = """
                SELECT * 
                FROM ggt.detailed_test_results 
                WHERE token = %s
                ORDER by test_id DESC
                LIMIT 1
                """
        val = (token,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", token=token,
                    function='get_test_result_by_token', error=err)
        return False


def get_test_details(test_id):
    try:
        sql = """
                SELECT * 
                FROM ggt.detailed_test_results 
                WHERE test_id = %s
                ORDER by test_id DESC
                LIMIT 1
                """
        val = (test_id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", test_id=test_id,
                    function='get_test_details', error=err)
        return False


def cc_patient_lookup(lname, dob):
    print(lname)
    try:
        sql = """
            SELECT * FROM detailed_test_results where 
            last_name= %s 
            AND dob = %s
            """
        val = (lname, dob,)
        return read_rows(sql, val)

    except Exception as err:
        log_generic(type="error", lname=lname, dob=lname,
                    function='cc_patient_lookup', error=err)
        return False


def search_tested_patients(last_name, dob):
    try:
        sql = """
                SELECT 
                    t.test_id,
                    t.first_name,
                    t.last_name,
                    t.dob,
                    t.phone_number,
                    t.email,
                    t.addr1 as p_addr1,
                    t.city as p_city,
                    t.st as p_st,
                    t.zip as p_zip,
                    t.sample_collection_start_dt,
                    t.token,
                    l.group_code,
                    l.account,
                    l.addr1,
                    l.city,
                    l.st,
                    l.zip,
                    (CASE
                        WHEN (test_result IS NULL) THEN 'Pending'
                        ELSE 'Available'
                    END) AS result
                FROM
                    (detailed_test_results t
                    JOIN locations l ON t.sample_collection_location_id = l.id)
                WHERE
                    last_name = %s
                        AND dob = %s
                ORDER BY t.test_id DESC
                """
        val = (last_name, dob)
        return read_rows(sql, val)

    except Exception as err:
        log_generic(type="error", last_name=last_name, dob=dob,
                    function='get_patient_search_results_with_tests', error=err)
        return False


'''
#TODO add provider ID
def create_test_sample(appointment_id, patient_id, patient_questionnaire_id, group_code, location_id):
    try:
        sql = """
                INSERT INTO test_samples
                (
                    id,
                    appointment_id,
                    group_code,
                    patient_id,
                    patient_questionnaire_id,
                    sample_collection_location_id,
                    sample_collection_start_dt
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
        val = (appointment_id, appointment_id, patient_id, patient_questionnaire_id, group_code, location_id)
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(
            type="error", 
            appointment_id=appointment_id, 
            patient_id=patient_id, 
            patient_questionnaire_id=patient_questionnaire_id, 
            group_code=group_code, 
            location_id=location_id, 
            function='create_test_sample', 
            error=err
        )
        return None

def update_test_with_test_start(appointment_id):
    try:
        sql = """
            UPDATE test_samples 
                SET 
                    sample_collection_start_dt = NOW(),
                    status = 'test_in_progress'
                WHERE
                    appointment_id = %s
        """
        val = (appointment_id,)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='update_appointment_with_test_start', error=err)
        return None

def update_test_with_test_completed(appointment_id):
    try:
        sql = """
            UPDATE test_samples 
                SET 
                    sample_collection_end_dt = NOW(),
                    status = 'test_completed'
                WHERE
                    appointment_id = %s
        """
        val = (appointment_id,)
        return exec_update(sql, val)
    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='update_appointment_with_test_completed', error=err)
        return None
'''
########################################################################################################
# [Protected] functions
########################################################################################################
