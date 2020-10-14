from datetime import datetime

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


def add_outbound_call_status(test_id: int,
                             first_name: str,
                             test_date: str,
                             dob: str,
                             token: str,
                             to_email: str,
                             to_number: str,
                             test_result: str,
                             call_status: str,
                             call_initiated_dt: datetime):
    try:
        # delete_status = __delete_earlier_status(test_id)
        sql = """
            INSERT INTO 
                outbound_results_logs
                (
                    test_id,
                    first_name,
                    test_date,
                    dob,
                    token, 
                    to_email,
                    to_number,
                    test_result,
                    call_status, 
                    call_initiated_dt
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        val = (
            test_id,
            first_name,
            test_date,
            dob,
            token,
            to_email,
            to_number,
            test_result,
            call_status,
            call_initiated_dt
        )
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(
            type=ERROR,
            data=(
                test_id,
                first_name,
                test_date,
                dob,
                token,
                to_email,
                to_number,
                test_result,
                call_status,
                call_initiated_dt
            ),
            locals=locals(),
            function=whoami(),
            error=err
        )
        return None

# Todo clean up
def update_outbound_call_status(test_id, call_status, datetime_field, date_time):
    try:
        sql = "UPDATE outbound_results_logs SET " + datetime_field + " = '" + \
            str(date_time)+"', call_status = '" + \
            call_status+"' WHERE test_id = "+test_id
        return exec_update(sql, )

    except Exception as err:
        log_generic(
            type=ERROR,
            data=(
                test_id,
                datetime_field,
                date_time
            ),
            function=whoami(),
            error=err
        )
    
    return None


def __delete_earlier_status(test_id: int):
    try:
        sql = """
            DELETE FROM 
                outbound_results_status
            WHERE
                test_id = %s
            """
        vals = (test_id,)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            test_id=test_id,
            function=whoami(),
            error=err
        )

    return None
