from ggt.lib.adapters.auth0_config import META_KEY, ORGANIZATION_KEY
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

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_sms_stats_by_date(date):
    where_statement = "1=1"
    if date != 'all':
        where_statement = "{} and `date(create_dt)` = '{}'".format(where_statement, date)
    try:
        sql = """SELECT 
                        `date(create_dt)` AS date, 
                        `count(date(create_dt))` AS sms_count
                 FROM
                        sms_notification_counts_by_day
                 WHERE
                        {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_email_stats_by_date(date):
    where_statement = "1=1"
    if date != 'all':
        where_statement = "{} and `date(create_dt)` = '{}'".format(where_statement, date)
    try:
        sql = """SELECT 
                        `date(create_dt)` AS date, 
                        `count(date(create_dt))` AS email_count
                 FROM
                        email_notification_counts_by_day
                 WHERE
                        {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_stats_today():
    try:
        sql = """SELECT * FROM todays_location_stats_with_totals_test"""
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_user_activity(req):
    try:
        where_statement = "1=1"
        if req.from_date != "":
            where_statement = "{} AND h.create_dt >= '{}".format(where_statement, req.from_date)
        if req.to_date != "":
            where_statement = "{} AND h.create_dt <= '{}".format(where_statement, req.to_date)
        if req.site_code != "":
            where_statement = "{} AND l.site_code = '{}".format(where_statement, req.site_code)
        sql = """SELECT 
                    h.id AS h_id,
                    h.function AS function_name,
                    h.status AS status,
                    h.vial_id AS val_id,
                    h.workstation_id AS workstation_id,
                    h.create_dt AS create_dt,
                    l.id AS location_id,
                    l.site_code,
                    u.email AS employee_email,
                    u.given_name,
                    u.family_name
                FROM
                    provider_appointment_activity_history h
                        JOIN
                    appointments a ON a.id = h.appointment_id
                        LEFT JOIN
                    locations l ON a.location_id = l.id
                        LEFT JOIN
                    ggt_users u ON u.external_id = h.provider_ext_id
                WHERE
                {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def aging_samples_with_lab_by_ship_date():
    try:
        sql = """SELECT * FROM aging_samples_with_lab_stats_by_ship_date"""
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_stats_by_date(date, organization_id):
    try:

        sql = """SELECT 
                    location_stats_for_dates.location_id AS location_id,
                    location_stats_for_dates.site_code AS site_code,
                    location_stats_for_dates.name AS name,
                    location_stats_for_dates.pending_signups AS pending_signups,
                    location_stats_for_dates.total_scheduled AS total_scheduled,
                    location_stats_for_dates.remaining_scheduled AS remaining_scheduled,
                    location_stats_for_dates.checked_in AS checked_in,
                    location_stats_for_dates.in_progress AS in_progress,
                    location_stats_for_dates.completed AS completed,
                    location_stats_for_dates.cancelled AS cancelled,
                    location_stats_for_dates.scanned AS scanned,
                    location_stats_for_dates.not_scanned AS not_scanned,
                    location_stats_for_dates.scan_percentage AS scan_percentage
                    FROM
                        (SELECT 
                            a.location_id AS location_id,
                                l.site_code AS site_code,
                                l.name AS name,
                                SUM(IF((a.status = 'pending'), 1, 0)) AS pending_signups,
                                COUNT(a.id) AS total_scheduled,
                                SUM(IF((a.status = 'scheduled'), 1, 0)) AS remaining_scheduled,
                                SUM(IF((a.status = 'checked_in'), 1, 0)) AS checked_in,
                                SUM(IF((a.status = 'test_in_progress'), 1, 0)) AS in_progress,
                                SUM(IF((a.status = 'test_completed'), 1, 0)) AS completed,
                                SUM(IF((a.status = 'cancelled'), 1, 0)) AS cancelled,
                                SUM(IF((t.pre_ship_label_scan_dt IS NOT NULL), 1, 0)) AS scanned,
                                SUM(IF((ISNULL(t.pre_ship_label_scan_dt)
                                    AND (t.id IS NOT NULL)), 1, 0)) AS not_scanned,
                            ROUND(((SUM(IF((t.pre_ship_label_scan_dt IS NOT NULL), 1, 0)) / IF(COUNT(t.id)=0, 1, COUNT(t.id))) * 100), 1) AS scan_percentage
                        FROM
                            ((appointments a
                        JOIN locations l ON ((l.id = a.location_id)))
                        LEFT JOIN test_samples t ON ((t.appointment_id = a.id))
                        LEFT JOIN organizations org on l.org_id = org.id)
                        WHERE
                            ((CAST(a.scheduled_dt AS DATE) = %s)
                                OR (CAST(a.test_start_dt AS DATE) =  %s)
                                OR (CAST(a.test_end_dt AS DATE) =  %s))
                                 AND org.id = %s AND org.is_active = 1
                        GROUP BY a.location_id
                        ORDER BY l.name) AS location_stats_for_dates
                    UNION SELECT 
                        '' AS location_id,
                        '' AS site_code,
                        '———ALL———' AS name,
                        SUM(location_stats_for_dates.pending_signups) AS pending_signups,
                        SUM(location_stats_for_dates.total_scheduled) AS total_scheduled,
                        SUM(location_stats_for_dates.remaining_scheduled) AS remaining_scheduled,
                        SUM(location_stats_for_dates.checked_in) AS checked_in,
                        SUM(location_stats_for_dates.in_progress) AS in_progress,
                        SUM(location_stats_for_dates.completed) AS completed,
                        SUM(location_stats_for_dates.cancelled) AS scanned,
                        SUM(location_stats_for_dates.scanned) AS not_scanned,
                        SUM(location_stats_for_dates.not_scanned) AS not_scanned,
                        ROUND(((SUM(location_stats_for_dates.scanned) / IF(SUM(location_stats_for_dates.completed)=0, 1, SUM(location_stats_for_dates.completed))) * 100),
                                1) AS scan_percentage
                    FROM
                        (SELECT 
                            a.location_id AS location_id,
                                l.site_code AS site_code,
                                l.name AS name,
                                SUM(IF((a.status = 'pending'), 1, 0)) AS pending_signups,
                                COUNT(a.id) AS total_scheduled,
                                SUM(IF((a.status = 'scheduled'), 1, 0)) AS remaining_scheduled,
                                SUM(IF((a.status = 'checked_in'), 1, 0)) AS checked_in,
                                SUM(IF((a.status = 'test_in_progress'), 1, 0)) AS in_progress,
                                SUM(IF((a.status = 'test_completed'), 1, 0)) AS completed,
                                SUM(IF((a.status = 'cancelled'), 1, 0)) AS cancelled,
                                SUM(IF((t.pre_ship_label_scan_dt IS NOT NULL), 1, 0)) AS scanned,
                                SUM(IF((ISNULL(t.pre_ship_label_scan_dt)
                                    AND (t.id IS NOT NULL)), 1, 0)) AS not_scanned,
                            ROUND(((SUM(IF((t.pre_ship_label_scan_dt IS NOT NULL), 1, 0)) / IF(COUNT(t.id)=0, 1, COUNT(t.id))) * 100), 1) AS scan_percentage
                        FROM
                            ((appointments a
                        JOIN locations l ON ((l.id = a.location_id)))
                        LEFT JOIN test_samples t ON ((t.appointment_id = a.id))
                        LEFT JOIN organizations org on l.org_id = org.id)
                        WHERE
                            ((CAST(a.scheduled_dt AS DATE) =  %s)
                                OR (CAST(a.test_start_dt AS DATE) =  %s)
                                OR (CAST(a.test_end_dt AS DATE) =  %s))
                                AND org.id = %s AND org.is_active = 1
                        GROUP BY a.location_id
                        ORDER BY l.name) AS location_stats_for_dates;"""
        vals = (date, date, date, organization_id, date, date, date, organization_id)
        return replica_read_rows(sql, vals)

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
