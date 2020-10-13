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


def add_outbound_call_status(test_id,
                             first_name,
                             test_date,
                             dob,
                             token,
                             to_email,
                             to_number,
                             test_result,
                             call_status, call_initiated_dt):
    try:
        # delete_status = __delete_earlier_status(test_id)
        sql = """
            INSERT INTO outbound_results_logs
                (test_id,first_name,test_date,dob,token, to_email,to_number,test_result,call_status, call_initiated_dt)
            
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
            call_status, call_initiated_dt
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


def update_outbound_call_status(test_id, call_status, datetime_field, datetime):
    try:
        sql = "UPDATE outbound_results_logs SET " + datetime_field + " = '" + \
            str(datetime)+"', call_status = '" + \
            call_status+"' WHERE test_id = "+test_id
        return exec_update(sql, )
    except Exception as err:
        log_generic(
            type=ERROR, 
            data=(
                test_id, 
                datetime_field, 
                datetime
            ),
            function=whoami(), 
            error=err
        )
        return None


def __delete_earlier_status(test_id):
    sql = """
        DELETE FROM 
            outbound_results_status
        WHERE
            test_id = %s
        """
    vals = (test_id,)
    return exec_delete(sql, vals)
