CREATE TABLE ggv_payments (
    id int(11) AUTO_INCREMENT PRIMARY KEY,
    patient_id int(11) NOT NULL,
    payment_id varchar(200) NOT NULL,
    status varchar(20),
    create_dt datetime default CURRENT_TIMESTAMP,
    update_dt datetime default CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
) ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX payment_id_idx ON ggv_payments(payment_id);



