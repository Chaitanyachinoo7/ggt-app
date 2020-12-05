from typing import List, Set, Dict, Tuple, Optional

from ggt.lib.adapters.google_maps import get_gps_coordinates
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    exec_batch_execute
)

from ggt.models.data_models.data_types import (
    GgtLocation,
    GgtServiceCatalogItem
)


########################################################################################################
# [Public] functions
########################################################################################################
async def get_location_by_id(location_id):
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
        row = await read_row(sql, vals)
        return __map_row_to_location(row)
        

    except Exception as err:
        log_generic(
            type=c.ERROR, 
            location_id=location_id, 
            function=whoami(), 
            error=err
        )
        return None


async def get_services_available_for_location(location_id):
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
        rows = await read_rows(sql, vals)
        return __map_rows_to_services_list(rows)
        

    except Exception as err:
        log_generic(
            type=c.ERROR, 
            location_id=location_id, 
            function=whoami(), 
            error=err
        )
        return None


async def get_states():
    try:
        sql = "SELECT * FROM states WHERE active = 1;"
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def get_all_locations_without_thumbnail():
    try:
        sql = """SELECT 
    l.id,
    l.site_code,
    l.group_code,
    l.account,
    l.name,
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
    l.status,
    l.type,
    l.billing_type,
    l.collect_insurance_info,
    l.allow_insurance_skip,
    l.collect_upfront_payment,
    l.test_covid19,
    l.test_flu,
    l.test_consult,
    l.create_dt,
    l.update_dt,
    s.service_names,
    gp.grpup_names
FROM
    locations l
        LEFT JOIN
    (SELECT 
        sm.location_id,
            GROUP_CONCAT(DISTINCT sc.service_name) AS service_names
    FROM
        services_to_locations_mapping sm
    LEFT JOIN services_catalog sc ON sm.service_id = sc.id
    GROUP BY sm.location_id) s ON l.id = s.location_id
    LEFT JOIN (SELECT 
    gm.location_id, GROUP_CONCAT(DISTINCT g.account) as grpup_names
FROM
    group_codes_to_locations_mapping gm
        LEFT JOIN
    groups g ON gm.group_id = g.id
    group by gm.location_id) gp on l.id = gp.location_id"""
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR, 
            function=whoami(), 
            error=err
        )
        return None


async def get_all_locations():
    try:
        sql = "SELECT * FROM locations"
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def search_locations(account, group_code, site_code, location_name):
    try:
        where_conditions = '' 
        if account != '':
            where_conditions = "{} AND g.account LIKE '%{}%'".format(where_conditions, account)
        if group_code != '':
            where_conditions = "{} AND g.group_code LIKE '%{}%'".format(where_conditions, group_code)
        if site_code != '':
            where_conditions = "{} AND l.site_code LIKE '%{}%'".format(where_conditions, site_code)
        if location_name != '':
            where_conditions = "{} AND l.name LIKE '%{}%'".format(where_conditions, location_name)

        limit = 500

        sql = """ SELECT DISTINCT
        l.name AS location_name,
    l.id AS location_id,
    l.site_code,
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
    l.status,
    l.billing_type,
    l.collect_insurance_info,
    l.allow_insurance_skip,
    l.collect_upfront_payment,
    s.service_names,
    gp.group_accounts,
    gp.group_codes
FROM
    locations l
        LEFT JOIN
    (SELECT 
        sm.location_id,
            GROUP_CONCAT(DISTINCT sc.service_name) AS service_names
    FROM
        services_to_locations_mapping sm
    LEFT JOIN services_catalog sc ON sm.service_id = sc.id
    GROUP BY sm.location_id) s ON l.id = s.location_id
        LEFT JOIN
    (SELECT 
        gm.location_id,
            GROUP_CONCAT(DISTINCT g.account) AS group_accounts,
            GROUP_CONCAT(DISTINCT g.group_code) AS group_codes
    FROM
        group_codes_to_locations_mapping gm
    LEFT JOIN groups g ON gm.group_id = g.id
    GROUP BY gm.location_id) gp ON l.id = gp.location_id
        WHERE 1=1
            {}
        ORDER BY l.id DESC
        LIMIT {}
        """.format(where_conditions, limit)
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR, 
            function=whoami(), 
            error=err
        )
        return None


async def create_location(location):
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
        location_id = await exec_insert(sql, vals)
        s_id = 2000 + int(location_id)

        site_code = 'GGT{}{}'.format(location.st, str(s_id))
        geo = get_gps_coordinates(location.addr1, location.city, location.st, location.zip, location.addr2)

        sql_2 = """UPDATE locations
                SET 
                    site_code = %s,
                    lat = %s,
                    lng = %s
                WHERE id = %s"""

        vals_2 = (site_code, geo['lat'], geo['lng'], location_id)
        update = await exec_update(sql_2, vals_2)
        if update:
            return location_id
        else:
            return None

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def assign_group(req):
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
        map_id = await exec_insert(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def assign_all_groups(vals):
    try:
        sql = """
               INSERT INTO group_codes_to_locations_mapping
               (
                  group_id, 
                  location_id
               )
               values (%s, %s)
               """
        map_id = await exec_batch_execute(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def assign_service(req):
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
        map_id = await exec_insert(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def assign_all_services(vals):
    try:
        sql = """
               INSERT INTO services_to_locations_mapping
               (
                  location_id, 
                  service_id
               )
               values (%s, %s)
               """
        map_id = await exec_batch_execute(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def remove_group(req):
    try:
        sql = """
               DELETE FROM group_codes_to_locations_mapping WHERE group_id = %s AND location_id = %s
               """
        vals = (
            req.group_id,
            req.location_id
        )
        deleted = await exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def remove_all_group(location_id):
    try:
        sql = """
               DELETE FROM group_codes_to_locations_mapping WHERE location_id = %s
               """
        vals = (
            location_id,
        )
        deleted = await exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def remove_service(req):
    try:
        sql = """
               DELETE FROM services_to_locations_mapping WHERE service_id = %s AND location_id = %s
               """
        vals = (
            req.service_id,
            req.location_id
        )
        deleted = await exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def remove_all_service(location_id):
    try:
        sql = """
               DELETE FROM services_to_locations_mapping WHERE location_id = %s
               """
        vals = (
            location_id,
        )
        deleted = await exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


async def update_location(location):
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
        updated = await exec_update(sql, vals)
        return updated

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR, 
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
            type=c.ERROR,
            function=whoami(),
            row=row,
            error=err
        )

    return s