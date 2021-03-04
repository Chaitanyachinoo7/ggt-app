-- This DDL is auto-generated with DBeaver
-- This DDL is not used by the application to generate anything (only for reference)
-- It is here because, in the long run we can see the changes done to the table
-- This file is the v1, when new alterations are done to table have them as versions

CREATE TABLE `services_catalog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_code` varchar(45) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `price` decimal(13,2) DEFAULT NULL,
  `selfpay_amount` decimal(13,2) DEFAULT NULL,
  `copay_amount` decimal(13,2) DEFAULT NULL,
  `insurance_amount` decimal(13,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `code_ix` (`service_code`),
  KEY `name_ix` (`service_name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;