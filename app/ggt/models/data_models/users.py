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
def get_user_by_email(email):
    try:
        sql = """
            SELECT * 
            FROM 
                users 
            WHERE
                email = %s
            LIMIT 1
            """
        val = (email,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(
            type="error", 
            email=email,
            function='get_user_by_email', 
            error=err)
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
