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

from ggt.models.data_models.data_types import (
    PatientStatusEnum
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

def get_patient_drilldown_by_date(location_id, date, status):
    if status == PatientStatusEnum.scanned.value:
        where_clause = " AND (t.pre_ship_label_scan_dt IS NOT NULL)"
    elif status == PatientStatusEnum.not_scanned.value:
        where_clause = " AND (ISNULL(t.pre_ship_label_scan_dt) AND (t.id IS NOT NULL))"
    elif status == PatientStatusEnum.total_scheduled.value:
        where_clause = ""
    else:
        where_clause = "AND a.status = '{}'".format(status)
    try:
        sql = """  SELECT
                        p.id AS patient_id,
                        p.first_name AS first_name,
                        p.middle_name AS middle_name,
                        p.last_name AS last_name,
                        p.gender AS gender,
                        p.height_ft AS height_ft,
                        p.height_in AS height_in,
                        p.weight_lb AS weight_lb,
                        (CASE
                            WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
                            WHEN (p.race = 'race_asian') THEN 'Asian'
                            WHEN (p.race = 'race_black') THEN 'Black or African American'
                            WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
                            WHEN (p.race = 'race_other') THEN 'Other'
                            WHEN (p.race = 'race_white') THEN 'White'
                            ELSE 'Unknown'
                        END) AS race,
                        (CASE
                            WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
                            WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
                            WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
                            ELSE 'Unknown'
                        END) AS ethnicity,
                        p.addr1 AS addr1,
                        p.addr2 AS addr2,
                        p.addr3 AS addr3,
                        p.city AS city,
                        p.county AS county,
                        p.st AS st,
                        p.zip AS zip,
                        p.dob AS dob,
                        p.phone_number AS phone_number,
                        p.phone_number_verified AS phone_number_verified,
                        p.email AS email,
                        p.email_verified AS email_verified,
                        p.create_dt AS register_dt,
                        p.token AS token,
                        q.symptom_fever AS symptom_fever,
                        q.symptom_shortness_breath AS symptom_shortness_breath,
                        q.symptom_cough AS symptom_cough,
                        q.symptom_chest_pain AS symptom_chest_pain,
                        q.symptom_lack_of_smell AS symptom_lack_of_smell,
                        q.symptom_other_breathing AS symptom_other_breathing,
                        q.covid_contact AS covid_contact,
                        q.prescription_use AS prescription_use,
                        q.heart_disease AS heart_disease,
                        q.diabetes AS diabetes,
                        q.respiratory_diseases AS respiratory_diseases,
                        q.autoimmune_disease AS autoimmune_disease,
                        q.other_chronic AS other_chronic,
                        q.allergies AS allergies,
                        '' AS insurance_photo,
                        q.insurance_details,
                        a.id AS appointment_id,
                        a.scheduled_dt AS scheduled_dt,
                        a.check_in_dt AS check_in_dt,
                        a.location_id AS location_id,
                        a.group_code AS group_code,
                        a.test_start_dt AS test_start_dt,
                        a.test_end_dt AS test_end_dt,
                        a.vial_id,
                        a.total_cost AS total_cost,
                        a.billed_amount AS billed_amount,
                        a.wp_customer_info_id AS wp_customer_info_id,
                        a.status AS appointment_status,
                        t.provider_id AS provider_id,
                        t.sample_collection_location_id AS sample_collection_location_id,
                        t.sample_collection_start_dt AS sample_collection_start_dt,
                        t.sample_collection_end_dt AS sample_collection_end_dt,
                        t.lab_physical_submission_dt AS lab_pysical_submission_dt,
                        t.lab_electronic_submission_dt AS lab_electronic_submission_dt,
                        t.lab_result_receive_dt AS lab_result_receive_dt,
                        t.test_result AS test_result,
                        t.consultation_status AS consultation_status,
                        t.consultation_notes AS consultation_notes,
                        t.status AS test_status,
                        l.id AS location_id,
                        l.site_code AS site_code,
                        l.name AS loc_name,
                        l.name AS account,
                        l.addr1 AS loc_addr1,
                        l.addr2 AS loc_addr2,
                        l.city AS loc_city,
                        l.st AS loc_st,
                        l.zip AS loc_zip,
                        l.time_zone AS time_zone,
                        l.test_type_offered AS test_type_offered,
                        r.sms_sent,
                        r.sms_dt,
                        r.email_sent,
                        r.email_dt,
                        r.voice_sent,
                        r.voice_dt,
                        r.group_notify,
                        r.overall_status,
                        c.id AS consultation_id,
                        c.notes AS consultation_notes,
                        c.start_dt AS consultation_start_dt,
                        c.end_dt AS consultation_end_dt,
                        c.provider_external_id AS provider_id,
                        c.consultation_type_code AS consultation_type_code,
                        c.resolution_code AS resolution_code,
                        u.name AS provider_name,
                        u.given_name AS provider_given_name,
                        u.family_name AS provider_family_name,
                        u.email AS provider_email,
                        u.email_verified AS provider_email_verified,
                        u.picture AS provider_image_url,
                        i.id AS insurance_id,
                        i.insurance_carrier AS insurance_carrier,
                        i.group_number AS insurance_group_number,
                        i.member_number AS insurance_member_number,
                        i.validated AS insurance_validated
                    FROM
                        patients p
                            LEFT JOIN
                        patient_questionnaires q ON (p.id = q.patient_id)
                            LEFT JOIN
                        appointments a ON (p.id = a.patient_id)
                            LEFT JOIN
                        test_samples t ON (a.id = t.id)
                            LEFT JOIN
                        locations l ON (a.location_id = l.id)
                            LEFT JOIN
                        result_notification_campaigns r ON (t.id = r.test_id)
                            LEFT JOIN
                        patient_consultations c ON a.id = c.appointment_id
                            LEFT JOIN
                        ggt_users u ON u.external_id = c.provider_external_id
                            LEFT JOIN
                        insurance_info i ON p.id = i.patient_id
                    WHERE
                        1 = 1
                            AND p.id IN (SELECT
                                a.patient_id
                            FROM
                                appointments a
                                    LEFT JOIN
                                test_samples t ON (t.appointment_id = a.id)
                            WHERE
                                a.location_id = %s
                                    AND ((CAST(a.scheduled_dt AS DATE) = %s)
                                    OR (CAST(a.test_start_dt AS DATE) = %s)
                                    OR (CAST(a.test_end_dt AS DATE) = %s))
                                    {});
                                    """.format(where_clause)

        vals = (location_id, date, date, date)
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
