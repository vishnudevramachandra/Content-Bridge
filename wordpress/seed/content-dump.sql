/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.18-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: wordpress-db    Database: wordpress
-- ------------------------------------------------------
-- Server version	11.4.13-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `wp_posts`
--

DROP TABLE IF EXISTS `wp_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_posts` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_author` bigint(20) unsigned NOT NULL DEFAULT 0,
  `post_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content` longtext NOT NULL,
  `post_title` text NOT NULL,
  `post_excerpt` text NOT NULL,
  `post_status` varchar(20) NOT NULL DEFAULT 'publish',
  `comment_status` varchar(20) NOT NULL DEFAULT 'open',
  `ping_status` varchar(20) NOT NULL DEFAULT 'open',
  `post_password` varchar(255) NOT NULL DEFAULT '',
  `post_name` varchar(200) NOT NULL DEFAULT '',
  `to_ping` text NOT NULL,
  `pinged` text NOT NULL,
  `post_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_modified_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content_filtered` longtext NOT NULL,
  `post_parent` bigint(20) unsigned NOT NULL DEFAULT 0,
  `guid` varchar(255) NOT NULL DEFAULT '',
  `menu_order` int(11) NOT NULL DEFAULT 0,
  `post_type` varchar(20) NOT NULL DEFAULT 'post',
  `post_mime_type` varchar(100) NOT NULL DEFAULT '',
  `comment_count` bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `post_name` (`post_name`(191)),
  KEY `type_status_date` (`post_type`,`post_status`,`post_date`,`ID`),
  KEY `post_parent` (`post_parent`),
  KEY `post_author` (`post_author`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_posts`
--

