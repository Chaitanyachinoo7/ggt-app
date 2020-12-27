from typing import List, Set, Dict, Tuple, Optional
from contextlib import suppress
from datetime import date
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
    GgtScheduleSlot,
    GgtDateTimeLocation,
    GgtServiceCatalogItem
)


########################################################################################################
# [Public] functions
########################################################################################################
def create_schedule_entry(location_id, start_dt, end_dt, duration, status):
    try:
        sql = """
            INSERT INTO schedules 
                (location_id, start_dt, end_dt, duration, status) 
            VALUES 
                (%s, %s, %s, %s, %s)
        """
        vals = (location_id, start_dt, end_dt, duration, status)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            location_id=location_id,
            start_dt=start_dt,
            end_dt=end_dt,
            duration=duration,
            status=status,
            error=err
        )
        return None


def get_schedule_generation_rules_by_location_id(location_id):
    try:
        sql = """
            SELECT 
                l.site_code, 
                l.time_zone, 
                l.time_zone_offset, 
                l.status, 
                r.id,
                r.rule_type,
                r.location_id,
                r.slot_increment,
                r.local_start_time,
                r.local_end_time, 
                r.sun,
                r.mon,
                r.tue,
                r.wed,
                r.thu,
                r.fri,
                r.sat,
                r.slot_multiplier,
                r.active_local_start_dt, 
                r.active_local_end_dt
            FROM
                schedule_generation_rules r
                join locations l on (l.id = r.location_id)
            WHERE
                location_id = %s
            ORDER BY rule_type ASC

        """
        vals = (location_id,)
        return read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            location_id=location_id,
            error=err
        )
        return None


