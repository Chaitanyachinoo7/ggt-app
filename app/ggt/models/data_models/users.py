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

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
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
        vals = (email,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            email=email,
            function=whoami(), 
            error=err)
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
