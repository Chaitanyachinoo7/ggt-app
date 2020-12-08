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
    read_rows
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
async def get_stats_today():
    try:
        sql = """SELECT * FROM todays_location_stats_with_totals_test"""
        return await read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR, 
            function=whoami(), 
            error=err
        )
        return None


async def get_stats_by_date(date):
    try:
        sql = """  SELECT 
    `location_stats_for_dates`.`location_id` AS `location_id`,
    `location_stats_for_dates`.`site_code` AS `site_code`,
    `location_stats_for_dates`.`name` AS `name`,
    `location_stats_for_dates`.`pending_signups` AS `pending_signups`,
    `location_stats_for_dates`.`total_scheduled` AS `total_scheduled`,
    `location_stats_for_dates`.`remaining_scheduled` AS `remaining_scheduled`,
    `location_stats_for_dates`.`checked_in` AS `checked_in`,
    `location_stats_for_dates`.`in_progress` AS `in_progress`,
    `location_stats_for_dates`.`completed` AS `completed`,
    `location_stats_for_dates`.`cancelled` AS `cancelled`,
    `location_stats_for_dates`.`scanned` AS `scanned`,
    `location_stats_for_dates`.`not_scanned` AS `not_scanned`,
    `location_stats_for_dates`.`scan_percentage` AS `scan_percentage`
FROM
     (SELECT 
        `a`.`location_id` AS `location_id`,
            `l`.`site_code` AS `site_code`,
            `l`.`name` AS `name`,
            SUM(IF((`a`.`status` = 'pending'), 1, 0)) AS `pending_signups`,
            COUNT(`a`.`id`) AS `total_scheduled`,
            SUM(IF((`a`.`status` = 'scheduled'), 1, 0)) AS `remaining_scheduled`,
            SUM(IF((`a`.`status` = 'checked_in'), 1, 0)) AS `checked_in`,
            SUM(IF((`a`.`status` = 'test_in_progress'), 1, 0)) AS `in_progress`,
            SUM(IF((`a`.`status` = 'test_completed'), 1, 0)) AS `completed`,
            SUM(IF((`a`.`status` = 'cancelled'), 1, 0)) AS `cancelled`,
            SUM(IF((`t`.`pre_ship_label_scan_dt` IS NOT NULL), 1, 0)) AS `scanned`,
            SUM(IF((ISNULL(`t`.`pre_ship_label_scan_dt`)
                AND (`t`.`id` IS NOT NULL)), 1, 0)) AS `not_scanned`,
           ROUND(((SUM(IF((`t`.`pre_ship_label_scan_dt` IS NOT NULL), 1, 0)) / IF(COUNT(`t`.`id`)=0, 1, COUNT(`t`.`id`))) * 100), 1) AS `scan_percentage`
    FROM
        ((`appointments` `a`
    JOIN `locations` `l` ON ((`l`.`id` = `a`.`location_id`)))
    LEFT JOIN `test_samples` `t` ON ((`t`.`appointment_id` = `a`.`id`)))
    WHERE
        ((CAST(`a`.`scheduled_dt` AS DATE) = %s)
            OR (CAST(`a`.`test_start_dt` AS DATE) =  %s)
            OR (CAST(`a`.`test_end_dt` AS DATE) =  %s))
    GROUP BY `a`.`location_id`
    ORDER BY `l`.`name`) AS `location_stats_for_dates`
UNION SELECT 
    '' AS `location_id`,
    '' AS `site_code`,
    '———ALL———' AS `name`,
    SUM(`location_stats_for_dates`.`pending_signups`) AS `pending_signups`,
    SUM(`location_stats_for_dates`.`total_scheduled`) AS `total_scheduled`,
    SUM(`location_stats_for_dates`.`remaining_scheduled`) AS `remaining_scheduled`,
    SUM(`location_stats_for_dates`.`checked_in`) AS `checked_in`,
    SUM(`location_stats_for_dates`.`in_progress`) AS `in_progress`,
    SUM(`location_stats_for_dates`.`completed`) AS `completed`,
    SUM(`location_stats_for_dates`.`cancelled`) AS `scanned`,
    SUM(`location_stats_for_dates`.`scanned`) AS `not_scanned`,
    SUM(`location_stats_for_dates`.`not_scanned`) AS `not_scanned`,
    ROUND(((SUM(`location_stats_for_dates`.`scanned`) / IF(SUM(`location_stats_for_dates`.`completed`)=0, 1, SUM(`location_stats_for_dates`.`completed`))) * 100),
            1) AS `scan_percentage`
FROM
    (SELECT 
        `a`.`location_id` AS `location_id`,
            `l`.`site_code` AS `site_code`,
            `l`.`name` AS `name`,
            SUM(IF((`a`.`status` = 'pending'), 1, 0)) AS `pending_signups`,
            COUNT(`a`.`id`) AS `total_scheduled`,
            SUM(IF((`a`.`status` = 'scheduled'), 1, 0)) AS `remaining_scheduled`,
            SUM(IF((`a`.`status` = 'checked_in'), 1, 0)) AS `checked_in`,
            SUM(IF((`a`.`status` = 'test_in_progress'), 1, 0)) AS `in_progress`,
            SUM(IF((`a`.`status` = 'test_completed'), 1, 0)) AS `completed`,
            SUM(IF((`a`.`status` = 'cancelled'), 1, 0)) AS `cancelled`,
            SUM(IF((`t`.`pre_ship_label_scan_dt` IS NOT NULL), 1, 0)) AS `scanned`,
            SUM(IF((ISNULL(`t`.`pre_ship_label_scan_dt`)
                AND (`t`.`id` IS NOT NULL)), 1, 0)) AS `not_scanned`,
           ROUND(((SUM(IF((`t`.`pre_ship_label_scan_dt` IS NOT NULL), 1, 0)) / IF(COUNT(`t`.`id`)=0, 1, COUNT(`t`.`id`))) * 100), 1) AS `scan_percentage`
    FROM
        ((`appointments` `a`
    JOIN `locations` `l` ON ((`l`.`id` = `a`.`location_id`)))
    LEFT JOIN `test_samples` `t` ON ((`t`.`appointment_id` = `a`.`id`)))
    WHERE
        ((CAST(`a`.`scheduled_dt` AS DATE) =  %s)
            OR (CAST(`a`.`test_start_dt` AS DATE) =  %s)
            OR (CAST(`a`.`test_end_dt` AS DATE) =  %s))
    GROUP BY `a`.`location_id`
    ORDER BY `l`.`name`) AS `location_stats_for_dates`;"""
        vals = (date, date, date, date, date, date)
        return await read_rows(sql, vals)

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