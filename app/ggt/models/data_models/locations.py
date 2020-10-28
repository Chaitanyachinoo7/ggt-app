from typing import List, Set, Dict, Tuple, Optional
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

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

from ggt.models.data_models.data_types import (
    GgtLocation,
    GgtServiceCatalogItem
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_location_by_id(location_id):
    try:
        sql = """
            SELECT 
                id,
                site_code,
                group_code,
                account,
                name,
                addr1,
                addr2,
                addr3,
                city,
                st,
                zip,
                lat,
                lng,
                time_zone,
                time_zone_offset,
                test_type_offered,
                status,
                type,
                billing_type,
                collect_insurance_info,
                allow_insurance_skip,
                collect_upfront_payment,
                image_thumbnail
            FROM 
                locations 
            WHERE 
                id = %s 
            LIMIT 1
        """
        vals = (location_id,)
        row = read_row(sql, vals)
        return __map_row_to_location(row)
        
    except Exception as err:
        log_generic(
            type=ERROR, 
            location_id=location_id, 
            function=whoami(), 
            error=err
        )
        return None


def get_services_available_for_location(location_id):
    try:
        sql = """
            SELECT 
                s.id,
                s.service_code,
                s.service_name,
                s.price,
                s.selfpay_amount,
                s.copay_amount,
                s.insurance_amount
            FROM
                services_to_locations_mapping m
                    JOIN
                services_catalog s ON (s.id = m.service_id)
            WHERE
                location_id = %s
        """
        vals = (location_id,)
        rows = read_rows(sql, vals)
        return __map_rows_to_services_list(rows)
        
    except Exception as err:
        log_generic(
            type=ERROR, 
            location_id=location_id, 
            function=whoami(), 
            error=err
        )
        return None


def get_all_locations_without_thumbnail():
    try:
        sql = """SELECT id,
                    site_code,
                    group_code,
                    account,
                    name,
                    addr1,
                    addr2,
                    addr3,
                    city,
                    st,
                    zip,
                    lat,
                    lng,
                    time_zone,
                    time_zone_offset,
                    test_type_offered,
                    status,
                    type,
                    billing_type,
                    collect_insurance_info,
                    allow_insurance_skip,
                    collect_upfront_payment,
                    test_covid19,
                    test_flu,
                    test_consult,
                    create_dt,
                    update_dt
                FROM locations"""
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR, 
            function=whoami(), 
            error=err
        )
        return None


def get_all_locations():
    try:
        sql = "SELECT * FROM locations"
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
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
            l.lat,
            l.lng,
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
        log_generic(
            type=ERROR, 
            function=whoami(), 
            error=err
        )
        return None


def create_location(location):
    try:
        sql = """
               INSERT INTO locations
               (
                   site_code,
                   group_code,
                   name,
                   addr1,
                   addr2,
                   addr3,
                   city,
                   st,
                   zip,
                   lat,
                   lng,
                   time_zone,
                   time_zone_offset,
                   test_type_offered,
                   status,
                   type,
                   billing_type,
                   collect_insurance_info,
                   allow_insurance_skip,
                   collect_upfront_payment,
                   image_thumbnail 
               )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               """
        vals = (
            location.site_code,
            location.group_code,
            location.name,
            location.addr1,
            location.addr2,
            location.addr3,
            location.city,
            location.st,
            location.zip,
            location.lat,
            location.lng,
            location.time_zone,
            location.time_zone_offset,
            location.test_type_offered,
            location.status,
            location.type,
            location.billing_type,
            location.collect_insurance_info,
            location.allow_insurance_skip,
            location.collect_upfront_payment,
            location.image_thumbnail
        )
        location_id = exec_insert(sql, vals)
        return location_id

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def assign_group(req):
    try:
        sql = """
               INSERT INTO group_codes_to_locations_mapping
               (
                  group_id, 
                  location_id
               )
               values (%s, %s)
               """
        vals = (
            req.group_id,
            req.location_id
        )
        map_id = exec_insert(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def assign_service(req):
    try:
        sql = """
               INSERT INTO services_to_locations_mapping
               (
                  location_id, 
                  service_id
               )
               values (%s, %s)
               """
        vals = (
            req.location_id,
            req.service_id
        )
        map_id = exec_insert(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def remove_group(req):
    try:
        sql = """
               DELETE FROM group_codes_to_locations_mapping WHERE group_id = %s AND location_id = %s
               """
        vals = (
            req.group_id,
            req.location_id
        )
        deleted = exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def remove_service(req):
    try:
        sql = """
               DELETE FROM services_to_locations_mapping WHERE service_id = %s AND location_id = %s
               """
        vals = (
            req.service_id,
            req.location_id
        )
        deleted = exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_location(location):
    try:
        sql = """
               UPDATE locations SET
                   test_type_offered = %s,
                   status = %s,
                   type = %s,
                   billing_type = %s,
                   collect_insurance_info = %s,
                   allow_insurance_skip = %s,
                   collect_upfront_payment = %s
               WHERE id =  %s
                        """
        vals = (
            location.test_type_offered,
            location.status,
            location.type,
            location.billing_type,
            location.collect_insurance_info,
            location.allow_insurance_skip,
            location.collect_upfront_payment,
            location.id
        )
        updated = exec_update(sql, vals)
        return updated

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
def __map_row_to_location(row):
    loc = GgtLocation()
    try:
        loc.id = row['id']
        loc.site_code = row['site_code']
        loc.group_code = row['group_code']
        loc.account = row['account']
        loc.name = row['name']
        loc.addr1 = row['addr1']
        loc.addr2 = row['addr2']
        loc.addr3 = row['addr3']
        loc.city = row['city']
        loc.st = row['st']
        loc.zip = row['zip']
        loc.lat = row['lat']
        loc.lng = row['lng']
        loc.time_zone = row['time_zone']
        loc.time_zone_offset = row['time_zone_offset']
        loc.status = row['status']
        loc.type = row['type']
        loc.billing_type = row['billing_type']
        loc.collect_insurance_info = row['collect_insurance_info']
        loc.allow_insurance_skip = row['allow_insurance_skip']
        loc.collect_upfront_payment = row['collect_upfront_payment']
        loc.image_thumbnail = row['image_thumbnail']
        
    except Exception as err:
        log_generic(
            type=ERROR, 
            function=whoami(), 
            error=err
        )
        return None

    return loc


def __map_rows_to_services_list(rows):
    services_list: List[GgtServiceCatalogItem]
    services_list = []
    for row in rows:
        service_item = __map_row_to_service_item(row)
        services_list.append(service_item)
    return services_list


def __map_row_to_service_item(row):
    s = None
    try:
        s = GgtServiceCatalogItem()
        s.id = row['id']
        s.service_code = row['service_code']
        s.service_name = row['service_name']
        s.price = row['price']
        s.selfpay_amount = row['selfpay_amount']
        s.copay_amount = row['copay_amount']
        s.insurance_amount = row['insurance_amount']

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            row=row,
            error=err
        )

    return s