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
-- Database: `guest_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `guests`
--

CREATE TABLE `guests` (
  `id` int NOT NULL,
  `guest_uid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `guests`
--

INSERT INTO `guests` (`id`, `guest_uid`, `name`, `email`, `phone`, `is_deleted`) VALUES
(1, 'guest001', 'Budi Santoso', 'budi.santoso@example.com', '081234567001', 0),
(2, 'guest002', 'Ani Wijaya', 'ani.wijaya@example.com', '081234567002', 0),
(3, 'guest003', 'Citra Dewi', 'citra.dewi@example.com', '081234567003', 0),
(4, 'guest004', 'Dodi Pratama', 'dodi.pratama@example.com', '081234567004', 0),
(5, 'guest005', 'Eka Putri', 'eka.putri@example.com', '081234567005', 0),
(6, 'guest006', 'Fajar Nugroho', 'fajar.nugroho@example.com', '081234567006', 0),
(7, 'guest007', 'Gita Sari', 'gita.sari@example.com', '081234567007', 0),
(8, 'guest008', 'Hendra Setiawan', 'hendra.setiawan@example.com', '081234567008', 0),
(9, 'guest009', 'Intan Permata', 'intan.permata@example.com', '081234567009', 0),
(10, 'guest010', 'Joko Susilo', 'joko.susilo@example.com', '081234567010', 0),
(11, 'guest011', 'Kartika Wulandari', 'kartika.wulandari@example.com', '081234567011', 0),
(12, 'guest012', 'Luki Hermawan', 'luki.hermawan@example.com', '081234567012', 0),
(13, 'guest013', 'Maya Indah', 'maya.indah@example.com', '081234567013', 0),
(14, 'guest014', 'Nando Pratama', 'nando.pratama@example.com', '081234567014', 0),
(15, 'guest015', 'Oki Ramadhan', 'oki.ramadhan@example.com', '081234567015', 0),
(16, 'guest016', 'Putri Ayu', 'putri.ayu@example.com', '081234567016', 0),
(17, 'guest017', 'Rudi Hartono', 'rudi.hartono@example.com', '081234567017', 0),
(18, 'guest018', 'Siti Rahayu', 'siti.rahayu@example.com', '081234567018', 0),
(19, 'guest019', 'Tono Wijaya', 'tono.wijaya@example.com', '081234567019', 0),
(20, 'guest020', 'Umi Kalsum', 'umi.kalsum@example.com', '081234567020', 0),
(21, 'guest021', 'Vino Ginting', 'vino.ginting@example.com', '081234567021', 1),
(22, 'guest022', 'Wulan Sari', 'wulan.sari@example.com', '081234567022', 1),
(23, 'guest023', 'Xavier Tan', 'xavier.tan@example.com', '081234567023', 0),
(24, 'guest024', 'Yuni Astuti', 'yuni.astuti@example.com', '081234567024', 0),
(25, 'guest025', 'Zaki Ahmad', 'zaki.ahmad@example.com', '081234567025', 0),
(26, 'guest026', 'Ade Putra', 'ade.putra@example.com', '081234567026', 0),
(27, 'guest027', 'Bella Nur', 'bella.nur@example.com', '081234567027', 0),
(28, 'guest028', 'Cahyo Purnomo', 'cahyo.purnomo@example.com', '081234567028', 0),
(29, 'guest029', 'Dina Melati', 'dina.melati@example.com', '081234567029', 0),
(30, 'guest030', 'Eko Prasetyo', 'eko.prasetyo@example.com', '081234567030', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `guests`
--
ALTER TABLE `guests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `guest_uid` (`guest_uid`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_guest_email` (`email`),
  ADD KEY `idx_is_deleted` (`is_deleted`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `guests`
--
ALTER TABLE `guests`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
