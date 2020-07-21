CREATE DATABASE `atolo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE `atolo`.`KYC_COMPLETE` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(127) NOT NULL,
  `email` varchar(127) NOT NULL,
  `tx_hash` varchar(127) DEFAULT NULL,
  `kyc_level` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address_UNIQUE` (`address`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `tx_hash_UNIQUE` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

