-- service_catalog table v2
-- Adding a new currency column

ALTER TABLE services_catalog
ADD currency varchar(3);