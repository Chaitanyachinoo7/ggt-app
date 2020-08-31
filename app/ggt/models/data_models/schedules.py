from datetime import date
from ggt.lib.utils import (
    log_generic
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    exec_batch_execute
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
        val = (location_id, start_dt, end_dt, duration, status)
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='create_schedule_entry',
            location_id=location_id,
            start_dt=start_dt,
            end_dt=end_dt,
            duration=duration,
            status=status,
            error=err)
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

        """
        val = (location_id,)
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_schedule_generation_rules_by_location_id',
            location_id=location_id,
            error=err)
        return None


def add_schedule_generation_rule(data):
    try:
        sql = """
        INSERT INTO schedule_generation_rules
        (
            location_id,
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
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        vals = (
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
            data.active_local_end_dt)

        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type="error",
            function='add_schedule_generation_rule',
            error=err)
        return None


def delete_schedule_entries_by_location_id(location_id):
    try:
        sql = """
        DELETE FROM 
            schedules
        WHERE
            location_id = %s
            AND id <> 0
        """
        vals = (location_id,)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type="error",
            function='delete_schedule_entries_by_location_id',
            error=err)
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
            type="error",
            function='delete_schedule_generation_rule',
            error=err)
        return None


def get_available_dates(group_code):
    try:
        today = date.today().strftime("%Y-%m-%d")
        sql = """
            SELECT DISTINCT
                DATE(start_dt) AS available_date
            FROM
                schedules
            WHERE
                location_id IN (SELECT 
                        id
                    FROM
                        locations
                    WHERE
                        group_code = %s)
                    AND status = 'available'
                    AND DATE(start_dt) >= %s
            ORDER BY DATE(start_dt)
        """
        val = (group_code, today)
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_dates_available',
            error=err)
        return None


def get_all_available_dtl():
    try:
        sql = """
        SELECT 
            nd.location_id,
            l.account AS account,
            l.name AS name,
            l.addr1 AS addr1,
            l.addr2 AS addr2,
            l.city AS city,
            l.st AS st,
            l.zip AS zip,
            l.lat AS lat,
            l.lng AS lng,
            nd.first_date_available AS first_date_time_available,
            (CASE
                WHEN (pt.average_processing_time IS NULL) THEN 48
                ELSE pt.average_processing_time
            END) AS average_processing_time,
            COUNT(DISTINCT (s.start_dt)) AS slot_count
        FROM
            schedules s
                JOIN
            locations l ON s.location_id = l.id
                LEFT JOIN
            schedule_next_available_location_and_date nd ON (nd.location_id = s.location_id)
                LEFT JOIN
            average_processing_times_for_last_5_days pt ON (pt.location_id = s.location_id)
        WHERE
            DATE(nd.first_date_available) = DATE(s.start_dt)
                AND start_dt >= CONVERT_TZ(NOW(), '+00:00', '-05:00')
                AND s.status = 'available'
                AND l.group_code = '_DEFAULT_'
        GROUP BY nd.location_id , pt.average_processing_time
        """
        return read_rows(sql)

    except Exception as err:
        log_generic(type="info", function='get_all_available_dtl', error=err)
        return None


def get_available_locations(date_str, group_code):
    today = date.today().strftime("%Y-%m-%d")
    if date_str == today:
        return __get_available_locations_for_current_day(date_str, group_code)
    else:
        return __get_available_locations_beyond_current_day(date_str, group_code)
        


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
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type="error",
            function='get_processing_averages_by_location',
            error=err)
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
                AND start_dt >= CONVERT_TZ(NOW(), '+00:00', '-05:00')
            ORDER BY id
        """
        val = (location_id, date)
        log_generic(
            type="info",
            function='get_available_times',
            location_id=location_id,
            date=date,
            info='looking_up_available_times')
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_available_times',
            error=err)
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
        val = (slot_id,)
        '''
        log_generic(type="info", 
                    function='__read_slot_information', 
                    slot_id=slot_id,
                    info='looking_up_slot_info')
        '''
        return read_row(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_slot_information',
            error=err)
        return None


def update_slot_information(slot_id, appointment_id):
    try:
        sql = """
            UPDATE 
                schedules 
            SET 
                appointment_id = %s 
            WHERE 
                id = %s
        """
        val = (appointment_id, slot_id)
        return exec_update(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            slot_id=slot_id,
            appointment_id=appointment_id,
            function='update_slot_information',
            error=err)
        return None


def add_schedule_entries(rows):
    try:
        sql = """
            INSERT INTO schedules
                (location_id, start_dt, end_dt, time_zone, time_zone_offset, duration, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return exec_batch_execute(sql, rows)

    except Exception as err:
        print("err:", err)


########################################################################################################
# [Protected] functions
########################################################################################################
def __get_available_locations_beyond_current_day(date_str, group_code):
    try:
        sql = """
            SELECT 
                s.location_id,
                l.account AS account,
                l.name AS name,
                l.addr1 AS addr1,
                l.addr2 AS addr2,
                l.city AS city,
                l.st AS st,
                l.zip AS zip,
                l.lat AS lat,
                l.lng AS lng,
                MIN(s.start_dt) AS first_date_time_available,
                (CASE
                    WHEN (pt.average_processing_time IS NULL) THEN 48
                    ELSE pt.average_processing_time
                END) AS average_processing_time,
                COUNT(DISTINCT (s.start_dt)) AS slot_count
            FROM
                schedules s
                    JOIN
                locations l ON s.location_id = l.id
                    LEFT JOIN
                average_processing_times_for_last_5_days pt ON (pt.location_id = s.location_id)
            WHERE
                1 AND DATE(s.start_dt) = %s
                    AND s.status = 'available'
                    AND l.group_code = %s
            GROUP BY s.location_id, pt.average_processing_time
        """
        val = (date_str, group_code)
        log_generic(
            type="info",
            function='get_available_locations_beyond_current_day',
            group_code=group_code,
            date=date_str,
            info='looking_up_available_locations_beyond_current_day')
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_available_locations_beyond_current_day',
            group_code=group_code,
            date=date_str,
            error=err)
        return None


def __get_available_locations_for_current_day(date_str, group_code):
    try:
        sql = """
            SELECT 
            nd.location_id,
            l.account AS account,
            l.name AS name,
            l.addr1 AS addr1,
            l.addr2 AS addr2,
            l.city AS city,
            l.st AS st,
            l.zip AS zip,
            l.lat AS lat,
            l.lng AS lng,
            nd.first_date_available AS first_date_time_available,
            (CASE
                WHEN (pt.average_processing_time IS NULL) THEN 48
                ELSE pt.average_processing_time
            END) AS average_processing_time,
            COUNT(DISTINCT (s.start_dt)) AS slot_count
        FROM
            schedules s
                JOIN
            locations l ON s.location_id = l.id
                LEFT JOIN
            schedule_next_available_location_and_date nd ON (nd.location_id = s.location_id)
                LEFT JOIN
            average_processing_times_for_last_5_days pt ON (pt.location_id = s.location_id)
        WHERE
            DATE(nd.first_date_available) = DATE(s.start_dt)
                AND DATE(s.start_dt) = %s
                AND s.status = 'available'
                AND l.group_code = %s
        GROUP BY nd.location_id , pt.average_processing_time
        """
        val = (date_str, group_code)
        log_generic(
            type="info",
            function='get_available_locations_for_current_day',
            group_code=group_code,
            date=date_str,
            info='looking_up_available_locations_for_current_day')
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error",
            function='get_available_locations_for_current_day',
            group_code=group_code,
            date=date_str,
            error=err)
        return None