def add_schedule_generation_rule(data):
    try:
        sql = """
        INSERT INTO schedule_generation_rules
        (
            location_id,
            rule_type,
            slot_increment,
            local_start_time,
            local_end_time,
            sun,
            mon,
            tue,
            wed,
            thu,
            fri,
            sat,
            slot_multiplier,
            active_local_start_dt,
            active_local_end_dt
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        vals = (
            data.location_id,
            data.rule_type,
            data.slot_increment,
            data.local_start_time,
            data.local_end_time,
            data.sun,
            data.mon,
            data.tue,
            data.wed,
            data.thu,
            data.fri,
            data.sat,
            data.slot_multiplier,
            data.active_local_start_dt,
            data.active_local_end_dt)

        if exec_insert(sql, vals):
            return True
        else:
            return False

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_schedule_generation_rule(data):
    try:
        sql = """
        UPDATE schedule_generation_rules
        SET 
            rule_type = %s,
            location_id = %s,
            slot_increment = %s,
            local_start_time = %s,
            local_end_time = %s,
            sun = %s,
            mon = %s,
            tue = %s,
            wed = %s,
            thu = %s,
            fri = %s,
            sat = %s,
            slot_multiplier = %s,
            active_local_start_dt = %s,
            active_local_end_dt = %s,
            modify_dt = NOW()
        WHERE
            id = %s
        """
        vals = (
            data.rule_type,
            data.location_id,
            data.slot_increment,
            data.local_start_time,
            data.local_end_time,
            data.sun,
            data.mon,
            data.tue,
            data.wed,
            data.thu,
            data.fri,
            data.sat,
            data.slot_multiplier,
            data.active_local_start_dt,
            data.active_local_end_dt,
            data.id
        )

        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def delete_schedule_entries_by_location_id(location_id):
    try:
        sql = """
        DELETE FROM 
            schedules
        WHERE
            location_id = %s
            AND status = 'available'
            AND id <> 0
        """
        vals = (location_id,)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )
        return None


def trim_schedule_generation_rules_start_dt(location_id, new_dt):
    try:
        sql = """
        UPDATE schedule_generation_rules
        SET 
        active_local_start_dt = %s
        WHERE
            location_id = %s
            AND id <> 0 AND DATEDIFF(%s , active_local_start_dt) > 2
        """
        vals = (new_dt, location_id, new_dt)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            function=whoami(),
            error=err
        )
        return None


def delete_schedule_entries_by_location_id_for_date(location_id, date_str):
    try:
        sql = """
        DELETE FROM schedules 
        WHERE
            location_id = %s
            AND DATE(start_dt) = %s
            AND id <> 0
        """
        vals = (location_id, date_str)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            date_str=date_str,
            function=whoami(),
            error=err
        )
        return None


def delete_schedule_generation_rule(id):
    try:
        sql = """
        DELETE FROM 
            schedule_generation_rules
        WHERE
            id = %s
        """
        vals = (id,)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_available_dates(group_code):
    try:
        sql = """
        SELECT DISTINCT
            DATE(s.start_dt) AS available_date
        FROM
            schedules s
        WHERE
            location_id IN (SELECT 
                    m.location_id
                FROM
                    group_codes_to_locations_mapping m
                        INNER JOIN
                    groups g ON (g.id = m.group_id)
                WHERE
                    g.group_code = %s)
                AND status = 'available'
                AND (CAST(s.start_dt AS DATE) >= CAST(CONVERT_TZ(NOW(), '+00:00', '-06:00') AS DATE))
        ORDER BY DATE(start_dt)
        """
        vals = (group_code,)
        return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_all_available_dtl(group_code):
    return __get_all_available_dtl(group_code)


def get_available_locations(date_str, group_code):
    return __get_available_locations_by_date_near_lat_lng(32.779167, 96.808891, 100000, date_str, group_code, True)


def get_available_locations_near_lat_lng(lat, lng, radius, date_str, group_code, map_thumbnail=False):
    return __get_available_locations_by_date_near_lat_lng(lat, lng, radius, date_str, group_code, map_thumbnail)


def get_processing_averages_by_location():
    try:
        sql = """
            SELECT 
                dtrwl.location_id AS location_id,
                (CASE
                    WHEN (AVG(HOUR(dtrwl.sample_processing_time)) > 48) THEN 48
                    ELSE CAST(AVG(HOUR(dtrwl.sample_processing_time))
                        AS DECIMAL (10 , 1 ))
                END) AS average_processing_time
            FROM
                detailed_test_results_with_locations dtrwl
            WHERE
                ((TO_DAYS(NOW()) - TO_DAYS(dtrwl.lab_result_receive_dt)) < 5)
            GROUP BY dtrwl.location_id
        """
        # ORDER BY l.city
        return replica_read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_available_times(location_id, date):
    try:
        sql = """
            SELECT DISTINCT 
                time(start_dt) as start_time, 
                id, 
                start_dt, 
                end_dt, 
                status 
            FROM 
                schedules 
            WHERE 
                location_id = %s 
                AND status = 'available' 
                AND date(start_dt) IN (%s) 
                AND start_dt >= CONVERT_TZ(NOW(), '+00:00', '-06:00')
            ORDER BY id
        """
        vals = (location_id, date)
        '''
        log_generic(
            type=c.INFO,
            function=whoami(),
            location_id=location_id,
            date=date,
            info='looking_up_available_times'
        )
        '''
        return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_slot_information(slot_id):
    try:
        sql = """
            SELECT 
                id, 
                location_id, 
                start_dt, 
                end_dt, 
                duration, 
                status, 
                appointment_id 
            FROM 
                schedules 
            WHERE 
                id = %s
        """
        vals = (slot_id,)

        row = replica_read_row(sql, vals)
        slot = GgtScheduleSlot()
        slot.id = row['id']
        slot.location_id = row['location_id']
        slot.start_dt = row['start_dt']
        slot.end_dt = row['end_dt']
        slot.duration = row['duration']
        slot.status = row['status']
        slot.appointment_id = row['appointment_id']

        '''
        log_generic(
            type=c.INFO,
            function=whoami(),
            slot_id=slot_id,
            data=slot,
            info='looking_up_slot_info'
        )
        '''

        return slot

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_slot_information(slot_id, appointment_id):
    try:
        sql = """
            UPDATE 
                schedules 
            SET 
                appointment_id = %s, 
                status = 'booked'
            WHERE 
                id = %s
        """
        vals = (appointment_id, slot_id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            slot_id=slot_id,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )
        return None


def add_schedule_entries(rows):
    try:
        sql = """
            INSERT INTO 
                schedules (
                    location_id, 
                    start_dt, 
                    end_dt, 
                    time_zone, 
                    time_zone_offset, 
                    duration, 
                    status
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return exec_batch_execute(sql, rows)

    except Exception as err:
        print(c.ERROR, err)


def get_slots_matching_dt_list(dt_list, location_id):
    slot_list = []
    try:
        format_strings = ','.join(['%s'] * len(dt_list))

        sql = """
            SELECT 
                id,
                location_id,
                start_dt,
                end_dt,
                duration,
                status,
                appointment_id
            FROM
                schedules
            WHERE
                location_id = {}
                AND start_dt IN ({})
        """.format(location_id, format_strings)

        vals = tuple(dt_list)

        rows = replica_read_rows(sql, vals)
        if rows:
            for row in rows:
                slot = GgtScheduleSlot()
                slot.id = row['id']
                slot.location_id = row['location_id']
                slot.start_dt = row['start_dt']
                slot.end_dt = row['end_dt']
                slot.duration = row['duration']
                slot.status = row['status']
                slot.appointment_id = row['appointment_id']
                slot_list.append(slot)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return slot_list


########################################################################################################
# [Protected] functions
########################################################################################################
def __get_available_locations_by_date_near_lat_lng(lat, lng, radius, date_str, group_code, map_thumbnail):
    try:
        map_thumbnail_field = 'l.image_thumbnail,' if map_thumbnail else "'' as image_thumbnail,"
        sql = """
        SELECT 
            l.id AS location_id,
            l.name,
            l.addr1,
            l.addr2,
            l.city,
            l.st,
            l.zip,
            l.lat,
            l.lng,
            (3963 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(l.lat)) * COS(RADIANS(l.lng) - RADIANS(%s)) + SIN(RADIANS(%s)) * SIN(RADIANS(l.lat)))) AS distance,
            {}
            l.billing_type,
            l.collect_insurance_info,
            l.allow_insurance_skip,
            l.collect_upfront_payment,
            c.id AS service_id,
            c.service_code,
            c.service_name,
            c.price,
            c.selfpay_amount,
            c.copay_amount,
            c.insurance_amount,
            MIN(smc.first_available_slot) AS first_date_time_available,
            smc.available_slots_count AS slot_count,
            (CASE
                WHEN (lmc.average_processing_time IS NULL) THEN 48
                ELSE lmc.average_processing_time
            END) AS average_processing_time,
            l.accepts_bookings,
            l.accepts_walkins,
            l.operator,
            l.phone_number,
            l.website,
            l.open_hours,
            l.is_external
        FROM
            locations l
                LEFT JOIN
            services_to_locations_mapping m ON (m.location_id = l.id)
                LEFT JOIN
            services_catalog c ON (c.id = m.service_id)
                LEFT JOIN
            schedules_metrics_cache smc ON (smc.location_id = l.id)
                LEFT JOIN
            locations_metrics_cache lmc ON (lmc.location_id = l.id)
        WHERE   
            1=1
                AND l.status = 'enabled'
                AND smc.first_available_slot IS NOT NULL
                AND smc.first_available_slot >= CONVERT_TZ(NOW(), '+00:00', '-06:00')
                AND (3963 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(l.lat)) * COS(RADIANS(l.lng) - RADIANS(%s)) + SIN(RADIANS(%s)) * SIN(RADIANS(l.lat)))) < %s
                AND l.id IN (SELECT 
                    glm.location_id
                FROM
                    group_codes_to_locations_mapping glm
                        INNER JOIN
                    groups g ON (g.id = glm.group_id)
                WHERE
                    g.group_code = %s)
        GROUP BY l.id
        ORDER BY distance    
        """.format(map_thumbnail_field)

        vals = (lat, lng, lat, lat, lng, lat, radius, group_code)

        return __map_rows_to_dtl_list(
            read_rows(sql, vals)
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            group_code=group_code,
            date=date_str,
            error=err
        )
        return None


def __get_all_available_dtl(group_code):
    try:
        sql = """
        SELECT 
            l.id AS location_id,
            l.name,
            l.addr1,
            l.addr2,
            l.city,
            l.st,
            l.zip,
            l.lat,
            l.lng,
            l.image_thumbnail,
            l.billing_type,
            l.collect_insurance_info,
            l.allow_insurance_skip,
            l.collect_upfront_payment,
            c.id AS service_id,
            c.service_code,
            c.service_name,
            c.price,
            c.selfpay_amount,
            c.copay_amount,
            c.insurance_amount,
            smc.first_available_slot AS first_date_time_available,
            smc.available_slots_count AS slot_count,
            (CASE
                WHEN (lmc.average_processing_time IS NULL) THEN 48
                ELSE lmc.average_processing_time
            END) AS average_processing_time,
            l.accepts_bookings,
            l.accepts_walkins,
            l.operator,
            l.phone_number,
            l.website,
            l.open_hours,
            l.is_external
        FROM
            locations l
                LEFT JOIN
            services_to_locations_mapping m ON (m.location_id = l.id)
                LEFT JOIN
            services_catalog c ON (c.id = m.service_id)
                LEFT JOIN
            schedules_metrics_cache smc ON (smc.location_id = l.id)
                LEFT JOIN
            locations_metrics_cache lmc ON (lmc.location_id = l.id)
        WHERE
            l.status = 'enabled'
                AND smc.local_scheduled_date >= CONVERT_TZ(NOW(), '+00:00', '-06:00')
                AND l.id IN (SELECT 
                    glm.location_id
                FROM
                    group_codes_to_locations_mapping glm
                        INNER JOIN
                    groups g ON (g.id = glm.group_id)
                WHERE
                    g.group_code = %s)   
        """

        vals = (group_code,)

        return __map_rows_to_dtl_list(
            replica_read_rows(sql, vals)
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            group_code=group_code,
            error=err
        )
        return None


def __map_rows_to_dtl_list(rows):
    dtl_list: List[GgtDateTimeLocation] = list()

    if rows is None:
        return dtl_list

    try:
        _temp: Dict[int, GgtDateTimeLocation] = dict()
        for row in rows:
            dtl, svc = __map_row_to_dtl(row)

            if dtl.location.id not in _temp:
                _temp[dtl.location.id] = dtl

            _temp[dtl.location.id].location.services_available.append(svc)

        for key in _temp:
            dtl_list.append(
                _temp[key]
            )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            # rows=rows,
            error=err
        )

    return dtl_list


