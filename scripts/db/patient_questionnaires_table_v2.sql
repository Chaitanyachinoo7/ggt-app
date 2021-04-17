-- ggt_prod.patient_questionnaires v2
-- adding new columns for new symptoms

ALTER TABLE patient_questionnaires ADD symptom_fatigue tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_muscle_body_aches tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_headache tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_sore_throat tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_congestion_runny_nose tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_nausea_vomitting tinyint(4) DEFAULT 0
ALTER TABLE patient_questionnaires ADD symptom_diarrhea tinyint(4) DEFAULT 0
