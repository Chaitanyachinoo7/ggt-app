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
def get_all_printer_hubs():
    try:
        sql = "SELECT * FROM workstations"
        return read_rows(sql)

    except Exception as err:
        log_generic(type="error", function='get_all_printer_hubs', error=err)
        return None








########################################################################################################
# [Protected] functions
########################################################################################################
