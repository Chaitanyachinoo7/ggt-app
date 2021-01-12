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
def lab_status_update(lab_status_update_request):
    try:
        sql = """
                INSERT INTO lab_status_updates
                (
                    lab_code,
                    requisition_id,
                    order_id,
                    status_code,
                    remarks, 
                    status_dt
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        vals = (
            lab_status_update_request.lab_code,
            lab_status_update_request.requisition_id,
            lab_status_update_request.order_id,
            lab_status_update_request.status_code,
            lab_status_update_request.remarks,
            lab_status_update_request.status_dt
        )
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
