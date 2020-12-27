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
    (3963 * ACOS(COS(RADIANS(39.049)) * COS(RADIANS(l.lat)) * COS(RADIANS(l.lng) - RADIANS(- 95.6776)) + SIN(RADIANS(39.049)) * SIN(RADIANS(l.lat)))) AS distance,
    '' AS image_thumbnail,
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
        AND (3963 * ACOS(COS(RADIANS(39.049)) * COS(RADIANS(l.lat)) * COS(RADIANS(l.lng) - RADIANS(- 95.6776)) + SIN(RADIANS(39.049)) * SIN(RADIANS(l.lat)))) < 100000
        AND smc.local_scheduled_date = DATE('2020-12-27')
        AND l.id IN (SELECT 
            glm.location_id
        FROM
            group_codes_to_locations_mapping glm
                INNER JOIN
            groups g ON (g.id = glm.group_id)
        WHERE
            g.group_code = '_DEFAULT_')
ORDER BY distance
