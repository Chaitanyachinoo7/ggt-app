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
        sql = """SELECT * FROM ggt.detailed_test_results 
                where id = %s"""
        val = (id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", id=id, function='get_test_result', error=err)
        return False


def get_test_result_by_token(token):
    try:
        sql = """SELECT * FROM ggt.detailed_test_results 
                where token = %s"""
        val = (token,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", token=token,
                    function='get_test_result_by_token', error=err)
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
