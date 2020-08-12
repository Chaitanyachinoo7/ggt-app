-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: wh-mobile-test-1.clwbkkblucao.us-east-1.rds.amazonaws.com
-- Generation Time: Jul 14, 2020 at 04:53 PM
-- Server version: 8.0.19
-- PHP Version: 7.4.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ggt`
--

-- --------------------------------------------------------

--
-- Table structure for table `#Tableau_7261_sid_00000844_3_Connect_CheckCreateTempTableCap`
--

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int NOT NULL,
  `scheduled_dt` datetime DEFAULT NULL,
  `check_in_dt` datetime DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `group_code` varchar(45) DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `patient_questionnaire_id` int DEFAULT NULL,
  `test_start_dt` datetime DEFAULT NULL,
  `test_end_dt` datetime DEFAULT NULL,
  `status` enum('scheduled','checked_in','test_in_progress','test_completed','record_locked') DEFAULT 'scheduled',
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Stand-in structure for view `appointment_with_patient`
-- (See below for the actual view)
--
CREATE TABLE `appointment_with_patient` (
`check_in_dt` datetime
,`create_dt` datetime
,`dob` varchar(45)
,`first_name` varchar(45)
,`group_code` varchar(45)
,`id` int
,`last_name` varchar(45)
,`location_id` int
,`patient_id` int
,`patient_questionnaire_id` int
,`scheduled_dt` datetime
,`status` enum('scheduled','checked_in','test_in_progress','test_completed','record_locked')
,`test_end_dt` datetime
,`test_start_dt` datetime
,`update_dt` datetime
);

-- --------------------------------------------------------

--
-- Table structure for table `communication_history`
--

