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

from ggt.lib.db import (
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
            INSERT INTO test_samples
            (   
                id,
                appointment_id,
                group_code,
                patient_id,
                vial_id,
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
                vial_id,
                patient_questionnaire_id,
                location_id,
                test_start_dt,
                test_end_dt,
                'ready_to_tx' AS status
            FROM
                appointments
            WHERE
            id = %s
            
            ON DUPLICATE KEY 
	        UPDATE 
                group_code = VALUES(group_code),
                patient_id = VALUES(patient_id),
                vial_id = VALUES(vial_id),
                patient_questionnaire_id = VALUES(patient_questionnaire_id),
                sample_collection_location_id = VALUES(sample_collection_location_id),
                sample_collection_start_dt = VALUES(sample_collection_start_dt),
                sample_collection_end_dt = VALUES(sample_collection_end_dt),
                status = VALUES(status)
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


def lab_status_update(lab_status_update_request):
    try:
        sql = """
                INSERT INTO status_updates_ait
                (
                    lab_code,
                    requisition_id,
                    order_id,
                    status_code,
                    remarks
                )
            VALUES (%s, %s, %s, %s, %s)
            """
        vals = (lab_status_update_request.lab_code,
                lab_status_update_request.requisition_id,
                lab_status_update_request.order_id,
                lab_status_update_request.status_code,
                lab_status_update_request.remarks)
        if exec_insert(sql, vals):
            return True
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err,
            lab_status_update_request=lab_status_update_request
        )
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
