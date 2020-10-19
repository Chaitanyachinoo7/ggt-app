DELETE t , a , q , q2 FROM patients p
        INNER JOIN
    test_samples t ON (t.patient_id = p.id)
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires q ON (q.patient_id = p.id)
        INNER JOIN
    patient_questionnaires_ext q2 ON (q2.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND t.test_result IS NULL
    AND t.id <> 0
    AND a.id <> 0
    AND q.id <> 0
    AND q2.id <> 0;
--    
    DELETE t , a , q FROM patients p
        INNER JOIN
    test_samples t ON (t.patient_id = p.id)
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires q ON (q.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND t.test_result IS NULL
    AND t.id <> 0
    AND a.id <> 0
    AND q.id <> 0;
    --
    DELETE t , a , q2 FROM patients p
        INNER JOIN
    test_samples t ON (t.patient_id = p.id)
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires_ext q2 ON (q2.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND t.test_result IS NULL
    AND t.id <> 0
    AND a.id <> 0
    AND q2.id <> 0;
    --
    DELETE a , q, q2 FROM patients p
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires q ON (q.patient_id = p.id)
        INNER JOIN
    patient_questionnaires_ext q2 ON (q2.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND a.id <> 0
    AND q.id <> 0
    AND q2.id <> 0;
    --
        DELETE a , q FROM patients p
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires q ON (q.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND a.id <> 0
    AND q.id <> 0;
    --
        DELETE a , q2 FROM patients p
        INNER JOIN
    appointments a ON (a.patient_id = p.id)
        INNER JOIN
    patient_questionnaires_ext q2 ON (q2.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND a.id <> 0
    AND q2.id <> 0;
    --
        DELETE a FROM patients p
        INNER JOIN
    appointments a ON (a.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND a.id <> 0;
--
        DELETE q , q2 FROM patients p
        INNER JOIN
    patient_questionnaires q ON (q.patient_id = p.id)
        INNER JOIN
    patient_questionnaires_ext q2 ON (q2.patient_id = p.id) 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND q.id <> 0
    AND q2.id <> 0;
    --
    DELETE p FROM patients p 
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND p.id <> 0;
    --

    DELETE p FROM patients p
        INNER JOIN
    test_samples t ON (t.patient_id = p.id)
WHERE
    p.last_name IN ('subasinghe' , 'test', 'gaber')
    AND t.test_result IS NULL
    AND p.id <> 0;

-- delete from    signups where phone_number = '+18018602474' and id <> 0