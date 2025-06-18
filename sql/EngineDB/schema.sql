--
-- Table structure for table `Attachments`
--

CREATE TABLE `Attachments` (
  `attach_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `test_id` int(11) DEFAULT NULL,
  `attach` blob DEFAULT NULL,
  `attachmime` varchar(30) DEFAULT NULL,
  `attachdesc` varchar(120) DEFAULT NULL,
  `comments` varchar(200) DEFAULT NULL,
  `originalname` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`attach_id`),
  KEY `test_id` (`test_id`)
);

--
-- Table structure for table `Board`
--
CREATE TABLE `Board` (
  `sn` int(10) unsigned NOT NULL,
  `full_id` varchar(20) NOT NULL,
  `board_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type_id` varchar(6) NOT NULL,
  `daq_chip_id` varchar(16) DEFAULT NULL,
  `location` varchar(50) NOT NULL,
  `comments` text DEFAULT NULL,
  `manufacturer_id` int(10) unsigned DEFAULT NULL,
  `LDO` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`board_id`),
  UNIQUE KEY `full_id` (`full_id`),
  UNIQUE KEY `full_id_idx` (`sn`,`board_id`),
  UNIQUE KEY `chip_id_idx` (`daq_chip_id`,`board_id`)
);

--
-- Table structure for table `Board_Info`
--
CREATE TABLE `Board_Info` (
  `info_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `board_id` int(11) NOT NULL,
  `info_type` int(11) NOT NULL,
  `info` varchar(300) DEFAULT NULL,
  `daq_chip_id` varchar(16) DEFAULT NULL,
  `trigger_chip_1_id` varchar(16) DEFAULT NULL,
  `trigger_chip_2_id` varchar(16) DEFAULT NULL,
  `location` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`info_id`),
  UNIQUE KEY `board_id` (`board_id`),
  KEY `board_id_2` (`board_id`),
  KEY `info_type` (`info_type`)
);

--
-- Table structure for table `Board_Info_Types`
--
CREATE TABLE `Board_Info_Types` (
  `info_type_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Info_Name` varchar(30) DEFAULT NULL,
  `Info_Desc_Short` varchar(100) DEFAULT NULL,
  `Info_Desc_Long` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`info_type_id`)
);


--
-- Table structure for table `Board_images`
--
CREATE TABLE `Board_images` (
  `board_id` int(10) unsigned NOT NULL,
  `image_name` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `view` varchar(20) DEFAULT NULL
);

--
-- Table structure for table `Board_type`
--
CREATE TABLE `Board_type` (
  `type_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `type_sn` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`type_id`),
  UNIQUE KEY `type_id` (`type_id`)
);

--
-- Table structure for table `Check_In`
--
CREATE TABLE `Check_In` (
  `checkin_id` int(11) NOT NULL AUTO_INCREMENT,
  `board_id` int(10) unsigned DEFAULT NULL,
  `person_id` int(10) unsigned DEFAULT NULL,
  `checkin_date` datetime DEFAULT NULL,
  `comment` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`checkin_id`)
);

--
-- Table structure for table `Check_Out`
--
CREATE TABLE `Check_Out` (
  `checkin_id` int(10) unsigned NOT NULL DEFAULT 0,
  `board_id` int(10) unsigned NOT NULL,
  `person_id` int(10) unsigned NOT NULL,
  `comment` varchar(120) DEFAULT NULL,
  `checkout_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
);

--
-- Table structure for table `Grades`
--
CREATE TABLE `Grades` (
  `grade_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `board_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  `grading_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `grade` varchar(4) NOT NULL,
  `comments` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`grade_id`),
  KEY `grade_id` (`grade_id`)
);

--
-- Table structure for table `Manufacturers`
--
CREATE TABLE `Manufacturers` (
  `manufacturer_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`manufacturer_id`)
);

--
-- Table structure for table `People`
--
CREATE TABLE `People` (
  `person_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `person_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`person_id`)
);

--
-- Table structure for table `Test`
--
CREATE TABLE `Test` (
  `test_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `test_type_id` int(10) unsigned NOT NULL,
  `board_id` int(10) unsigned NOT NULL,
  `person_id` int(10) unsigned NOT NULL,
  `day` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `successful` tinyint(1) NOT NULL,
  `comments` varchar(320) DEFAULT NULL,
  `config_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`test_id`),
  KEY `board_id` (`board_id`),
  KEY `person_id` (`person_id`)
);

--
-- Table structure for table `TestRevoke`
--
CREATE TABLE `TestRevoke` (
  `test_id` int(10) unsigned NOT NULL,
  `comment` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`test_id`)
);

--
-- Table structure for table `Test_Type`
--
CREATE TABLE `Test_Type` (
  `test_type` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `required` tinyint(1) NOT NULL,
  `desc_short` varchar(50) DEFAULT NULL,
  `desc_long` varchar(250) DEFAULT NULL,
  `relative_order` int(11) NOT NULL,
  PRIMARY KEY (`test_type`)
);

--
-- Table structure for table `Tester_Component`
--
CREATE TABLE `Tester_Component` (
  `component_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `full_id` varchar(15) DEFAULT NULL,
  `working` tinyint(1) DEFAULT NULL,
  `comments` text DEFAULT NULL,
  PRIMARY KEY (`component_id`)
);

--
-- Table structure for table `Tester_Configuration`
--
CREATE TABLE `Tester_Configuration` (
  `config_id` int(10) unsigned NOT NULL DEFAULT 0,
  `role_id` int(10) unsigned NOT NULL,
  `component_id` int(10) unsigned DEFAULT NULL,
  `teststand_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`config_id`,`role_id`)
);

--
-- Table structure for table `Tester_Roles`
--
CREATE TABLE `Tester_Roles` (
  `role_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`role_id`)
);

--
-- Table structure for table `Teststand`
--
CREATE TABLE `Teststand` (
  `teststand_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  `ip_address` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`teststand_id`)
);

--
-- Table structure for table `Type_test_stitch`
--
CREATE TABLE `Type_test_stitch` (
  `type_id` int(10) unsigned DEFAULT NULL,
  `test_type_id` int(10) unsigned DEFAULT NULL,
  KEY `type_id` (`type_id`),
  KEY `test_type_id` (`test_type_id`)
);


CREATE TABLE COMPONENT_STOCK (
       component_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
       PRIMARY KEY(component_id),
       barcode CHAR(16) UNIQUE NOT NULL,
       typecode CHAR(10) NOT NULL,
       entered TIMESTAMP       
       );

CREATE TABLE COMPONENT_USAGE (
       component_id INT UNSIGNED NOT NULL UNIQUE,
       FOREIGN KEY (component_id) REFERENCES COMPONENT_STOCK(component_id),
       used_in_barcode CHAR(16),
       used_when TIMESTAMP       
       );
