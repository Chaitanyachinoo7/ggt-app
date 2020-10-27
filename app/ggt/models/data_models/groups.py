from ggt.lib.adapters.mysql_adapter import (
    read_rows
)
from ggt.lib.constants import (
    ERROR
)
from ggt.lib.utils import (
    log_generic,
    whoami
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_all_groups():
    try:
        sql = "SELECT * FROM groups"
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None