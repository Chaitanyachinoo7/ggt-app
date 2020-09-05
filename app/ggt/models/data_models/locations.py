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
        log_generic(type="error", location_id=location_id, function='get_location_by_id', error=err)
        return None


def get_all_locations():
    try:
        sql = "SELECT * FROM locations"
        return read_rows(sql)

    except Exception as err:
        log_generic(type="error", function='get_all_locations', error=err)
        return None


def search_locations(account, group_code, site_code):
    try:
        where_conditions = '' 
        if account != '':
            where_conditions = "{} AND account LIKE '%{}%'".format(where_conditions, account)
        if group_code != '':
            where_conditions = "{} AND group_code LIKE '%{}%'".format(where_conditions, group_code)
        if site_code != '':
            where_conditions = "{} AND site_code LIKE '%{}%'".format(where_conditions, site_code)

        limit = 500

        sql = """
        SELECT 
            id as location_id,
            site_code,
            group_code,
            account,
            addr1,
            addr2,
            addr3,
            city,
            st,
            zip,
            time_zone,
            time_zone_offset,
            test_type_offered,
            status
        FROM
            locations
        WHERE 1=1
            {}
        ORDER BY 
            id DESC
        LIMIT {}
        """.format(where_conditions, limit)
        return read_rows(sql)

    except Exception as err:
        log_generic(type="error", function='get_all_locations', error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
