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
-- Database: `payment_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `payment_transactions`
--

CREATE TABLE `payment_transactions` (
  `id` int NOT NULL,
  `payment_uid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `booking_uid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `requested_amount` float NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'processing',
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `failure_reason` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_time` datetime NOT NULL,
  `processed_at` datetime DEFAULT NULL,
  `is_fraud` tinyint(1) DEFAULT '0',
  `fraud_score` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payment_transactions`
--

INSERT INTO `payment_transactions` (`id`, `payment_uid`, `booking_uid`, `requested_amount`, `status`, `message`, `failure_reason`, `request_time`, `processed_at`, `is_fraud`, `fraud_score`) VALUES
(1, 'pay001', 'book001', 1000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-01 10:05:00', '2025-05-01 10:07:00', 0, 0.15),
(2, 'pay002', 'book002', 1500000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-02 11:05:00', '2025-05-02 11:07:00', 0, 0.12),
(3, 'pay003', 'book004', 1700000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-04 13:05:00', '2025-05-04 13:07:00', 0, 0.18),
(4, 'pay004', 'book006', 1400000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-06 15:05:00', '2025-05-06 15:07:00', 0, 0.22),
(5, 'pay005', 'book007', 1800000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-07 16:05:00', '2025-05-07 16:07:00', 0, 0.1),
(6, 'pay006', 'book009', 1200000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-09 18:05:00', '2025-05-09 18:07:00', 0, 0.14),
(7, 'pay007', 'book011', 1000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-11 10:05:00', '2025-05-11 10:07:00', 0, 0.25),
(8, 'pay008', 'book013', 2400000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-13 12:05:00', '2025-05-13 12:07:00', 0, 0.3),
(9, 'pay009', 'book014', 1700000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-14 13:05:00', '2025-05-14 13:07:00', 0, 0.11),
(10, 'pay010', 'book016', 1400000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-16 15:05:00', '2025-05-16 15:07:00', 0, 0.19),
(11, 'pay011', 'book018', 5000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-18 17:05:00', '2025-05-18 17:07:00', 0, 0.45),
(12, 'pay012', 'book019', 1200000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-19 18:05:00', '2025-05-19 18:07:00', 0, 0.2),
(13, 'pay013', 'book021', 1000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-21 10:05:00', '2025-05-21 10:07:00', 0, 0.15),
(14, 'pay014', 'book022', 1500000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-22 11:05:00', '2025-05-22 11:07:00', 0, 0.12),
(15, 'pay015', 'book024', 1700000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-24 13:05:00', '2025-05-24 13:07:00', 0, 0.18),
(16, 'pay016', 'book026', 1400000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-26 15:05:00', '2025-05-26 15:07:00', 0, 0.22),
(17, 'pay017', 'book027', 1800000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-27 16:05:00', '2025-05-27 16:07:00', 0, 0.1),
(18, 'pay018', 'book029', 1200000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-29 18:05:00', '2025-05-29 18:07:00', 0, 0.14),
(19, 'pay019', 'book030', 800000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-05-30 19:05:00', '2025-05-30 19:07:00', 0, 0.25),
(20, 'pay020', 'book032', 1500000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-01 11:05:00', '2025-06-01 11:07:00', 0, 0.3),
(21, 'pay021', 'book033', 2400000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-02 12:05:00', '2025-06-02 12:07:00', 0, 0.11),
(22, 'pay022', 'book035', 3000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-04 14:05:00', '2025-06-04 14:07:00', 0, 0.19),
(23, 'pay023', 'book037', 1800000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-06 16:05:00', '2025-06-06 16:07:00', 0, 0.45),
(24, 'pay024', 'book038', 5000000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-07 17:05:00', '2025-06-07 17:07:00', 0, 0.2),
(25, 'pay025', 'book040', 800000, 'success', 'Pembayaran berhasil diproses', NULL, '2025-06-09 19:05:00', '2025-06-09 19:07:00', 0, 0.15),
(26, 'pay026', 'book003', 2400000, 'failed', 'Pembayaran gagal', 'Kartu kredit ditolak', '2025-05-03 12:05:00', '2025-05-03 12:07:00', 1, 0.85),
(27, 'pay027', 'book005', 3000000, 'failed', 'Pembayaran gagal', 'Saldo tidak mencukupi', '2025-05-05 14:05:00', '2025-05-05 14:07:00', 1, 0.82),
(28, 'pay028', 'book008', 5000000, 'failed', 'Pembayaran gagal', 'Kartu kredit kadaluarsa', '2025-05-08 17:05:00', '2025-05-08 17:07:00', 1, 0.78),
(29, 'pay029', 'book010', 800000, 'failed', 'Pembayaran gagal', 'Transaksi dicurigai', '2025-05-10 19:05:00', '2025-05-10 19:07:00', 1, 0.92),
(30, 'pay030', 'book012', 1500000, 'failed', 'Pembayaran gagal', 'Kartu kredit diblokir', '2025-05-12 11:05:00', '2025-05-12 11:07:00', 1, 0.88),
(31, 'pay031', 'book015', 3000000, 'failed', 'Pembayaran gagal', 'Limit kartu terlampaui', '2025-05-15 14:05:00', '2025-05-15 14:07:00', 1, 0.75),
(32, 'pay032', 'book017', 1800000, 'failed', 'Pembayaran gagal', 'Kartu kredit hilang', '2025-05-17 16:05:00', '2025-05-17 16:07:00', 1, 0.81),
(33, 'pay033', 'book020', 800000, 'failed', 'Pembayaran gagal', 'Transaksi tidak sah', '2025-05-20 19:05:00', '2025-05-20 19:07:00', 1, 0.95),
(34, 'pay034', 'book023', 2400000, 'failed', 'Pembayaran gagal', 'Kartu kredit dicuri', '2025-05-23 12:05:00', '2025-05-23 12:07:00', 1, 0.89),
(35, 'pay035', 'book025', 3000000, 'failed', 'Pembayaran gagal', 'Sistem pembayaran down', '2025-05-25 14:05:00', '2025-05-25 14:07:00', 1, 0.76),
(36, 'pay036', 'book028', 5000000, 'failed', 'Pembayaran gagal', 'Koneksi terputus', '2025-05-28 17:05:00', '2025-05-28 17:07:00', 1, 0.83),
(37, 'pay037', 'book031', 1000000, 'processing', 'Pembayaran sedang diproses', NULL, '2025-05-31 10:05:00', NULL, 0, 0.35),
(38, 'pay038', 'book034', 1700000, 'processing', 'Pembayaran sedang diproses', NULL, '2025-06-03 13:05:00', NULL, 0, 0.42),
(39, 'pay039', 'book036', 1400000, 'processing', 'Pembayaran sedang diproses', NULL, '2025-06-05 15:05:00', NULL, 0, 0.38),
(40, 'pay040', 'book039', 1200000, 'processing', 'Pembayaran sedang diproses', NULL, '2025-06-08 18:05:00', NULL, 0, 0.45);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `payment_transactions`
--
ALTER TABLE `payment_transactions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `payment_uid` (`payment_uid`),
  ADD KEY `idx_payment_uid` (`payment_uid`),
  ADD KEY `idx_booking_uid` (`booking_uid`),
  ADD KEY `idx_payment_status` (`status`),
  ADD KEY `idx_payment_fraud` (`is_fraud`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `payment_transactions`
--
ALTER TABLE `payment_transactions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
