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
def create_test_sample_from_appointment(appointment_id):
    try:
        sql = """
            INSERT ignore INTO test_samples
            (   
                id,
                appointment_id,
                group_code,
                patient_id,
                patient_questionnaire_id,
                sample_collection_location_id,
                sample_collection_start_dt,
                sample_collection_end_dt,
                status
            )
            SELECT 
                id,
                id,
                group_code,
                patient_id,
                patient_questionnaire_id,
                location_id,
                test_start_dt,
                test_end_dt,
                'ready_to_tx' AS status
            FROM
                appointments
            WHERE
            id = %s;
        """
        vals = (appointment_id,)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err,
            appointment_id=appointment_id
        )
        return None


def record_label_scan(appointment_id):
    try:
        sql = """
            UPDATE test_samples 
            SET 
                pre_ship_label_scan_dt = NOW() 
            WHERE 
                id = %s
        """

        vals = (appointment_id,)
        
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err,
            appointment_id=appointment_id
        )
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