def __map_row_to_dtl(row):
    dtl = None
    svc = None

    if row is None:
        return dtl, svc

    try:
        dtl = GgtDateTimeLocation()
        dtl.location.id = row['location_id']
        dtl.location.name = row['name']
        dtl.location.addr1 = row['addr1']
        dtl.location.addr2 = row['addr2']
        dtl.location.city = row['city']
        dtl.location.st = row['st']
        dtl.location.zip = row['zip']
        dtl.location.lat = row['lat']
        dtl.location.lng = row['lng']
        dtl.location.image_thumbnail = row['image_thumbnail']
        dtl.location.billing_type = row['billing_type']
        dtl.location.collect_insurance_info = True if row['collect_insurance_info'] else False
        dtl.location.allow_insurance_skip = True if row['allow_insurance_skip'] else False
        dtl.location.collect_upfront_payment = True if row['collect_upfront_payment'] else False

        dtl.first_date_time_available = row['first_date_time_available']
        dtl.average_processing_time = row['average_processing_time']
        dtl.slot_count = row['slot_count']
        dtl.location.services_available = list()

        svc = GgtServiceCatalogItem()
        svc.id = row['service_id']
        svc.service_code = row['service_code']
        svc.service_name = row['service_name']
        if row['price']:
            svc.price = int(row['price']*100)
        if row['selfpay_amount']:
            svc.selfpay_amount = int(row['selfpay_amount']*100)
        if row['copay_amount']:
            svc.copay_amount = int(row['copay_amount']*100)
        if row['insurance_amount']:
            svc.insurance_amount = int(row['insurance_amount']*100)

        svc.sku = row['service_code']
        if row['price']:
            svc.cost = int(row['selfpay_amount']*100)

        if 'distance' in row:
            dtl.distance = row['distance']

        if 'accepts_bookings' in row:
            dtl.accepts_bookings = row['accepts_bookings']
        if 'accepts_walkins' in row:
            dtl.accepts_walkins = row['accepts_walkins']
        if 'operator' in row:
            dtl.operated_by = row['operator']
        if 'phone_number' in row:
            dtl.external_phone = row['phone_number']
        if 'website' in row:
            dtl.website = row['website']
        if 'open_hours' in row:
            dtl.open_hours = row['open_hours']
        if 'is_external' in row:
            dtl.is_external = row['is_external']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            row=row,
            error=err
        )

    return dtl, svc
