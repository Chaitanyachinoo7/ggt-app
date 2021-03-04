create table appointments (
    id int auto_increment primary key,
    scheduled_dt datetime null,
    check_in_dt datetime null,
    pre_consultation_provider_id int null,
    pre_consultation_notes varchar(45) null,
    pre_consultaiton_start_dt datetime null,
    pre_consultation_end_dt datetime null,
    location_id int null,
    group_code varchar(45) null,
    patient_id int null,
    patient_questionnaire_id int null,
    vial_id varchar(45) null,
    test_start_dt datetime null,
    test_end_dt datetime null,
    wp_receipt_token varchar(45) null,
    wp_customer_info_id int null,
    total_cost decimal(13, 2) null,
    billed_amount decimal(13, 2) null,
    status enum (
        'pending',
        'cancelled',
        'scheduled',
        'checked_in',
        'pre_consultation_in_progress',
        'test_in_progress',
        'vial_scanned',
        'test_completed',
        'record_locked',
        'scan_vial_vax',
        'notes',
        'start_vax',
        'end_vax',
        'verify_insurance'
    ) default 'pending' null,
    billing_status enum ('pending', 'billed') default 'pending' null,
    vax_start_dt datetime null,
    vax_notes_dt datetime null,
    vax_end_dt datetime null,
    injection_site varchar(45) null,
    no_adverse_reactions tinyint null,
    lot_no varchar(45) null,
    expiration_date varchar(45) null,
    gtin varchar(45) null,
    sample_collection_location_id int null,
    create_dt datetime default CURRENT_TIMESTAMP null,
    update_dt datetime default CURRENT_TIMESTAMP null,
    constraint fk_appointments_patients1 foreign key (patient_id) references patients (id)
) charset = utf8;
create index fk_appointments_locations1_idx on appointments (location_id);
create index fk_appointments_patient_questionnaires1_idx on appointments (patient_questionnaire_id);
create index fk_appointments_patients1_idx on appointments (patient_id);
create index ix_group_code on appointments (group_code);
create index ix_scheduled_dt on appointments (scheduled_dt);
create index ix_status on appointments (status);
create index ix_vial_id on appointments (vial_id);