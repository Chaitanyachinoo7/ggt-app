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
async def get_stats_today():
    try:
        sql = """SELECT * FROM todays_location_stats_with_totals_test"""
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR, 
            function=whoami(), 
            error=err
        )
        return None

########################################################################################################
# [Protected] functions
########################################################################################################