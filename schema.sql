-- schema.sql

-- Create a new database
-- TODO replace db_name
CREATE DATABASE IF NOT EXISTS db_name
USE db_name;

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
  `sn` varchar(10) DEFAULT NULL,
  `full_id` varchar(20) NOT NULL,
  `board_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type_id` varchar(6) DEFAULT NULL,
  `location` varchar(50) NOT NULL,
  `comments` text DEFAULT NULL,
  `manufacturer_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`board_id`),
  UNIQUE KEY `full_id` (`full_id`),
  UNIQUE KEY `full_id_idx` (`sn`,`board_id`),
  UNIQUE KEY `chip_id_idx` (`board_id`)
);

--
-- Table structure for table `Board_images`
--

CREATE TABLE `Board_images` (
  `board_id` int(10) unsigned NOT NULL,
  `image_name` varchar(50) DEFAULT NULL,
  `view` varchar(20) DEFAULT NULL,
  `date` datetime DEFAULT NULL
);

--
-- Table structure for table `Board_type`
--

CREATE TABLE `Board_type` (
  `type_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `type_sn` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`type_id`)
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
  PRIMARY KEY (`test_id`),
  KEY `board_id` (`board_id`),
  KEY `person_id` (`person_id`)
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
-- Table structure for table `Type_test_stitch`
--

CREATE TABLE `Type_test_stitch` (
  `type_id` int(10) unsigned DEFAULT NULL,
  `test_type_id` int(10) unsigned DEFAULT NULL,
  KEY `type_id` (`type_id`),
  KEY `test_type_id` (`test_type_id`)
);
