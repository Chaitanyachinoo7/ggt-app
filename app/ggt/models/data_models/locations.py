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
        vals = (location_id,)
        return read_row(sql, vals)

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
            where_conditions = "{} AND g.account LIKE '%{}%'".format(where_conditions, account)
        if group_code != '':
            where_conditions = "{} AND g.group_code LIKE '%{}%'".format(where_conditions, group_code)
        if site_code != '':
            where_conditions = "{} AND l.site_code LIKE '%{}%'".format(where_conditions, site_code)

        limit = 500

        sql = """
        SELECT DISTINCT
            l.id AS location_id,
            l.site_code,
            g.group_code,
            g.account,
            l.addr1,
            l.addr2,
            l.addr3,
            l.city,
            l.st,
            l.zip,
            l.time_zone,
            l.time_zone_offset,
            l.test_type_offered,
            l.status
        FROM
            locations l
                INNER JOIN
            group_codes_to_locations_mapping m ON l.id = m.location_id
                INNER JOIN
            groups g ON (g.id = m.group_id)
        WHERE 1=1
            {}
        ORDER BY l.id DESC
        LIMIT {}
        """.format(where_conditions, limit)
        return read_rows(sql)

    except Exception as err:
        log_generic(type="error", function='get_all_locations', error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
