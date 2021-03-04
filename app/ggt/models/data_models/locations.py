from typing import List, Set, Dict, Tuple, Optional

from ggt.lib.adapters.auth0_config import META_KEY, ORGANIZATION_KEY
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
    exec_batch_execute,
    replica_read_row,
    replica_read_rows
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
                image_thumbnail,
                accepts_bookings,
                accepts_walkins,
                operator,
                website,
                open_hours,
                phone_number,
                is_external
            FROM 
                locations 
            WHERE 
                id = %s 
            LIMIT 1
        """
        vals = (location_id,)
        row = replica_read_row(sql, vals)
        return __map_row_to_location(row)

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
        rows = replica_read_rows(sql, vals)
        return __map_rows_to_services_list(rows)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )
        return None


def get_states():
    try:
        sql = "SELECT * FROM states WHERE active = 1;"
        return replica_read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_all_locations_without_thumbnail(org_id):
    try:
        sql = """SELECT 
                    l.id,
                    l.site_code,
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
                    l.accepts_bookings,
                    l.accepts_walkins,
                    l.operator,
                    l.website,
                    l.open_hours,
                    l.phone_number,
                    l.is_external,
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
                    group by gm.location_id) gp on l.id = gp.location_id
                WHERE l.org_id = %s
            """
        vals = (org_id, )
        return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_all_locations():
    try:
        sql = "SELECT * FROM locations"
        return replica_read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def search_locations(account, group_code, site_code, location_name, org_id, id=None, st=""):
    try:
        where_conditions = 'AND org.id = {} and org.is_active = 1'.format(org_id)
        if account != '':
            where_conditions = "{} AND g.account LIKE '%{}%'".format(
                where_conditions, account)
        if group_code != '':
            where_conditions = "{} AND gp.group_codes LIKE '%{}%'".format(
                where_conditions, group_code)
        if site_code != '':
            where_conditions = "{} AND l.site_code LIKE '%{}%'".format(
                where_conditions, site_code)
        if location_name != '':
            where_conditions = "{} AND l.name LIKE '%{}%'".format(
                where_conditions, location_name)
        if id:
            where_conditions = "{} AND l.id = {}".format(where_conditions, id)
        if st != "":
            where_conditions = "{} AND l.st = '{}'".format(where_conditions, st)

        limit = 500

        sql = """SELECT DISTINCT
					org.id as org_di,
                    org.name as org_name,
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
                    l.type,
                    l.accepts_bookings,
                    l.accepts_walkins,
                    l.operator,
                    l.website,
                    l.open_hours,
                    l.phone_number,
                    l.is_external,
                    s.service_names,
                    gp.group_accounts,
                    gp.group_codes,
                    s.service_ids,
                    gp.group_ids
                FROM
                    locations l
                        LEFT JOIN
                    (SELECT 
                        sm.location_id,
                            GROUP_CONCAT(DISTINCT sc.service_name) AS service_names,
                            GROUP_CONCAT(DISTINCT sc.id) AS service_ids
                    FROM
                        services_to_locations_mapping sm
                    LEFT JOIN services_catalog sc ON sm.service_id = sc.id
                    GROUP BY sm.location_id) s ON l.id = s.location_id
                        LEFT JOIN
                    (SELECT 
                        gm.location_id,
                            GROUP_CONCAT(DISTINCT g.id) AS group_ids,
                            GROUP_CONCAT(DISTINCT g.account) AS group_accounts,
                            GROUP_CONCAT(DISTINCT g.group_code) AS group_codes
                    FROM
                        group_codes_to_locations_mapping gm
                    LEFT JOIN groups g ON gm.group_id = g.id
                    GROUP BY gm.location_id) gp ON l.id = gp.location_id
                    JOIN organizations org ON l.org_id = org.id
                        WHERE 1=1
                            {}
                        LIMIT {}
        """.format(where_conditions, limit)
        res = replica_read_rows(sql)
        return __process_location_search(res)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_location(location, organization_id):
    try:
        if organization_id is None:
            return None
        sql = """
               INSERT INTO locations
               (
                   site_code,
                   org_id,
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
                   image_thumbnail,
                   accepts_bookings,
                   accepts_walkins,
                   operator,
                   phone_number,
                   website,
                   open_hours,
                   is_external,
                   country
               )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
               %s, %s, %s, %s, %s)
               """
        vals = (
            location.site_code,
            organization_id,
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
            location.image_thumbnail,
            location.accepts_bookings,
            location.accepts_walkins,
            location.operator,
            location.phone_number,
            location.website,
            location.open_hours,
            location.is_external,
            location.country
        )
        location_id = exec_insert(sql, vals)

        site_code = 'GGT{}{}'.format(location.st, location_id)
        
        geo = get_gps_coordinates(
           location.addr1, location.city, location.st, location.zip, location.addr2)
        # geo={}
        # geo['lat']=0
        # geo['lng']=0
        sql_2 = """UPDATE locations
                SET 
                    site_code = %s,
                    lat = %s,
                    lng = %s
                WHERE id = %s"""

        vals_2 = (site_code, geo['lat'], geo['lng'], location_id)
        update = exec_update(sql_2, vals_2)
        if update:
            return {'location_id': location_id, 'site_code': site_code}
        else:
            return None

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def assign_all_groups(vals):
    try:
        sql = """
               INSERT INTO group_codes_to_locations_mapping
               (
                  group_id, 
                  location_id
               )
               values (%s, %s)
               """
        map_id = exec_batch_execute(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def assign_all_services(vals):
    try:
        sql = """
               INSERT INTO services_to_locations_mapping
               (
                  location_id, 
                  service_id
               )
               values (%s, %s)
               """
        map_id = exec_batch_execute(sql, vals)
        return map_id

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def remove_all_group(location_id):
    try:
        sql = """
               DELETE FROM group_codes_to_locations_mapping WHERE location_id = %s
               """
        vals = (
            location_id,
        )
        deleted = exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def remove_all_service(location_id):
    try:
        sql = """
               DELETE FROM services_to_locations_mapping WHERE location_id = %s
               """
        vals = (
            location_id,
        )
        deleted = exec_delete(sql, vals)
        return deleted

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_location(location):
    try:
        sql = """
               UPDATE locations SET
                   name = %s,
                   test_type_offered = %s,
                   status = %s,
                   type = %s,
                   billing_type = %s,
                   collect_insurance_info = %s,
                   allow_insurance_skip = %s,
                   collect_upfront_payment = %s,
                   accepts_bookings = %s,
                   accepts_walkins = %s,
                   operator = %s,
                   phone_number = %s,
                   website = %s,
                   open_hours = %s,
                   is_external = %s
               WHERE id =  %s
                        """
        vals = (
            location.location_name,
            location.test_type_offered,
            location.status,
            location.type,
            location.billing_type,
            location.collect_insurance_info,
            location.allow_insurance_skip,
            location.collect_upfront_payment,
            location.accepts_bookings,
            location.accepts_walkins,
            location.operator,
            location.phone_number,
            location.website,
            location.open_hours,
            location.is_external,
            location.id
        )
        updated = exec_update(sql, vals)
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
def __process_location_search(res):
    for row in res:
        service_ids = row['service_ids']
        group_ids = row['group_ids']
        if service_ids is not None:
            service_ids = service_ids.split(',')
            service_ids = [int(x) for x in service_ids]
            row['service_ids'] = service_ids
        else:
            row['service_ids'] = []
        if group_ids is not None:
            group_ids = group_ids.split(',')
            group_ids = [int(x) for x in group_ids]
            row['group_ids'] = group_ids
        else:
            row['group_ids'] = []
    return res


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
        loc.image_thumbnail = row['accepts_bookings']
        loc.image_thumbnail = row['accepts_walkins']
        loc.image_thumbnail = row['operator']
        loc.image_thumbnail = row['phone_number']
        loc.image_thumbnail = row['website']
        loc.image_thumbnail = row['open_hours']
        loc.image_thumbnail = row['is_external']

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
