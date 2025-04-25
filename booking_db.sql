-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3308
-- Generation Time: Apr 25, 2025 at 07:20 AM
-- Server version: 8.0.30
-- PHP Version: 8.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `booking_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int NOT NULL,
  `booking_uid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `guest_uid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `room_type_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `check_in_date` date NOT NULL,
  `check_out_date` date NOT NULL,
  `total_price` float NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending_payment',
  `payment_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `booking_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cancellation_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `cancelled_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `booking_uid`, `guest_uid`, `room_type_code`, `check_in_date`, `check_out_date`, `total_price`, `status`, `payment_id`, `booking_time`, `cancellation_reason`, `cancelled_at`) VALUES
(1, 'book001', 'guest001', 'rt001', '2025-06-01', '2025-06-03', 1000000, 'confirmed', 'pay001', '2025-05-01 10:00:00', NULL, NULL),
(2, 'book002', 'guest002', 'rt002', '2025-06-05', '2025-06-07', 1500000, 'confirmed', 'pay002', '2025-05-02 11:00:00', NULL, NULL),
(3, 'book003', 'guest003', 'rt003', '2025-06-10', '2025-06-12', 2400000, 'pending_payment', NULL, '2025-05-03 12:00:00', NULL, NULL),
(4, 'book004', 'guest004', 'rt004', '2025-06-15', '2025-06-17', 1700000, 'confirmed', 'pay003', '2025-05-04 13:00:00', NULL, NULL),
(5, 'book005', 'guest005', 'rt005', '2025-06-20', '2025-06-22', 3000000, 'cancelled', NULL, '2025-05-05 14:00:00', 'Change of plans', '2025-05-06 09:00:00'),
(6, 'book006', 'guest006', 'rt006', '2025-06-25', '2025-06-27', 1400000, 'confirmed', 'pay004', '2025-05-06 15:00:00', NULL, NULL),
(7, 'book007', 'guest007', 'rt007', '2025-07-01', '2025-07-03', 1800000, 'confirmed', 'pay005', '2025-05-07 16:00:00', NULL, NULL),
(8, 'book008', 'guest008', 'rt008', '2025-07-05', '2025-07-07', 5000000, 'pending_payment', NULL, '2025-05-08 17:00:00', NULL, NULL),
(9, 'book009', 'guest009', 'rt009', '2025-07-10', '2025-07-12', 1200000, 'confirmed', 'pay006', '2025-05-09 18:00:00', NULL, NULL),
(10, 'book010', 'guest010', 'rt010', '2025-07-15', '2025-07-17', 800000, 'cancelled', NULL, '2025-05-10 19:00:00', 'Found better deal', '2025-05-11 10:00:00'),
(11, 'book011', 'guest011', 'rt001', '2025-07-20', '2025-07-22', 1000000, 'confirmed', 'pay007', '2025-05-11 10:00:00', NULL, NULL),
(12, 'book012', 'guest012', 'rt002', '2025-07-25', '2025-07-27', 1500000, 'pending_payment', NULL, '2025-05-12 11:00:00', NULL, NULL),
(13, 'book013', 'guest013', 'rt003', '2025-08-01', '2025-08-03', 2400000, 'confirmed', 'pay008', '2025-05-13 12:00:00', NULL, NULL),
(14, 'book014', 'guest014', 'rt004', '2025-08-05', '2025-08-07', 1700000, 'confirmed', 'pay009', '2025-05-14 13:00:00', NULL, NULL),
(15, 'book015', 'guest015', 'rt005', '2025-08-10', '2025-08-12', 3000000, 'pending_payment', NULL, '2025-05-15 14:00:00', NULL, NULL),
(16, 'book016', 'guest016', 'rt006', '2025-08-15', '2025-08-17', 1400000, 'confirmed', 'pay010', '2025-05-16 15:00:00', NULL, NULL),
(17, 'book017', 'guest017', 'rt007', '2025-08-20', '2025-08-22', 1800000, 'cancelled', NULL, '2025-05-17 16:00:00', 'Travel restrictions', '2025-05-18 11:00:00'),
(18, 'book018', 'guest018', 'rt008', '2025-08-25', '2025-08-27', 5000000, 'confirmed', 'pay011', '2025-05-18 17:00:00', NULL, NULL),
(19, 'book019', 'guest019', 'rt009', '2025-09-01', '2025-09-03', 1200000, 'confirmed', 'pay012', '2025-05-19 18:00:00', NULL, NULL),
(20, 'book020', 'guest020', 'rt010', '2025-09-05', '2025-09-07', 800000, 'pending_payment', NULL, '2025-05-20 19:00:00', NULL, NULL),
(21, 'book021', 'guest021', 'rt001', '2025-09-10', '2025-09-12', 1000000, 'confirmed', 'pay013', '2025-05-21 10:00:00', NULL, NULL),
(22, 'book022', 'guest022', 'rt002', '2025-09-15', '2025-09-17', 1500000, 'confirmed', 'pay014', '2025-05-22 11:00:00', NULL, NULL),
(23, 'book023', 'guest023', 'rt003', '2025-09-20', '2025-09-22', 2400000, 'cancelled', NULL, '2025-05-23 12:00:00', 'Family emergency', '2025-05-24 09:00:00'),
(24, 'book024', 'guest024', 'rt004', '2025-09-25', '2025-09-27', 1700000, 'confirmed', 'pay015', '2025-05-24 13:00:00', NULL, NULL),
(25, 'book025', 'guest025', 'rt005', '2025-10-01', '2025-10-03', 3000000, 'pending_payment', NULL, '2025-05-25 14:00:00', NULL, NULL),
(26, 'book026', 'guest026', 'rt006', '2025-10-05', '2025-10-07', 1400000, 'confirmed', 'pay016', '2025-05-26 15:00:00', NULL, NULL),
(27, 'book027', 'guest027', 'rt007', '2025-10-10', '2025-10-12', 1800000, 'confirmed', 'pay017', '2025-05-27 16:00:00', NULL, NULL),
(28, 'book028', 'guest028', 'rt008', '2025-10-15', '2025-10-17', 5000000, 'pending_payment', NULL, '2025-05-28 17:00:00', NULL, NULL),
(29, 'book029', 'guest029', 'rt009', '2025-10-20', '2025-10-22', 1200000, 'confirmed', 'pay018', '2025-05-29 18:00:00', NULL, NULL),
(30, 'book030', 'guest030', 'rt010', '2025-10-25', '2025-10-27', 800000, 'confirmed', 'pay019', '2025-05-30 19:00:00', NULL, NULL),
(31, 'book031', 'guest001', 'rt001', '2025-11-01', '2025-11-03', 1000000, 'pending_payment', NULL, '2025-05-31 10:00:00', NULL, NULL),
(32, 'book032', 'guest002', 'rt002', '2025-11-05', '2025-11-07', 1500000, 'confirmed', 'pay020', '2025-06-01 11:00:00', NULL, NULL),
(33, 'book033', 'guest003', 'rt003', '2025-11-10', '2025-11-12', 2400000, 'confirmed', 'pay021', '2025-06-02 12:00:00', NULL, NULL),
(34, 'book034', 'guest004', 'rt004', '2025-11-15', '2025-11-17', 1700000, 'cancelled', NULL, '2025-06-03 13:00:00', 'Business trip cancelled', '2025-06-04 10:00:00'),
(35, 'book035', 'guest005', 'rt005', '2025-11-20', '2025-11-22', 3000000, 'confirmed', 'pay022', '2025-06-04 14:00:00', NULL, NULL),
(36, 'book036', 'guest006', 'rt006', '2025-11-25', '2025-11-27', 1400000, 'pending_payment', NULL, '2025-06-05 15:00:00', NULL, NULL),
(37, 'book037', 'guest007', 'rt007', '2025-12-01', '2025-12-03', 1800000, 'confirmed', 'pay023', '2025-06-06 16:00:00', NULL, NULL),
(38, 'book038', 'guest008', 'rt008', '2025-12-05', '2025-12-07', 5000000, 'confirmed', 'pay024', '2025-06-07 17:00:00', NULL, NULL),
(39, 'book039', 'guest009', 'rt009', '2025-12-10', '2025-12-12', 1200000, 'cancelled', NULL, '2025-06-08 18:00:00', 'Pengen aja', '2025-04-25 06:53:05'),
(40, 'book040', 'guest010', 'rt010', '2025-12-15', '2025-12-17', 800000, 'confirmed', 'pay025', '2025-06-09 19:00:00', NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `booking_uid` (`booking_uid`),
  ADD KEY `idx_guest_uid` (`guest_uid`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_check_in_date` (`check_in_date`),
  ADD KEY `idx_room_type_code` (`room_type_code`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