CREATE TABLE `communication_history` (
  `id` int NOT NULL,
  `type` varchar(45) DEFAULT NULL,
  `medium` varchar(45) DEFAULT NULL,
  `sent_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `message` text,
  `delivery_status` varchar(45) DEFAULT NULL,
  `direction` varchar(45) DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `appointment_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `consultations`
--

CREATE TABLE `consultations` (
  `id` int NOT NULL,
  `consultation_dt` datetime DEFAULT NULL,
  `consultation_notes` text,
  `create_dt` datetime DEFAULT NULL,
  `update_dt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Stand-in structure for view `detailed_test_results`
-- (See below for the actual view)
--
CREATE TABLE `detailed_test_results` (
`addr1` varchar(45)
,`addr2` varchar(45)
,`addr3` varchar(45)
,`appointment_id` int
,`city` varchar(45)
,`consultaiton_notes` text
,`consultation_status` enum('not_required','required','completed')
,`county` varchar(45)
,`dob` varchar(45)
,`email` varchar(45)
,`email_verified` varchar(45)
,`ethnicity` varchar(45)
,`first_name` varchar(45)
,`gender` enum('male','female','unknown')
,`group_code` varchar(45)
,`height_ft` varchar(45)
,`height_in` varchar(45)
,`inform_status` enum('pending_notification','attempted_notification','acknowledged_notification','use_group_settings')
,`lab_electronic_submission_dt` datetime
,`lab_id` int
,`lab_pysical_submission_dt` datetime
,`lab_result_receive_dt` datetime
,`lab_submission_batch_id` int
,`last_name` varchar(45)
,`middle_name` varchar(45)
,`notification_acknowledgement_dt` datetime
,`notification_method` enum('sms','email','call','use_group_settings')
,`patient_id` int
,`patient_questionnaire_id` int
,`phone_number` varchar(45)
,`phone_number_verified` varchar(45)
,`provider_id` int
,`race` varchar(45)
,`report_link` varchar(255)
,`sample_collection_end_dt` datetime
,`sample_collection_location_id` int
,`sample_collection_start_dt` datetime
,`st` varchar(45)
,`status` enum('test_in_progress','test_completed','ready_to_tx','pending_tx','with_lab','lab_result_received','attempted_notification','notification_acknowledged','attempted_consultation','consultation_in_progress','consultation_completed','record_locked')
,`test_id` int
,`test_result` enum('pos','neg','inconclusive')
,`token` varchar(45)
,`weight_lb` varchar(45)
,`zip` varchar(45)
);

-- --------------------------------------------------------

--
-- Table structure for table `healthtracrx_transmissions`
--

CREATE TABLE `healthtracrx_transmissions` (
  `test_id` int NOT NULL,
  `patient_id` varchar(45) DEFAULT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `dob` varchar(45) DEFAULT NULL,
  `gender` varchar(45) DEFAULT NULL,
  `race` varchar(45) DEFAULT NULL,
  `ethnicity` varchar(45) DEFAULT NULL,
  `addr1` varchar(45) DEFAULT NULL,
  `addr2` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `st` varchar(45) DEFAULT NULL,
  `zip` varchar(45) DEFAULT NULL,
  `phone` varchar(45) DEFAULT NULL,
  `client_site_code` varchar(45) DEFAULT NULL,
  `physician_npi` varchar(45) DEFAULT NULL,
  `bill` varchar(45) DEFAULT NULL,
  `client_order_number` varchar(45) DEFAULT NULL,
  `sample_type` varchar(45) DEFAULT NULL,
  `sample_source` varchar(45) DEFAULT NULL,
  `date_of_collection` varchar(45) DEFAULT NULL,
  `panel_code` varchar(45) DEFAULT NULL,
  `panel_name` varchar(45) DEFAULT NULL,
  `lab_submission_dt` datetime DEFAULT NULL,
  `lab_result_received_dt` datetime DEFAULT NULL,
  `transmission_status` enum('to_send','sent','received','process_completed') DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



--
-- Table structure for table `labs`
--

CREATE TABLE `labs` (
  `id` int NOT NULL,
  `lab_name` varchar(45) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `locations`
--

CREATE TABLE `locations` (
  `id` int NOT NULL,
  `site_code` varchar(45) NOT NULL,
  `group_code` varchar(45) DEFAULT '_DEFAULT_',
  `account` varchar(45) DEFAULT NULL,
  `addr1` varchar(45) DEFAULT NULL,
  `addr2` varchar(45) DEFAULT NULL,
  `addr3` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `st` varchar(10) DEFAULT NULL,
  `zip` varchar(12) DEFAULT NULL,
  `lat` float(10,6) DEFAULT NULL,
  `lng` float(10,6) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `type` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--


--
-- Table structure for table `patients`
--

CREATE TABLE `patients` (
  `id` int NOT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `middle_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `gender` enum('male','female','unknown') DEFAULT NULL,
  `height_ft` varchar(45) DEFAULT NULL,
  `height_in` varchar(45) DEFAULT NULL,
  `weight_lb` varchar(45) DEFAULT NULL,
  `ethnicity` varchar(45) DEFAULT NULL,
  `race` varchar(45) DEFAULT NULL,
  `addr1` varchar(45) DEFAULT NULL,
  `addr2` varchar(45) DEFAULT NULL,
  `addr3` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `county` varchar(45) DEFAULT NULL,
  `st` varchar(45) DEFAULT NULL,
  `zip` varchar(45) DEFAULT NULL,
  `dob` varchar(45) DEFAULT NULL,
  `phone_number` varchar(45) DEFAULT NULL,
  `phone_number_verified` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `email_verified` varchar(45) DEFAULT NULL,
  `token` varchar(45) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



--
-- Table structure for table `patient_questionnaires`
--

CREATE TABLE `patient_questionnaires` (
  `id` int NOT NULL,
  `patient_id` int DEFAULT NULL,
  `token` varchar(45) DEFAULT NULL,
  `group_code` varchar(45) DEFAULT NULL,
  `symptom_fever` tinyint DEFAULT NULL,
  `symptom_shortness_breath` tinyint DEFAULT NULL,
  `symptom_cough` tinyint DEFAULT NULL,
  `symptom_chest_pain` tinyint DEFAULT NULL,
  `symptom_lack_of_smell` tinyint DEFAULT NULL,
  `symptom_other_breathing` tinyint DEFAULT NULL,
  `covid_contact` tinyint DEFAULT NULL,
  `prescription_use` tinyint DEFAULT NULL,
  `heart_disease` tinyint DEFAULT NULL,
  `diabetes` tinyint DEFAULT NULL,
  `respiratory_diseases` tinyint DEFAULT NULL,
  `autoimmune_disease` tinyint DEFAULT NULL,
  `other_chronic` tinyint DEFAULT NULL,
  `allergies` tinyint DEFAULT NULL,
  `consent_signed` varchar(45) DEFAULT NULL,
  `consent_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `insurance_details` varchar(45) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- --------------------------------------------------------

--
-- Table structure for table `schedule_generation_rules`
--

CREATE TABLE `schedule_generation_rules` (
  `id` int NOT NULL,
  `location_id` int NOT NULL,
  `slot_increment` int DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `sun` tinyint DEFAULT NULL,
  `mon` tinyint DEFAULT NULL,
  `tue` tinyint DEFAULT NULL,
  `wed` tinyint DEFAULT NULL,
  `thu` tinyint DEFAULT NULL,
  `fri` tinyint DEFAULT NULL,
  `sat` tinyint DEFAULT NULL,
  `slot_multiplier` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



--
-- Table structure for table `signups`
--

CREATE TABLE `signups` (
  `id` int NOT NULL,
  `phone_number` varchar(45) DEFAULT NULL,
  `otp` varchar(45) DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  `device_data` text,
  `status` enum('pending','verified') DEFAULT 'pending',
  `token` varchar(45) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ;

--


--
-- Table structure for table `sql_log`
--

CREATE TABLE `sql_log` (
  `id` int NOT NULL,
  `log_type` enum('info','error') DEFAULT NULL,
  `sql_type` enum('SELECT','INSERT','UPDATE','DELETE') DEFAULT NULL,
  `statement` text,
  `details` text,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



--
-- Table structure for table `system_log`
--

CREATE TABLE `system_log` (
  `id` int NOT NULL,
  `event` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `correlation_id` varchar(45) DEFAULT NULL,
  `payload` mediumtext,
  `created_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--


--
-- Stand-in structure for view `tests_ready_to_tx_view`
-- (See below for the actual view)
--
CREATE TABLE `tests_ready_to_tx_view` (
`addr1` varchar(45)
,`addr2` varchar(45)
,`bill` varchar(11)
,`city` varchar(45)
,`client_order_number` int
,`client_site_code` varchar(8)
,`date_of_collection` varchar(8)
,`dob` varchar(45)
,`ethnicity` varchar(22)
,`first_name` varchar(45)
,`gender` varchar(7)
,`id` int
,`last_name` varchar(45)
,`panel_code` varchar(8)
,`panel_name` varchar(33)
,`patient_id` int
,`phone_number` varchar(45)
,`physician_npi` varchar(11)
,`race` varchar(41)
,`sample_source` varchar(11)
,`sample_type` varchar(11)
,`st` varchar(45)
,`zip` varchar(45)
);

-- --------------------------------------------------------

--
-- Table structure for table `test_samples`
--

CREATE TABLE `test_samples` (
  `id` int NOT NULL,
  `appointment_id` int DEFAULT NULL,
  `group_code` varchar(45) DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `patient_questionnaire_id` int DEFAULT NULL,
  `provider_id` int DEFAULT NULL,
  `sample_collection_location_id` int DEFAULT NULL,
  `sample_collection_start_dt` datetime DEFAULT NULL,
  `sample_collection_end_dt` datetime DEFAULT NULL,
  `lab_id` int DEFAULT NULL,
  `lab_submission_batch_id` int DEFAULT NULL,
  `lab_pysical_submission_dt` datetime DEFAULT NULL,
  `lab_electronic_submission_dt` datetime DEFAULT NULL,
  `lab_result_receive_dt` datetime DEFAULT NULL,
  `test_result` enum('pos','neg','inconclusive') DEFAULT NULL,
  `report_link` varchar(255) DEFAULT NULL,
  `inform_status` enum('pending_notification','attempted_notification','acknowledged_notification','use_group_settings') DEFAULT NULL,
  `notification_method` enum('sms','email','call','use_group_settings') DEFAULT NULL,
  `notification_acknowledgement_dt` datetime DEFAULT NULL,
  `consultation_status` enum('not_required','required','completed') DEFAULT NULL,
  `consultaiton_notes` text,
  `status` enum('test_in_progress','test_completed','ready_to_tx','pending_tx','with_lab','lab_result_received','attempted_notification','notification_acknowledged','attempted_consultation','consultation_in_progress','consultation_completed','record_locked') DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




-- --------------------------------------------------------

--
-- Table structure for table `providers`
--

CREATE TABLE `providers` (
  `id` int NOT NULL,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `phone` varchar(25) DEFAULT NULL,
  `company` varchar(45) DEFAULT NULL,
  `is_medical_assoc` tinyint DEFAULT NULL,
  `is_medical_provider` tinyint DEFAULT NULL,
  `is_testing_cordinator` tinyint DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Stand-in structure for view `quesionnaires_with_patient_info`
-- (See below for the actual view)
--
CREATE TABLE `quesionnaires_with_patient_info` (
`addr1` varchar(45)
,`addr2` varchar(45)
,`allergies` tinyint
,`autoimmune_disease` tinyint
,`city` varchar(45)
,`covid_contact` tinyint
,`date_of_collection` varchar(8)
,`diabetes` tinyint
,`dob` varchar(45)
,`ethnicity` varchar(22)
,`first_name` varchar(45)
,`gender` varchar(7)
,`group_code` varchar(45)
,`heart_disease` tinyint
,`last_name` varchar(45)
,`other_chronic` tinyint
,`patient_id` int
,`phone_number` varchar(45)
,`prescription_use` tinyint
,`questionnaire_id` int
,`race` varchar(41)
,`respiratory_diseases` tinyint
,`st` varchar(45)
,`symptom_chest_pain` tinyint
,`symptom_cough` tinyint
,`symptom_fever` tinyint
,`symptom_lack_of_smell` tinyint
,`symptom_other_breathing` tinyint
,`symptom_shortness_breath` tinyint
,`token1` varchar(45)
,`token2` varchar(45)
,`zip` varchar(45)
);

-- --------------------------------------------------------

--
-- Table structure for table `reference_data`
--

CREATE TABLE `reference_data` (
  `key` varchar(45) NOT NULL,
  `value` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `reference_data`
--

INSERT INTO `reference_data` (`key`, `value`) VALUES
('race_american_indian', 'American Indian or Alaska Native'),
('race_asian', 'Asian'),
('race_black', 'Black or African American'),
('race_hawaiian', 'Native Hawaiian or Other Pacific Islander'),
('race_other', 'Other'),
('race_white', 'White');

-- --------------------------------------------------------

--
-- Table structure for table `schedules`
--

CREATE TABLE `schedules` (
  `id` int NOT NULL,
  `location_id` int DEFAULT NULL,
  `start_dt` datetime DEFAULT NULL,
  `end_dt` datetime DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `status` enum('available','booked','blocked') DEFAULT 'available',
  `appointment_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



--
-- Table structure for table `vehicles`
--

CREATE TABLE `vehicles` (
  `id` int NOT NULL,
  `registration` varchar(45) DEFAULT NULL,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `workstations`
--

CREATE TABLE `workstations` (
  `id` int NOT NULL,
  `description` text,
  `printer_info` text,
  `create_dt` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_dt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




-- --------------------------------------------------------

--
-- Structure for view `appointment_with_patient`
--
DROP TABLE IF EXISTS `appointment_with_patient`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `appointment_with_patient`  AS  select `p`.`first_name` AS `first_name`,`p`.`last_name` AS `last_name`,`p`.`dob` AS `dob`,`appointments`.`id` AS `id`,`appointments`.`scheduled_dt` AS `scheduled_dt`,`appointments`.`check_in_dt` AS `check_in_dt`,`appointments`.`location_id` AS `location_id`,`appointments`.`group_code` AS `group_code`,`appointments`.`patient_id` AS `patient_id`,`appointments`.`patient_questionnaire_id` AS `patient_questionnaire_id`,`appointments`.`test_start_dt` AS `test_start_dt`,`appointments`.`test_end_dt` AS `test_end_dt`,`appointments`.`status` AS `status`,`appointments`.`create_dt` AS `create_dt`,`appointments`.`update_dt` AS `update_dt` from (`appointments` join `patients` `p` on((`p`.`id` = `appointments`.`patient_id`))) order by `appointments`.`id` desc ;

-- --------------------------------------------------------

--
-- Structure for view `detailed_test_results`
--
DROP TABLE IF EXISTS `detailed_test_results`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `detailed_test_results`  AS  select `test_samples`.`patient_id` AS `patient_id`,`test_samples`.`id` AS `test_id`,`test_samples`.`appointment_id` AS `appointment_id`,`test_samples`.`group_code` AS `group_code`,`patients`.`first_name` AS `first_name`,`patients`.`middle_name` AS `middle_name`,`patients`.`last_name` AS `last_name`,`patients`.`gender` AS `gender`,`patients`.`height_ft` AS `height_ft`,`patients`.`height_in` AS `height_in`,`patients`.`weight_lb` AS `weight_lb`,`patients`.`ethnicity` AS `ethnicity`,`patients`.`race` AS `race`,`patients`.`addr1` AS `addr1`,`patients`.`addr2` AS `addr2`,`patients`.`addr3` AS `addr3`,`patients`.`city` AS `city`,`patients`.`county` AS `county`,`patients`.`st` AS `st`,`patients`.`zip` AS `zip`,`patients`.`dob` AS `dob`,`patients`.`phone_number` AS `phone_number`,`patients`.`phone_number_verified` AS `phone_number_verified`,`patients`.`email` AS `email`,`patients`.`email_verified` AS `email_verified`,`patients`.`token` AS `token`,`test_samples`.`patient_questionnaire_id` AS `patient_questionnaire_id`,`test_samples`.`provider_id` AS `provider_id`,`test_samples`.`sample_collection_location_id` AS `sample_collection_location_id`,`test_samples`.`sample_collection_start_dt` AS `sample_collection_start_dt`,`test_samples`.`sample_collection_end_dt` AS `sample_collection_end_dt`,`test_samples`.`lab_id` AS `lab_id`,`test_samples`.`lab_submission_batch_id` AS `lab_submission_batch_id`,`test_samples`.`lab_pysical_submission_dt` AS `lab_pysical_submission_dt`,`test_samples`.`lab_electronic_submission_dt` AS `lab_electronic_submission_dt`,`test_samples`.`lab_result_receive_dt` AS `lab_result_receive_dt`,`test_samples`.`test_result` AS `test_result`,`test_samples`.`report_link` AS `report_link`,`test_samples`.`inform_status` AS `inform_status`,`test_samples`.`notification_method` AS `notification_method`,`test_samples`.`notification_acknowledgement_dt` AS `notification_acknowledgement_dt`,`test_samples`.`consultation_status` AS `consultation_status`,`test_samples`.`consultaiton_notes` AS `consultaiton_notes`,`test_samples`.`status` AS `status` from (`test_samples` join `patients` on((`patients`.`id` = `test_samples`.`patient_id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `quesionnaires_with_patient_info`
--
DROP TABLE IF EXISTS `quesionnaires_with_patient_info`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `quesionnaires_with_patient_info`  AS  select `q`.`id` AS `questionnaire_id`,`q`.`patient_id` AS `patient_id`,`p`.`first_name` AS `first_name`,`p`.`last_name` AS `last_name`,`p`.`dob` AS `dob`,`q`.`group_code` AS `group_code`,`q`.`symptom_fever` AS `symptom_fever`,`q`.`symptom_shortness_breath` AS `symptom_shortness_breath`,`q`.`symptom_cough` AS `symptom_cough`,`q`.`symptom_chest_pain` AS `symptom_chest_pain`,`q`.`symptom_lack_of_smell` AS `symptom_lack_of_smell`,`q`.`symptom_other_breathing` AS `symptom_other_breathing`,`q`.`covid_contact` AS `covid_contact`,`q`.`prescription_use` AS `prescription_use`,`q`.`heart_disease` AS `heart_disease`,`q`.`diabetes` AS `diabetes`,`q`.`respiratory_diseases` AS `respiratory_diseases`,`q`.`autoimmune_disease` AS `autoimmune_disease`,`q`.`other_chronic` AS `other_chronic`,`q`.`allergies` AS `allergies`,`p`.`token` AS `token1`,`q`.`token` AS `token2`,(case when (`p`.`gender` = 'male') then 'Male' when (`p`.`gender` = 'female') then 'Female' else 'Unknown' end) AS `gender`,(case when (`p`.`race` = 'race_american_indian') then 'American Indian or Alaska Native' when (`p`.`race` = 'race_asian') then 'Asian' when (`p`.`race` = 'race_black') then 'Black or African American' when (`p`.`race` = 'race_hawaiian') then 'Native Hawaiian or Other Pacific Islander' when (`p`.`race` = 'race_other') then 'Other' when (`p`.`race` = 'race_white') then 'White' else 'Unknown' end) AS `race`,(case when (`p`.`ethnicity` = 'true') then 'Hispanic or Latino' when (`p`.`ethnicity` = 'false') then 'Not Hispanic or Latino' else 'Unknown' end) AS `ethnicity`,replace(`p`.`addr1`,',','') AS `addr1`,replace(`p`.`addr2`,',','') AS `addr2`,`p`.`city` AS `city`,`p`.`st` AS `st`,`p`.`zip` AS `zip`,`p`.`phone_number` AS `phone_number`,date_format(`p`.`create_dt`,'%m/%d/%y') AS `date_of_collection` from (`patient_questionnaires` `q` join `patients` `p` on((`q`.`patient_id` = `p`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `tests_ready_to_tx_view`
--
DROP TABLE IF EXISTS `tests_ready_to_tx_view`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `tests_ready_to_tx_view`  AS  select `t`.`id` AS `id`,`t`.`patient_id` AS `patient_id`,replace(`p`.`first_name`,',','') AS `first_name`,replace(`p`.`last_name`,',','') AS `last_name`,`p`.`dob` AS `dob`,(case when (`p`.`gender` = 'male') then 'Male' when (`p`.`gender` = 'female') then 'Female' else 'Unknown' end) AS `gender`,(case when (`p`.`race` = 'race_american_indian') then 'American Indian or Alaska Native' when (`p`.`race` = 'race_asian') then 'Asian' when (`p`.`race` = 'race_black') then 'Black or African American' when (`p`.`race` = 'race_hawaiian') then 'Native Hawaiian or Other Pacific Islander' when (`p`.`race` = 'race_other') then 'Other' when (`p`.`race` = 'race_white') then 'White' else 'Unknown' end) AS `race`,(case when (`p`.`ethnicity` = 'true') then 'Hispanic or Latino' when (`p`.`ethnicity` = 'false') then 'Not Hispanic or Latino' when (`p`.`ethnicity` = 'hispanic_latino_spanish') then 'Hispanic or Latino' else 'Unknown' end) AS `ethnicity`,replace(`p`.`addr1`,',','') AS `addr1`,(case when (`p`.`addr2` is null) then '' else replace(`p`.`addr2`,',','') end) AS `addr2`,replace(`p`.`city`,',','') AS `city`,replace(`p`.`st`,',','') AS `st`,replace(`p`.`zip`,',','') AS `zip`,`p`.`phone_number` AS `phone_number`,'WELLHLTX' AS `client_site_code`,'22244887999' AS `physician_npi`,'Client Bill' AS `bill`,`t`.`id` AS `client_order_number`,'Respiratory' AS `sample_type`,'Nasopharynx' AS `sample_source`,date_format(`t`.`sample_collection_start_dt`,'%m/%d/%y') AS `date_of_collection`,'RESPI507' AS `panel_code`,'COVID-19 Coronavirus (SARS-CoV-2)' AS `panel_name` from (`test_samples` `t` join `patients` `p` on((`t`.`patient_id` = `p`.`id`))) where (`t`.`status` = 'ready_to_tx') ;

-- --------------------------------------------------------

--
-- Structure for view `z_persons`
--
DROP TABLE IF EXISTS `z_persons`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `z_persons`  AS  select `patients`.`id` AS `patient_id`,concat(`patients`.`last_name`,', ',`patients`.`first_name`,', ',`patients`.`dob`) AS `person_unique`,md5(concat(`patients`.`last_name`,', ',`patients`.`first_name`,', ',`patients`.`dob`)) AS `person_unique_nr`,(case when ((`patients`.`phone_number` = '+18018602474') or (`patients`.`phone_number` = '+14159354133') or (`patients`.`phone_number` = '+18476240342') or (lower(`patients`.`email`) like '%@wellpay%') or (lower(`patients`.`email`) like 'm.gaber@%') or (lower(`patients`.`email`) like 'gaber55@%') or (lower(`patients`.`email`) like 'sureshd@gmail.com') or (lower(`patients`.`email`) like 'suresh@ioeffect%')) then 'QA' else NULL end) AS `test_flag` from `patients` ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_appointments_patients1_idx` (`patient_id`),
  ADD KEY `fk_appointments_locations1_idx` (`location_id`),
  ADD KEY `fk_appointments_patient_questionnaires1_idx` (`patient_questionnaire_id`);

--
-- Indexes for table `communication_history`
--
ALTER TABLE `communication_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_communication_history_patients1_idx` (`patient_id`),
  ADD KEY `fk_communication_history_appointments1_idx` (`appointment_id`);

--
-- Indexes for table `consultations`
--
ALTER TABLE `consultations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `healthtracrx_transmissions`
--
ALTER TABLE `healthtracrx_transmissions`
  ADD PRIMARY KEY (`test_id`);

--
-- Indexes for table `labs`
--
ALTER TABLE `labs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `locations`
--
ALTER TABLE `locations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `patient_questionnaires`
--
ALTER TABLE `patient_questionnaires`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `providers`
--
ALTER TABLE `providers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `reference_data`
--
ALTER TABLE `reference_data`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `schedules`
--
ALTER TABLE `schedules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `start_dt_ix` (`start_dt`),
  ADD KEY `end_dt_ix` (`end_dt`),
  ADD KEY `status` (`status`),
  ADD KEY `appt_id_ix` (`appointment_id`);

--
-- Indexes for table `schedule_generation_rules`
--
ALTER TABLE `schedule_generation_rules`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `location_id_UNIQUE` (`location_id`),
  ADD KEY `fk_schedule_generation_rules_locations1_idx` (`location_id`);

--
-- Indexes for table `signups`
--
ALTER TABLE `signups`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IX_phone` (`phone_number`);

--
-- Indexes for table `sql_log`
--
ALTER TABLE `sql_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `system_log`
--
ALTER TABLE `system_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `correlation_id_idx` (`correlation_id`),
  ADD KEY `type_idx` (`type`),
  ADD KEY `created_dt_idx` (`created_dt`);

--
-- Indexes for table `test_samples`
--
ALTER TABLE `test_samples`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `workstations`
--
ALTER TABLE `workstations`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=200750;

--
-- AUTO_INCREMENT for table `communication_history`
--
ALTER TABLE `communication_history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `consultations`
--
ALTER TABLE `consultations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `labs`
--
ALTER TABLE `labs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `locations`
--
ALTER TABLE `locations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `patients`
--
ALTER TABLE `patients`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=125701;

--
-- AUTO_INCREMENT for table `patient_questionnaires`
--
ALTER TABLE `patient_questionnaires`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1508;

--
-- AUTO_INCREMENT for table `providers`
--
ALTER TABLE `providers`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `schedules`
--
ALTER TABLE `schedules`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2105;

--
-- AUTO_INCREMENT for table `schedule_generation_rules`
--
ALTER TABLE `schedule_generation_rules`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `signups`
--
ALTER TABLE `signups`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sql_log`
--
ALTER TABLE `sql_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3697;

--
-- AUTO_INCREMENT for table `system_log`
--
ALTER TABLE `system_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=945;

--
-- AUTO_INCREMENT for table `test_samples`
--
ALTER TABLE `test_samples`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=200698;

--
-- AUTO_INCREMENT for table `vehicles`
--
ALTER TABLE `vehicles`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `workstations`
--
ALTER TABLE `workstations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `fk_appointments_locations1` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`),
  ADD CONSTRAINT `fk_appointments_patient_questionnaires1` FOREIGN KEY (`patient_questionnaire_id`) REFERENCES `patient_questionnaires` (`id`),
  ADD CONSTRAINT `fk_appointments_patients1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `communication_history`
--
ALTER TABLE `communication_history`
  ADD CONSTRAINT `fk_communication_history_appointments1` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`),
  ADD CONSTRAINT `fk_communication_history_patients1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `schedule_generation_rules`
--
ALTER TABLE `schedule_generation_rules`
  ADD CONSTRAINT `fk_schedule_generation_rules_locations1` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
