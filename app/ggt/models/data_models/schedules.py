from datetime import date
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
            function='__insert_record_schedules', 
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
                id,
                location_id,
                slot_increment,
                start_time,
                end_time,
                DATE(active_start_dt) AS active_start_dt,
                DATE(active_end_dt) AS active_end_dt,
                slot_multiplier
            FROM
                schedule_generation_rules
            WHERE
                location_id = %s
            LIMIT 1
        """
        val = (location_id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(
            type="error", 
            function='__read_record_schedule_generation_rules_by_location_id', 
            location_id=location_id, 
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
        return read_rows(sql,val)

    except Exception as err:
        log_generic(
            type="error", 
            function='get_dates_available', 
            error=err)
        return None



def get_available_locations(date, group_code):
    try:
        sql = """
            SELECT DISTINCT
                s.location_id,
                l.addr1 as addr1,
                l.addr2 as addr2,
                l.city as city,
                l.st as st,
                l.zip as zip,
                l.lat as lat,
                l.lng as lng
            FROM
                schedules s
                    JOIN
                locations l ON s.location_id = l.id
            WHERE
                s.status = 'available'
                    AND DATE(start_dt) IN (%s) 
                    AND l.group_code = %s
        """
        val = (date, group_code)
        log_generic(
            type="info", 
            function='__read_locations_available', 
            group_code=group_code,
            date=date,
            info='looking_up_available_locations')
        return read_rows(sql, val)
    
    except Exception as err:
        log_generic(
            type="error", 
            function='__read_locations_available', 
            group_code=group_code,
            date=date,
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
            ORDER BY id
        """
        val = (location_id, date)
        log_generic(
            type="info", 
            function='__read_times_available', 
            location_id=location_id,
            date=date,
            info='looking_up_available_times')
        return read_rows(sql, val)

    except Exception as err:
        log_generic(
            type="error", 
            function='__read_times_available', 
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
            function='__read_slot_information', 
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
            function='__update_slot_information', 
            error=err)
        return None






########################################################################################################
# [Protected] functions
########################################################################################################

