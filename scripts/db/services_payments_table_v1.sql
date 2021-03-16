CREATE TABLE services_payments (
    id int(11) AUTO_INCREMENT PRIMARY KEY,
    service_catalog_id int(11),
    price decimal(13,2) DEFAULT NULL,
    selfpay_amount decimal(13,2) DEFAULT NULL,
    copay_amount decimal(13,2) DEFAULT NULL,
    insurance_amount decimal(13,2) DEFAULT NULL,
    currency varchar(3) DEFAULT NULL,
    FOREIGN KEY (service_catalog_id) REFERENCES services_catalog(id)
) ENGINE=InnoDB CHARSET=utf8;


-- INSERT INTO

INSERT INTO services_payments
(service_catalog_id, price, selfpay_amount, copay_amount, insurance_amount, currency)
SELECT
id, price, selfpay_amount, copay_amount, insurance_amount, currency
FROM services_catalog
