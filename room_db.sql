-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3308
-- Generation Time: Apr 25, 2025 at 07:21 AM
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
-- Database: `room_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `room_types`
--

CREATE TABLE `room_types` (
  `id` int NOT NULL,
  `type_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `price_per_night` float NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `room_types`
--

INSERT INTO `room_types` (`id`, `type_code`, `name`, `description`, `price_per_night`, `is_active`) VALUES
(1, 'rt001', 'Standard Room', 'Basic room with essential amenities', 500000, 1),
(2, 'rt002', 'Deluxe Room', 'Spacious room with upgraded furnishings', 750000, 1),
(3, 'rt003', 'Executive Suite', 'Luxurious suite with separate living area', 1200000, 1),
(4, 'rt004', 'Family Room', 'Large room suitable for families', 850000, 1),
(5, 'rt005', 'Honeymoon Suite', 'Romantic suite with special amenities', 1500000, 1),
(6, 'rt006', 'Business Room', 'Room with work desk and business amenities', 700000, 1),
(7, 'rt007', 'Pool View Room', 'Room with direct pool access', 900000, 1),
(8, 'rt008', 'Presidential Suite', 'Most luxurious suite in the hotel', 2500000, 1),
(9, 'rt009', 'Accessible Room', 'Room designed for guests with disabilities', 600000, 1),
(10, 'rt010', 'Economy Room', 'Compact room for budget travelers', 400000, 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `room_types`
--
ALTER TABLE `room_types`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type_code` (`type_code`),
  ADD KEY `idx_is_active` (`is_active`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `room_types`
--
ALTER TABLE `room_types`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
