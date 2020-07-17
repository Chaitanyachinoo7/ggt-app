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
        log_generic(type="info", location_id=location_id, function='__read_record_locations_by_id', error=err)
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
