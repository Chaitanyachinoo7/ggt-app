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
def get_location_by_id(location_id):
    try:
        sql = "SELECT * FROM locations where id = %s LIMIT 1"
        val = (location_id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="info", location_id=location_id, function='get_location_by_id', error=err)
        return None


def get_all_locations():
    try:
        sql = "SELECT * FROM locations"
        return read_rows(sql)

    except Exception as err:
        log_generic(type="info", function='get_all_locations', error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
