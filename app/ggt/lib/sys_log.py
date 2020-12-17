from ggt.lib.utils import (
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.lib.db import (exec_insert)

########################################################################################################
# [Public] functions
########################################################################################################


async def write_syslog(event, log_type, payload):
    return __insert_record_syslog(event, log_type, payload)

########################################################################################################
# [Protected] functions
########################################################################################################


async def __insert_record_syslog(event, log_type, payload):
    try:
        sql = "INSERT INTO system_log (event, type, payload) VALUES (%s, %s, %s)"
        val = (event, log_type, payload)
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            event=event,
            log_type=log_type,
            payload=payload,
            function=whoami(),
            error=err
        )
        return None