LOCK TABLES `wp_posts` WRITE;
/*!40000 ALTER TABLE `wp_posts` DISABLE KEYS */;
INSERT INTO `wp_posts` VALUES
(4,0,'2026-09-02 08:31:40','2026-09-02 08:31:40','<!-- wp:paragraph --><p>Sentinel Industrial Supply (SIS) has served industrial and manufacturing customers with MRO parts, safety equipment, and compliance-documented components since our founding. Our technical team specializes in cross-referencing substitute parts and keeping certification records current as standards evolve.</p><!-- /wp:paragraph -->','About Us','','publish','closed','closed','','about-us','','','2026-09-02 08:31:40','2026-09-02 08:31:40','',0,'http://localhost:8080/about-us/',0,'page','',0),
(5,0,'2026-09-02 08:31:40','2026-09-02 08:31:40','<!-- wp:paragraph --><p>SIS stocks industrial safety and automation components from leading manufacturers, including our Veridian Automation product line below.</p><!-- /wp:paragraph -->','Products','','publish','closed','closed','','products','','','2026-09-02 08:31:40','2026-09-02 08:31:40','',0,'http://localhost:8080/products/',0,'page','',0),
(6,0,'2026-09-02 08:31:40','2026-09-02 08:31:40','<!-- wp:paragraph --><p>Spec sheet lookup, compliance certification tracking, substitute/cross-reference parts sourcing, tiered B2B pricing, and punchout catalog integration (EDI/cXML) for procurement systems.</p><!-- /wp:paragraph -->','Services','','publish','closed','closed','','services','','','2026-09-02 08:31:40','2026-09-02 08:31:40','',0,'http://localhost:8080/services/',0,'page','',0),
(7,0,'2026-09-02 08:31:40','2026-09-02 08:31:40','<!-- wp:paragraph --><p>On-site and virtual training on safety equipment installation, machine guarding compliance, and code-update briefings for plant safety teams.</p><!-- /wp:paragraph -->','Training','','publish','closed','closed','','training','','','2026-09-02 08:31:40','2026-09-02 08:31:40','',0,'http://localhost:8080/training/',0,'page','',0),
(8,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>We design, build, integrate, and install industrial automation and machine safety systems tailored to your production line, from initial spec through commissioning.</p><!-- /wp:paragraph -->','SIS Automation Solutions','','publish','closed','closed','','sis-automation-solutions','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',0,'http://localhost:8080/sis-automation-solutions/',0,'page','',0),
(9,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>Reach the Sentinel Industrial Supply team for quotes, technical support, or compliance documentation requests.</p><!-- /wp:paragraph -->','Contact Us','','publish','closed','closed','','contact-us','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',0,'http://localhost:8080/contact-us/',0,'page','',0),
(10,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>Full range of Veridian Automation safety interlock switches for guard doors and access points, in stock for same-day shipping.</p><!-- /wp:paragraph -->','Veridian Safety Switches','','publish','closed','closed','','veridian-safety-switches','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',5,'http://localhost:8080/products/veridian-safety-switches/',0,'page','',0),
(11,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>Veridian Automation emergency stop pushbuttons and pull-wire e-stop devices for machine safety circuits.</p><!-- /wp:paragraph -->','Veridian Emergency Stop Devices','','publish','closed','closed','','veridian-emergency-stop-devices','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',5,'http://localhost:8080/products/veridian-emergency-stop-devices/',0,'page','',0),
(12,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>Veridian Automation Type 4 safety light curtains for point-of-operation guarding on presses and automated cells.</p><!-- /wp:paragraph -->','Veridian Safety Light Curtains','','publish','closed','closed','','veridian-safety-light-curtains','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',5,'http://localhost:8080/products/veridian-safety-light-curtains/',0,'page','',0),
(13,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph --><p>Sentinel Industrial Supply (SIS) is an authorized Veridian Automation distributor. Industrial safety switches, emergency stop devices, and safety light curtains, backed by same-day quoting and compliance documentation.</p><!-- /wp:paragraph -->','Home','','publish','closed','closed','','home','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',0,'http://localhost:8080/home/',0,'page','',0),
(14,0,'2026-09-02 08:31:41','2026-09-02 08:31:41','<!-- wp:paragraph {\"className\":\"is-style-default\"} -->\n<p class=\"is-style-default\">The newly developed engraver BX54 uses the most powerful laser there is to get its work done in a fraction of time. This saves not just unlimited time but has the advantage that the material need not be cooled to dissipate the extra energy imparted by the 50mW laser. </p>\n<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->','Burn it with BX54','','publish','open','open','','burn-it-with-bx54','','','2026-09-02 08:31:41','2026-09-02 08:31:41','',0,'http://localhost:8080/burn-it-with-bx54/',0,'post','',0),
(15,0,'2026-09-02 08:31:42','2026-09-02 08:31:42','Our UL508A-certified panel shop has completed its transition to the latest edition of the standard. If you spec custom control panels built to UL508A, note the updated short-circuit current rating (SCCR) documentation requirements before your next build order.','UL508A Panel Shop Update: What the Latest Revision Changes for Custom Control Panels','','publish','open','open','','ul508a-panel-shop-update-what-the-latest-revision-changes-for-custom-control-panels','','','2026-09-02 08:31:42','2026-09-02 08:31:42','',0,'http://localhost:8080/ul508a-panel-shop-update-what-the-latest-revision-changes-for-custom-control-panels/',0,'post','',0),
(16,0,'2026-09-02 08:31:42','2026-09-02 08:31:42','Our team spent the week at IMTS talking with plant engineers and procurement teams. The recurring theme: faster cross-reference lookups for substitute parts when a primary SKU is backordered. More on that in an upcoming post.','On the Floor at IMTS: What Buyers Were Asking About This Year','','publish','open','open','','on-the-floor-at-imts-what-buyers-were-asking-about-this-year','','','2026-09-02 08:31:42','2026-09-02 08:31:42','',0,'http://localhost:8080/on-the-floor-at-imts-what-buyers-were-asking-about-this-year/',0,'post','',0),
(17,0,'2026-09-02 08:31:42','2026-09-02 08:31:42','<!-- wp:navigation-link {\"label\":\"About Us\",\"type\":\"page\",\"id\":4,\"url\":\"http://localhost:8080/about-us/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-submenu {\"label\":\"Products\",\"type\":\"page\",\"id\":5,\"url\":\"http://localhost:8080/products/\",\"kind\":\"post-type\"} -->\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Switches\",\"type\":\"page\",\"id\":10,\"url\":\"http://localhost:8080/products/veridian-safety-switches/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Emergency Stop Devices\",\"type\":\"page\",\"id\":11,\"url\":\"http://localhost:8080/products/veridian-emergency-stop-devices/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Light Curtains\",\"type\":\"page\",\"id\":12,\"url\":\"http://localhost:8080/products/veridian-safety-light-curtains/\",\"kind\":\"post-type\"} /-->\n<!-- /wp:navigation-submenu -->\n\n<!-- wp:navigation-link {\"label\":\"Services\",\"type\":\"page\",\"id\":6,\"url\":\"http://localhost:8080/services/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Training\",\"type\":\"page\",\"id\":7,\"url\":\"http://localhost:8080/training/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"SIS Automation Solutions\",\"type\":\"page\",\"id\":8,\"url\":\"http://localhost:8080/sis-automation-solutions/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Contact Us\",\"type\":\"page\",\"id\":9,\"url\":\"http://localhost:8080/contact-us/\",\"kind\":\"post-type\"} /-->\n','Navigation','','publish','closed','closed','','navigation','','','2026-09-02 08:31:42','2026-09-02 08:31:42','',0,'http://localhost:8080/navigation/',0,'wp_navigation','',0),
(18,0,'2026-09-02 08:31:42','2026-09-02 08:31:42','<!-- wp:navigation-link {\"label\":\"About Us\",\"type\":\"page\",\"id\":4,\"url\":\"http://localhost:8080/about-us/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-submenu {\"label\":\"Products\",\"type\":\"page\",\"id\":5,\"url\":\"http://localhost:8080/products/\",\"kind\":\"post-type\"} -->\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Switches\",\"type\":\"page\",\"id\":10,\"url\":\"http://localhost:8080/products/veridian-safety-switches/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Emergency Stop Devices\",\"type\":\"page\",\"id\":11,\"url\":\"http://localhost:8080/products/veridian-emergency-stop-devices/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Light Curtains\",\"type\":\"page\",\"id\":12,\"url\":\"http://localhost:8080/products/veridian-safety-light-curtains/\",\"kind\":\"post-type\"} /-->\n<!-- /wp:navigation-submenu -->\n\n<!-- wp:navigation-link {\"label\":\"Services\",\"type\":\"page\",\"id\":6,\"url\":\"http://localhost:8080/services/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Training\",\"type\":\"page\",\"id\":7,\"url\":\"http://localhost:8080/training/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"SIS Automation Solutions\",\"type\":\"page\",\"id\":8,\"url\":\"http://localhost:8080/sis-automation-solutions/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Contact Us\",\"type\":\"page\",\"id\":9,\"url\":\"http://localhost:8080/contact-us/\",\"kind\":\"post-type\"} /-->\n','Navigation','','inherit','closed','closed','','17-revision-v1','','','2026-09-02 08:31:42','2026-09-02 08:31:42','',17,'http://localhost:8080/?p=18',0,'revision','',0);
/*!40000 ALTER TABLE `wp_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_postmeta`
--

DROP TABLE IF EXISTS `wp_postmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_postmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext DEFAULT NULL,
  PRIMARY KEY (`meta_id`),
  KEY `post_id` (`post_id`),
  KEY `meta_key` (`meta_key`(191))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_postmeta`
--

LOCK TABLES `wp_postmeta` WRITE;
/*!40000 ALTER TABLE `wp_postmeta` DISABLE KEYS */;
INSERT INTO `wp_postmeta` VALUES
(3,14,'_pingme','1'),
(4,14,'_encloseme','1'),
(5,14,'related_product_ids','104,891,233'),
(6,15,'_pingme','1'),
(7,15,'_encloseme','1'),
(8,16,'_pingme','1'),
(9,16,'_encloseme','1');
/*!40000 ALTER TABLE `wp_postmeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_comments`
--

DROP TABLE IF EXISTS `wp_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_comments` (
  `comment_ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comment_post_ID` bigint(20) unsigned NOT NULL DEFAULT 0,
  `comment_author` tinytext NOT NULL,
  `comment_author_email` varchar(100) NOT NULL DEFAULT '',
  `comment_author_url` varchar(200) NOT NULL DEFAULT '',
  `comment_author_IP` varchar(100) NOT NULL DEFAULT '',
  `comment_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_content` text NOT NULL,
  `comment_karma` int(11) NOT NULL DEFAULT 0,
  `comment_approved` varchar(20) NOT NULL DEFAULT '1',
  `comment_agent` varchar(255) NOT NULL DEFAULT '',
  `comment_type` varchar(20) NOT NULL DEFAULT 'comment',
  `comment_parent` bigint(20) unsigned NOT NULL DEFAULT 0,
  `user_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`comment_ID`),
  KEY `comment_post_ID` (`comment_post_ID`),
  KEY `comment_approved_date_gmt` (`comment_approved`,`comment_date_gmt`),
  KEY `comment_date_gmt` (`comment_date_gmt`),
  KEY `comment_parent` (`comment_parent`),
  KEY `comment_author_email` (`comment_author_email`(10))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_comments`
--

LOCK TABLES `wp_comments` WRITE;
/*!40000 ALTER TABLE `wp_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `wp_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_commentmeta`
--

DROP TABLE IF EXISTS `wp_commentmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_commentmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comment_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext DEFAULT NULL,
  PRIMARY KEY (`meta_id`),
  KEY `comment_id` (`comment_id`),
  KEY `meta_key` (`meta_key`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_commentmeta`
--

LOCK TABLES `wp_commentmeta` WRITE;
/*!40000 ALTER TABLE `wp_commentmeta` DISABLE KEYS */;
/*!40000 ALTER TABLE `wp_commentmeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_terms`
--

DROP TABLE IF EXISTS `wp_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_terms` (
  `term_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL DEFAULT '',
  `slug` varchar(200) NOT NULL DEFAULT '',
  `term_group` bigint(10) NOT NULL DEFAULT 0,
  PRIMARY KEY (`term_id`),
  KEY `slug` (`slug`(191)),
  KEY `name` (`name`(191))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_terms`
--

LOCK TABLES `wp_terms` WRITE;
/*!40000 ALTER TABLE `wp_terms` DISABLE KEYS */;
INSERT INTO `wp_terms` VALUES
(1,'Uncategorized','uncategorized',0),
(2,'Product Spotlights','product-spotlights',0),
(3,'Code &amp; Compliance','code-compliance',0),
(4,'Trade Show Recaps','trade-show-recaps',0);
/*!40000 ALTER TABLE `wp_terms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_term_taxonomy`
--

DROP TABLE IF EXISTS `wp_term_taxonomy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_term_taxonomy` (
  `term_taxonomy_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `taxonomy` varchar(32) NOT NULL DEFAULT '',
  `description` longtext NOT NULL,
  `parent` bigint(20) unsigned NOT NULL DEFAULT 0,
  `count` bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`term_taxonomy_id`),
  UNIQUE KEY `term_id_taxonomy` (`term_id`,`taxonomy`),
  KEY `taxonomy` (`taxonomy`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_term_taxonomy`
--

LOCK TABLES `wp_term_taxonomy` WRITE;
/*!40000 ALTER TABLE `wp_term_taxonomy` DISABLE KEYS */;
INSERT INTO `wp_term_taxonomy` VALUES
(1,1,'category','',0,0),
(2,2,'category','',0,1),
(3,3,'category','',0,1),
(4,4,'category','',0,1);
/*!40000 ALTER TABLE `wp_term_taxonomy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_term_relationships`
--

DROP TABLE IF EXISTS `wp_term_relationships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_term_relationships` (
  `object_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `term_taxonomy_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `term_order` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`object_id`,`term_taxonomy_id`),
  KEY `term_taxonomy_id` (`term_taxonomy_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_term_relationships`
--

LOCK TABLES `wp_term_relationships` WRITE;
/*!40000 ALTER TABLE `wp_term_relationships` DISABLE KEYS */;
INSERT INTO `wp_term_relationships` VALUES
(14,2,0),
(15,3,0),
(16,4,0);
/*!40000 ALTER TABLE `wp_term_relationships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_termmeta`
--

DROP TABLE IF EXISTS `wp_termmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wp_termmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext DEFAULT NULL,
  PRIMARY KEY (`meta_id`),
  KEY `term_id` (`term_id`),
  KEY `meta_key` (`meta_key`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_termmeta`
--

LOCK TABLES `wp_termmeta` WRITE;
/*!40000 ALTER TABLE `wp_termmeta` DISABLE KEYS */;
/*!40000 ALTER TABLE `wp_termmeta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02  9:05:27
