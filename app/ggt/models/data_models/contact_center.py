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


def update_outbound_call_status(test_id,
                                first_name,
                                test_date,
                                dob,
                                token,
                                to_email,
                                to_number,
                                test_result,
                                call_status):
    try:
        delete_status = __delete_earlier_status(test_id)
        sql = """
            INSERT INTO outbound_results_status 
                (test_id,first_name,test_date,dob,token, to_email,to_number,test_result,call_status)
            
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        val = (test_id,
               first_name,
               test_date,
               dob,
               token,
               to_email,
               to_number,
               test_result,
               call_status)

        return exec_insert(sql, val)

    except Exception as err:
        log_generic(type="error", data=(test_id,
                                        first_name,
                                        test_date,
                                        dob,
                                        token,
                                        to_email,
                                        to_number,
                                        test_result,
                                        call_status), locals=locals(),
                    function='update_outbound_call_status', error=err)
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