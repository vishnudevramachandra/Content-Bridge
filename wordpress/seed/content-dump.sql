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
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
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
(18,0,'2026-09-02 08:31:42','2026-09-02 08:31:42','<!-- wp:navigation-link {\"label\":\"About Us\",\"type\":\"page\",\"id\":4,\"url\":\"http://localhost:8080/about-us/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-submenu {\"label\":\"Products\",\"type\":\"page\",\"id\":5,\"url\":\"http://localhost:8080/products/\",\"kind\":\"post-type\"} -->\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Switches\",\"type\":\"page\",\"id\":10,\"url\":\"http://localhost:8080/products/veridian-safety-switches/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Emergency Stop Devices\",\"type\":\"page\",\"id\":11,\"url\":\"http://localhost:8080/products/veridian-emergency-stop-devices/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Veridian Safety Light Curtains\",\"type\":\"page\",\"id\":12,\"url\":\"http://localhost:8080/products/veridian-safety-light-curtains/\",\"kind\":\"post-type\"} /-->\n<!-- /wp:navigation-submenu -->\n\n<!-- wp:navigation-link {\"label\":\"Services\",\"type\":\"page\",\"id\":6,\"url\":\"http://localhost:8080/services/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Training\",\"type\":\"page\",\"id\":7,\"url\":\"http://localhost:8080/training/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"SIS Automation Solutions\",\"type\":\"page\",\"id\":8,\"url\":\"http://localhost:8080/sis-automation-solutions/\",\"kind\":\"post-type\"} /-->\n\n<!-- wp:navigation-link {\"label\":\"Contact Us\",\"type\":\"page\",\"id\":9,\"url\":\"http://localhost:8080/contact-us/\",\"kind\":\"post-type\"} /-->\n','Navigation','','inherit','closed','closed','','17-revision-v1','','','2026-09-02 08:31:42','2026-09-02 08:31:42','',17,'http://localhost:8080/?p=18',0,'revision','',0),
(19,0,'2026-09-07 13:19:36','2026-09-07 13:19:36','When reordering the replacement lens for your BX54 engraver, our internal reference is part number BX54-FL-02. Contact support for the exact catalog SKU your fabricator\'s paperwork needs.','Reordering the BX54 Focus Lens','','publish','open','open','','reordering-the-bx54-focus-lens','','','2026-09-07 13:19:36','2026-09-07 13:19:36','',0,'http://localhost:8080/reordering-the-bx54-focus-lens/',0,'post','',0),
(21,0,'2026-09-07 13:48:34','2026-09-07 13:48:34','When a critical safety switch or laser engraver filter cartridge fails, waiting on a slow shipment isn\'t an option. Our just-in-time delivery program keeps top-moving SKUs — Veridian safety switches, BX54 consumables, and other frequently reordered parts — staged for same-day dispatch from our regional warehouse. Talk to your account rep about setting up a standing JIT schedule for your top 20 parts.','Just-In-Time Delivery for MRO Parts: Keeping Your Line Running','','publish','open','open','','just-in-time-delivery-for-mro-parts','','','2026-09-07 13:48:34','2026-09-07 13:48:34','',0,'http://localhost:8080/just-in-time-delivery-for-mro-parts/',0,'post','',0),
(22,0,'2026-09-07 13:48:34','2026-09-07 13:48:34','Running out of gloves, cutting fluid, or BX54 filter cartridges mid-shift costs more than the part itself — it costs downtime. Our smart vending and inventory management program places locked, tracked dispensing units directly on your shop floor, automatically triggering reorders against your SIS account before a bin ever goes empty.','Vending & Inventory Management for Shop-Floor Consumables','','publish','open','open','','vending-and-inventory-management-for-shop-floor-consumables','','','2026-09-07 13:48:34','2026-09-07 13:48:34','',0,'http://localhost:8080/vending-and-inventory-management-for-shop-floor-consumables/',0,'post','',0),
(23,0,'2026-09-07 13:48:34','2026-09-07 13:48:34','We\'ve expanded our warehouse to stock gravity and powered conveyor sections, roller assemblies, and transfer components for material handling lines — alongside the Veridian safety switches and light curtains you\'d typically pair with a new conveyor guarding zone. Ask your rep for a line-side safety and material handling bundle quote.','Conveyor & Material Handling Components Now In Stock','','publish','open','open','','conveyor-and-material-handling-components-now-in-stock','','','2026-09-07 13:48:34','2026-09-07 13:48:34','',0,'http://localhost:8080/conveyor-and-material-handling-components-now-in-stock/',0,'post','',0),
(72,1,'2026-09-07 14:27:14','0000-00-00 00:00:00','','Auto Draft','','auto-draft','open','open','','','','','2026-09-07 14:27:14','0000-00-00 00:00:00','',0,'http://localhost:8080/?p=72',0,'post','',0),
(73,1,'2026-09-07 14:32:10','2026-09-07 14:32:10','{\"version\": 3, \"isGlobalStylesUserThemeJSON\": true }','Custom Styles','','publish','closed','closed','','wp-global-styles-twentytwentyfive','','','2026-09-07 14:32:10','2026-09-07 14:32:10','',0,'http://localhost:8080/wp-global-styles-twentytwentyfive/',0,'wp_global_styles','',0),
(74,0,'2026-09-07 14:42:28','2026-09-07 14:42:28','','About Sentinel Industrial Supply','','inherit','open','closed','','about-sentinel-industrial-supply','','','2026-09-07 14:42:28','2026-09-07 14:42:28','',4,'http://localhost:8080/wp-content/uploads/2026/09/page-4-about-us.png',0,'attachment','image/png',0),
(75,0,'2026-09-07 14:42:28','2026-09-07 14:42:28','','Industrial Safety & Automation Catalog','','inherit','open','closed','','industrial-safety-automation-catalog','','','2026-09-07 14:42:28','2026-09-07 14:42:28','',5,'http://localhost:8080/wp-content/uploads/2026/09/page-5-products.png',0,'attachment','image/png',0),
(76,0,'2026-09-07 14:42:28','2026-09-07 14:42:28','','Spec Lookup & Compliance Services','','inherit','open','closed','','spec-lookup-compliance-services','','','2026-09-07 14:42:28','2026-09-07 14:42:28','',6,'http://localhost:8080/wp-content/uploads/2026/09/page-6-services.png',0,'attachment','image/png',0),
(77,0,'2026-09-07 14:42:28','2026-09-07 14:42:28','','Machine Safety Training Programs','','inherit','open','closed','','machine-safety-training-programs','','','2026-09-07 14:42:28','2026-09-07 14:42:28','',7,'http://localhost:8080/wp-content/uploads/2026/09/page-7-training.png',0,'attachment','image/png',0),
(78,0,'2026-09-07 14:42:28','2026-09-07 14:42:28','','SIS Automation Solutions','','inherit','open','closed','','sis-automation-solutions-2','','','2026-09-07 14:42:28','2026-09-07 14:42:28','',8,'http://localhost:8080/wp-content/uploads/2026/09/page-8-automation.png',0,'attachment','image/png',0),
(79,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Contact Sentinel Industrial Supply','','inherit','open','closed','','contact-sentinel-industrial-supply','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',9,'http://localhost:8080/wp-content/uploads/2026/09/page-9-contact-us.png',0,'attachment','image/png',0),
(80,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Veridian Safety Interlock Switches','','inherit','open','closed','','veridian-safety-interlock-switches','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',10,'http://localhost:8080/wp-content/uploads/2026/09/page-10-veridian-switches.png',0,'attachment','image/png',0),
(81,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Veridian Emergency Stop Devices','','inherit','open','closed','','veridian-emergency-stop-devices-2','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',11,'http://localhost:8080/wp-content/uploads/2026/09/page-11-veridian-estop.png',0,'attachment','image/png',0),
(82,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Veridian Type 4 Safety Light Curtains','','inherit','open','closed','','veridian-type-4-safety-light-curtains','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',12,'http://localhost:8080/wp-content/uploads/2026/09/page-12-veridian-curtains.png',0,'attachment','image/png',0),
(83,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Sentinel Industrial Supply','','inherit','open','closed','','sentinel-industrial-supply','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',13,'http://localhost:8080/wp-content/uploads/2026/09/page-13-home.png',0,'attachment','image/png',0),
(84,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Burn It With BX54','','inherit','open','closed','','burn-it-with-bx54-2','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',14,'http://localhost:8080/wp-content/uploads/2026/09/post-14-burn-it-bx54.png',0,'attachment','image/png',0),
(85,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','UL508A Panel Shop Update','','inherit','open','closed','','ul508a-panel-shop-update','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',15,'http://localhost:8080/wp-content/uploads/2026/09/post-15-ul508a-update.png',0,'attachment','image/png',0),
(86,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','On the Floor at IMTS','','inherit','open','closed','','on-the-floor-at-imts','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',16,'http://localhost:8080/wp-content/uploads/2026/09/post-16-imts-recap.png',0,'attachment','image/png',0),
(87,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Reordering the BX54 Focus Lens','','inherit','open','closed','','reordering-the-bx54-focus-lens-2','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',19,'http://localhost:8080/wp-content/uploads/2026/09/post-19-bx54-lens.png',0,'attachment','image/png',0),
(88,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Just-In-Time Delivery for MRO Parts','','inherit','open','closed','','just-in-time-delivery-for-mro-parts-2','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',21,'http://localhost:8080/wp-content/uploads/2026/09/post-21-jit-delivery.png',0,'attachment','image/png',0),
(89,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Vending & Inventory Management','','inherit','open','closed','','vending-inventory-management','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',22,'http://localhost:8080/wp-content/uploads/2026/09/post-22-vending.png',0,'attachment','image/png',0),
(90,0,'2026-09-07 14:42:29','2026-09-07 14:42:29','','Conveyor & Material Handling Components Now In Stock','','inherit','open','closed','','conveyor-material-handling-components-now-in-stock','','','2026-09-07 14:42:29','2026-09-07 14:42:29','',23,'http://localhost:8080/wp-content/uploads/2026/09/post-23-conveyors.png',0,'attachment','image/png',0),
(91,1,'2026-09-07 14:44:48','0000-00-00 00:00:00','','Auto Draft','','auto-draft','open','open','','','','','2026-09-07 14:44:48','0000-00-00 00:00:00','',0,'http://localhost:8080/?p=91',0,'post','',0);
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
) ENGINE=InnoDB AUTO_INCREMENT=285 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
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
(9,16,'_encloseme','1'),
(10,19,'_pingme','1'),
(11,19,'_encloseme','1'),
(13,21,'_pingme','1'),
(14,21,'_encloseme','1'),
(15,22,'_pingme','1'),
(16,22,'_encloseme','1'),
(17,23,'_pingme','1'),
(18,23,'_encloseme','1'),
(211,21,'_edit_lock','1788791400:1'),
(212,14,'_edit_lock','1788895094:1'),
(213,16,'_edit_lock','1788792163:1'),
(214,15,'_edit_lock','1788894299:1'),
(215,19,'_edit_lock','1788902504:1'),
(216,19,'slug','BX54-FL-02'),
(217,74,'_wp_attached_file','2026/09/page-4-about-us.png'),
(218,74,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:27:\"2026/09/page-4-about-us.png\";s:8:\"filesize\";i:15339;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:27:\"page-4-about-us-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:7992;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:27:\"page-4-about-us-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5869;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:27:\"page-4-about-us-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:23350;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(219,74,'_wp_attachment_image_alt','About Sentinel Industrial Supply'),
(220,4,'_thumbnail_id','74'),
(221,75,'_wp_attached_file','2026/09/page-5-products.png'),
(222,75,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:27:\"2026/09/page-5-products.png\";s:8:\"filesize\";i:17382;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:27:\"page-5-products-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9833;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:27:\"page-5-products-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5801;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:27:\"page-5-products-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:29202;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(223,75,'_wp_attachment_image_alt','Industrial safety and automation catalog'),
(224,5,'_thumbnail_id','75'),
(225,76,'_wp_attached_file','2026/09/page-6-services.png'),
(226,76,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:27:\"2026/09/page-6-services.png\";s:8:\"filesize\";i:17442;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:27:\"page-6-services-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9108;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:27:\"page-6-services-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5623;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:27:\"page-6-services-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:27785;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(227,76,'_wp_attachment_image_alt','Spec lookup and compliance services'),
(228,6,'_thumbnail_id','76'),
(229,77,'_wp_attached_file','2026/09/page-7-training.png'),
(230,77,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:27:\"2026/09/page-7-training.png\";s:8:\"filesize\";i:14976;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:27:\"page-7-training-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9868;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:27:\"page-7-training-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6317;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:27:\"page-7-training-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:28234;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(231,77,'_wp_attachment_image_alt','Machine safety training programs'),
(232,7,'_thumbnail_id','77'),
(233,78,'_wp_attached_file','2026/09/page-8-automation.png'),
(234,78,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:29:\"2026/09/page-8-automation.png\";s:8:\"filesize\";i:14700;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:29:\"page-8-automation-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:10006;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:29:\"page-8-automation-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6576;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:29:\"page-8-automation-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:28650;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(235,78,'_wp_attachment_image_alt','SIS automation solutions'),
(236,8,'_thumbnail_id','78'),
(237,79,'_wp_attached_file','2026/09/page-9-contact-us.png'),
(238,79,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:29:\"2026/09/page-9-contact-us.png\";s:8:\"filesize\";i:15828;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:29:\"page-9-contact-us-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:8310;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:29:\"page-9-contact-us-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5955;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:29:\"page-9-contact-us-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:24627;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(239,79,'_wp_attachment_image_alt','Contact Sentinel Industrial Supply'),
(240,9,'_thumbnail_id','79'),
(241,80,'_wp_attached_file','2026/09/page-10-veridian-switches.png'),
(242,80,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:37:\"2026/09/page-10-veridian-switches.png\";s:8:\"filesize\";i:17694;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:37:\"page-10-veridian-switches-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9471;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:37:\"page-10-veridian-switches-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6327;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:37:\"page-10-veridian-switches-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:28702;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(243,80,'_wp_attachment_image_alt','Veridian safety interlock switches'),
(244,10,'_thumbnail_id','80'),
(245,81,'_wp_attached_file','2026/09/page-11-veridian-estop.png'),
(246,81,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:34:\"2026/09/page-11-veridian-estop.png\";s:8:\"filesize\";i:18666;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:34:\"page-11-veridian-estop-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:12555;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:34:\"page-11-veridian-estop-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:7494;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:34:\"page-11-veridian-estop-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:34269;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(247,81,'_wp_attachment_image_alt','Veridian emergency stop devices'),
(248,11,'_thumbnail_id','81'),
(249,82,'_wp_attached_file','2026/09/page-12-veridian-curtains.png'),
(250,82,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:37:\"2026/09/page-12-veridian-curtains.png\";s:8:\"filesize\";i:17021;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:37:\"page-12-veridian-curtains-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9070;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:37:\"page-12-veridian-curtains-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5747;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:37:\"page-12-veridian-curtains-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:27399;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(251,82,'_wp_attachment_image_alt','Veridian Type 4 safety light curtains'),
(252,12,'_thumbnail_id','82'),
(253,83,'_wp_attached_file','2026/09/page-13-home.png'),
(254,83,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:24:\"2026/09/page-13-home.png\";s:8:\"filesize\";i:15397;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:24:\"page-13-home-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9037;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:24:\"page-13-home-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6051;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:24:\"page-13-home-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:27661;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(255,83,'_wp_attachment_image_alt','Sentinel Industrial Supply'),
(256,13,'_thumbnail_id','83'),
(257,84,'_wp_attached_file','2026/09/post-14-burn-it-bx54.png'),
(258,84,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:32:\"2026/09/post-14-burn-it-bx54.png\";s:8:\"filesize\";i:12116;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:32:\"post-14-burn-it-bx54-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:7426;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:32:\"post-14-burn-it-bx54-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:4793;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:32:\"post-14-burn-it-bx54-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:20152;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(259,84,'_wp_attachment_image_alt','Burn it with BX54'),
(260,14,'_thumbnail_id','84'),
(261,85,'_wp_attached_file','2026/09/post-15-ul508a-update.png'),
(262,85,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:33:\"2026/09/post-15-ul508a-update.png\";s:8:\"filesize\";i:17676;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:33:\"post-15-ul508a-update-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:8391;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:33:\"post-15-ul508a-update-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5300;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:33:\"post-15-ul508a-update-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:24888;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(263,85,'_wp_attachment_image_alt','UL508A panel shop update'),
(264,15,'_thumbnail_id','85'),
(265,86,'_wp_attached_file','2026/09/post-16-imts-recap.png'),
(266,86,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:30:\"2026/09/post-16-imts-recap.png\";s:8:\"filesize\";i:12877;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:30:\"post-16-imts-recap-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6461;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:30:\"post-16-imts-recap-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:4129;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:30:\"post-16-imts-recap-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:19356;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(267,86,'_wp_attachment_image_alt','On the floor at IMTS'),
(268,16,'_thumbnail_id','86'),
(269,87,'_wp_attached_file','2026/09/post-19-bx54-lens.png'),
(270,87,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:29:\"2026/09/post-19-bx54-lens.png\";s:8:\"filesize\";i:17953;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:29:\"post-19-bx54-lens-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:12518;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:29:\"post-19-bx54-lens-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:7337;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:29:\"post-19-bx54-lens-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:33324;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(271,87,'_wp_attachment_image_alt','Reordering the BX54 focus lens'),
(272,19,'_thumbnail_id','87'),
(273,88,'_wp_attached_file','2026/09/post-21-jit-delivery.png'),
(274,88,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:32:\"2026/09/post-21-jit-delivery.png\";s:8:\"filesize\";i:15556;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:32:\"post-21-jit-delivery-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:8770;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:32:\"post-21-jit-delivery-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5467;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:32:\"post-21-jit-delivery-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:24501;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(275,88,'_wp_attachment_image_alt','Just-in-time delivery for MRO parts'),
(276,21,'_thumbnail_id','88'),
(277,89,'_wp_attached_file','2026/09/post-22-vending.png'),
(278,89,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:27:\"2026/09/post-22-vending.png\";s:8:\"filesize\";i:15163;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:27:\"post-22-vending-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:9313;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:27:\"post-22-vending-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:5327;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:27:\"post-22-vending-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:24982;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(279,89,'_wp_attachment_image_alt','Vending and inventory management for shop-floor consumables'),
(280,22,'_thumbnail_id','89'),
(281,90,'_wp_attached_file','2026/09/post-23-conveyors.png'),
(282,90,'_wp_attachment_metadata','a:6:{s:5:\"width\";i:800;s:6:\"height\";i:500;s:4:\"file\";s:29:\"2026/09/post-23-conveyors.png\";s:8:\"filesize\";i:18737;s:5:\"sizes\";a:3:{s:6:\"medium\";a:5:{s:4:\"file\";s:29:\"post-23-conveyors-300x188.png\";s:5:\"width\";i:300;s:6:\"height\";i:188;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:10944;}s:9:\"thumbnail\";a:5:{s:4:\"file\";s:29:\"post-23-conveyors-150x150.png\";s:5:\"width\";i:150;s:6:\"height\";i:150;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:6442;}s:12:\"medium_large\";a:5:{s:4:\"file\";s:29:\"post-23-conveyors-768x480.png\";s:5:\"width\";i:768;s:6:\"height\";i:480;s:9:\"mime-type\";s:9:\"image/png\";s:8:\"filesize\";i:31061;}}s:10:\"image_meta\";a:12:{s:8:\"aperture\";s:1:\"0\";s:6:\"credit\";s:0:\"\";s:6:\"camera\";s:0:\"\";s:7:\"caption\";s:0:\"\";s:17:\"created_timestamp\";s:1:\"0\";s:9:\"copyright\";s:0:\"\";s:12:\"focal_length\";s:1:\"0\";s:3:\"iso\";s:1:\"0\";s:13:\"shutter_speed\";s:1:\"0\";s:5:\"title\";s:0:\"\";s:11:\"orientation\";s:1:\"0\";s:8:\"keywords\";a:0:{}}}'),
(283,90,'_wp_attachment_image_alt','Conveyor and material handling components now in stock'),
(284,23,'_thumbnail_id','90');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
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
(4,'Trade Show Recaps','trade-show-recaps',0),
(5,'Shop Floor Services','shop-floor-services',0),
(6,'twentytwentyfive','twentytwentyfive',0);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_term_taxonomy`
--

LOCK TABLES `wp_term_taxonomy` WRITE;
/*!40000 ALTER TABLE `wp_term_taxonomy` DISABLE KEYS */;
INSERT INTO `wp_term_taxonomy` VALUES
(1,1,'category','',0,0),
(2,2,'category','',0,3),
(3,3,'category','',0,1),
(4,4,'category','',0,1),
(5,5,'category','',0,2),
(6,6,'wp_theme','',0,1);
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
(16,4,0),
(19,2,0),
(21,5,0),
(22,5,0),
(23,2,0),
(73,6,0);
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

-- Dump completed on 2026-09-10 14:42:22
