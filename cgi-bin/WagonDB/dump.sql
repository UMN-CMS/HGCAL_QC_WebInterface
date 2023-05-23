-- MySQL dump 10.14  Distrib 5.5.68-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: WagonDB
-- ------------------------------------------------------
-- Server version	5.5.68-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Attachments`
--

DROP TABLE IF EXISTS `Attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Attachments` (
  `attach_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `test_id` int(11) DEFAULT NULL,
  `attachmime` varchar(30) DEFAULT NULL,
  `attachdesc` varchar(120) DEFAULT NULL,
  `comments` varchar(200) DEFAULT NULL,
  `originalname` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`attach_id`),
  KEY `test_id` (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Attachments`
--

LOCK TABLES `Attachments` WRITE;
/*!40000 ALTER TABLE `Attachments` DISABLE KEYS */;
/*!40000 ALTER TABLE `Attachments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `People`
--

DROP TABLE IF EXISTS `People`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `People` (
  `person_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `person_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `People`
--

LOCK TABLES `People` WRITE;
/*!40000 ALTER TABLE `People` DISABLE KEYS */;
INSERT INTO `People` VALUES (1,'Bryan');
/*!40000 ALTER TABLE `People` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Test`
--

DROP TABLE IF EXISTS `Test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Test` (
  `test_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `test_type_id` int(11) NOT NULL,
  `wagon_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  `day` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `successful` tinyint(1) NOT NULL,
  `comments` varchar(320) DEFAULT NULL,
  PRIMARY KEY (`test_id`),
  KEY `wagon_id` (`wagon_id`),
  KEY `person_id` (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Test`
--

LOCK TABLES `Test` WRITE;
/*!40000 ALTER TABLE `Test` DISABLE KEYS */;
/*!40000 ALTER TABLE `Test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TestRevoke`
--

DROP TABLE IF EXISTS `TestRevoke`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TestRevoke` (
  `test_id` int(10) unsigned NOT NULL,
  `comment` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TestRevoke`
--

LOCK TABLES `TestRevoke` WRITE;
/*!40000 ALTER TABLE `TestRevoke` DISABLE KEYS */;
/*!40000 ALTER TABLE `TestRevoke` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Test_Type`
--

DROP TABLE IF EXISTS `Test_Type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Test_Type` (
  `test_type` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `required` tinyint(1) NOT NULL,
  `desc_short` varchar(50) DEFAULT NULL,
  `desc_long` varchar(250) DEFAULT NULL,
  `relative_order` int(11) NOT NULL,
  PRIMARY KEY (`test_type`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Test_Type`
--

LOCK TABLES `Test_Type` WRITE;
/*!40000 ALTER TABLE `Test_Type` DISABLE KEYS */;
INSERT INTO `Test_Type` VALUES (1,'test',1,'test','test',1);
/*!40000 ALTER TABLE `Test_Type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Wagon`
--

DROP TABLE IF EXISTS `Wagon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Wagon` (
  `sn` int(11) NOT NULL,
  `wagon_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`wagon_id`),
  UNIQUE KEY `sn` (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Wagon`
--

LOCK TABLES `Wagon` WRITE;
/*!40000 ALTER TABLE `Wagon` DISABLE KEYS */;
/*!40000 ALTER TABLE `Wagon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Wagon_Info`
--

DROP TABLE IF EXISTS `Wagon_Info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Wagon_Info` (
  `info_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `wagon_id` int(11) NOT NULL,
  `info_type` int(11) NOT NULL,
  `info` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`info_id`),
  KEY `wagon_id` (`wagon_id`),
  KEY `info_type` (`info_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Wagon_Info`
--

LOCK TABLES `Wagon_Info` WRITE;
/*!40000 ALTER TABLE `Wagon_Info` DISABLE KEYS */;
/*!40000 ALTER TABLE `Wagon_Info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Wagon_Info_Types`
--

DROP TABLE IF EXISTS `Wagon_Info_Types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Wagon_Info_Types` (
  `info_type_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Info_Name` varchar(30) DEFAULT NULL,
  `Info_Desc_Short` varchar(100) DEFAULT NULL,
  `Info_Desc_Long` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`info_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Wagon_Info_Types`
--

LOCK TABLES `Wagon_Info_Types` WRITE;
/*!40000 ALTER TABLE `Wagon_Info_Types` DISABLE KEYS */;
/*!40000 ALTER TABLE `Wagon_Info_Types` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-07-13 16:05:26
