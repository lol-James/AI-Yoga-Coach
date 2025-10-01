-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 
-- 伺服器版本： 10.1.38-MariaDB
-- PHP 版本： 7.3.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `yoga_coach_database`
--

-- --------------------------------------------------------

--
-- 資料表結構 `comment_dislike`
--

CREATE TABLE `comment_dislike` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `comment_dislike`
--

INSERT INTO `comment_dislike` (`id`, `user_id`, `comment_id`) VALUES
(4, 13, 40);

-- --------------------------------------------------------

--
-- 資料表結構 `comment_like`
--

CREATE TABLE `comment_like` (
  `id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `comment_like`
--

INSERT INTO `comment_like` (`id`, `comment_id`, `user_id`) VALUES
(2, 40, 13),
(5, 39, 17);

-- --------------------------------------------------------

--
-- 資料表結構 `comment_page`
--

CREATE TABLE `comment_page` (
  `id` int(11) NOT NULL,
  `comment_user_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `comment_date` date NOT NULL,
  `comment_text` text COLLATE utf8_unicode_ci NOT NULL,
  `comment_like` int(11) DEFAULT '0',
  `comment_dislike` int(11) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `comment_page`
--

INSERT INTO `comment_page` (`id`, `comment_user_id`, `post_id`, `comment_date`, `comment_text`, `comment_like`, `comment_dislike`) VALUES
(1, 1, 31, '2025-07-22', '8465132', 0, 0),
(2, 1, 31, '2025-07-22', '7\\2\\75', 0, 0),
(3, 1, 31, '2025-07-22', '5\\757\\5', 0, 0),
(4, 1, 31, '2025-07-22', '5\\757\\', 0, 0),
(5, 1, 31, '2025-07-22', '\\5\\5', 0, 0),
(6, 1, 31, '2025-07-22', '\\5\\5', 0, 0),
(7, 1, 31, '2025-07-22', '\\4\\4', 0, 0),
(8, 1, 31, '2025-07-22', '5533\n3', 0, 0),
(9, 1, 30, '2025-07-22', '3\\75', 0, 0),
(10, 1, 30, '2025-07-22', '111111', 0, 0),
(11, 1, 31, '2025-07-22', '11111', 0, 0),
(14, 1, 28, '2025-07-23', '45632', 0, 0),
(15, 1, 27, '2025-07-23', '48612', 0, 0),
(16, 1, 31, '2025-07-23', '123', 0, 0),
(17, 1, 31, '2025-07-23', 'DWADAWDAWDAWDWA', 0, 0),
(18, 1, 31, '2025-07-23', 'WDWADADAWDWDWADADAWDWDWADADAWDWDWADADAWD', 0, 0),
(19, 1, 31, '2025-07-23', 'DWADAWDAWD\nAWDAWDDAWDAWDAWDAWDAWD\nAWDAWDAWDAWDAWDAW', 0, 0),
(20, 1, 31, '2025-07-23', 'AWDWADAW WDAWDAW DAWDWA D AWD AWD', 0, 0),
(21, 1, 31, '2025-07-23', 'AWD AWDADWADWADW AD AWD AWD AWD AWD AW DAW DAW DAWD AWD AWD AWD AW D', 0, 0),
(22, 1, 31, '2025-07-23', '123445678910 123445678910 123445678910 123445678910', 9, 7),
(23, 1, 31, '2025-07-23', '123445678910 123445678910 123445678910 123445678910 123445678910 123445678910 123445678910 123445678910 123445678910', 5, 5),
(24, 1, 31, '2025-07-23', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1 ABCDEFGHIJKLMNOPQRSTUVWXYZ2 ABCDEFGHIJKLMNOPQRSTUVWXYZ3', 8, 5),
(25, 1, 26, '2025-07-23', 'AWD', 0, 0),
(26, 1, 26, '2025-07-23', 'AWD', 0, 0),
(27, 1, 26, '2025-07-23', 'AWD', 0, 0),
(28, 1, 26, '2025-07-23', 'AWD', 0, 0),
(29, 1, 26, '2025-07-23', 'AWD', 0, 0),
(30, 1, 26, '2025-07-23', 'AWD', 0, 0),
(31, 1, 26, '2025-07-23', 'AWD', 0, 0),
(32, 1, 31, '2025-07-23', 'Dㄊ', 6, 3),
(33, 1, 22, '2025-07-23', '456', 0, 0),
(34, 1, 31, '2025-07-23', 'dㄎ', 0, 0),
(35, 1, 31, '2025-07-23', 'dwadawdawd', 0, 0),
(36, 1, 27, '2025-09-05', '123123', 0, 0),
(37, 17, 34, '2025-09-05', 'awdadw', 0, 0),
(38, 17, 33, '2025-09-05', 'dawdaw', 0, 0),
(39, 17, 35, '2025-09-05', '5312546', 3, 4),
(40, 17, 35, '2025-09-05', '752375', 1, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `favorite_songs`
--

CREATE TABLE `favorite_songs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `song_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `favorite_songs`
--

INSERT INTO `favorite_songs` (`id`, `user_id`, `song_name`) VALUES
(19, 19, '周杰倫 - 蒲公英的約定.mp3'),
(20, 19, '周杰倫 - 夜曲.mp3'),
(21, 19, '周杰倫 - 晴天.mp3'),
(22, 19, '周杰倫 - 七里香.mp3');

-- --------------------------------------------------------

--
-- 資料表結構 `post_like`
--

CREATE TABLE `post_like` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `post_like`
--

INSERT INTO `post_like` (`id`, `post_id`, `user_id`) VALUES
(8, 35, 17);

-- --------------------------------------------------------

--
-- 資料表結構 `record_detail`
--

CREATE TABLE `record_detail` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `mode` int(11) NOT NULL,
  `total_posture_count` int(11) DEFAULT '0',
  `daily_max_app_opens` int(11) DEFAULT '0',
  `max_daily_usage_hours` float DEFAULT '0',
  `min_daily_usage_hours` float DEFAULT '0',
  `longest_streak_days` int(11) DEFAULT '0',
  `total_usage_hours` float DEFAULT '0',
  `posture_id` int(11) DEFAULT NULL,
  `posture_name` text COLLATE utf8_unicode_ci,
  `total_completed` int(11) DEFAULT '0',
  `max_accuracy` float DEFAULT NULL,
  `min_accuracy` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `record_detail`
--

INSERT INTO `record_detail` (`id`, `user_id`, `mode`, `total_posture_count`, `daily_max_app_opens`, `max_daily_usage_hours`, `min_daily_usage_hours`, `longest_streak_days`, `total_usage_hours`, `posture_id`, `posture_name`, `total_completed`, `max_accuracy`, `min_accuracy`) VALUES
(1, 17, 0, 6, 0, 0, 0, 0, 0, 0, 'Bridge Pose', 6, 99.92, 94.18),
(2, 17, 0, 6, 0, 0, 0, 0, 0, 1, 'Chair Pose', 0, NULL, NULL),
(3, 17, 0, 6, 0, 0, 0, 0, 0, 2, 'Downward Facing Dog', 0, NULL, NULL),
(4, 17, 0, 6, 0, 0, 0, 0, 0, 3, 'Locust Pose', 0, NULL, NULL),
(5, 17, 0, 6, 0, 0, 0, 0, 0, 4, 'Plank Pose', 0, NULL, NULL),
(6, 17, 0, 6, 0, 0, 0, 0, 0, 5, 'Staff Pose', 0, NULL, NULL),
(7, 17, 0, 6, 0, 0, 0, 0, 0, 6, 'Triangle Pose', 0, NULL, NULL),
(8, 17, 0, 6, 0, 0, 0, 0, 0, 7, 'Warrior 1', 0, NULL, NULL),
(9, 17, 0, 6, 0, 0, 0, 0, 0, 8, 'Warrior 2', 0, NULL, NULL),
(10, 17, 0, 6, 0, 0, 0, 0, 0, 9, 'Warrior 3', 0, NULL, NULL),
(11, 17, 1, 0, 0, 0, 0, 0, 0, 0, 'Bridge Pose', 0, NULL, NULL),
(12, 17, 1, 0, 0, 0, 0, 0, 0, 1, 'Chair Pose', 0, NULL, NULL),
(13, 17, 1, 0, 0, 0, 0, 0, 0, 2, 'Downward Facing Dog', 0, NULL, NULL),
(14, 17, 1, 0, 0, 0, 0, 0, 0, 3, 'Locust Pose', 0, NULL, NULL),
(15, 17, 1, 0, 0, 0, 0, 0, 0, 4, 'Plank Pose', 0, NULL, NULL),
(16, 17, 1, 0, 0, 0, 0, 0, 0, 5, 'Staff Pose', 0, NULL, NULL),
(17, 17, 1, 0, 0, 0, 0, 0, 0, 6, 'Triangle Pose', 0, NULL, NULL),
(18, 17, 1, 0, 0, 0, 0, 0, 0, 7, 'Warrior 1', 0, NULL, NULL),
(19, 17, 1, 0, 0, 0, 0, 0, 0, 8, 'Warrior 2', 0, NULL, NULL),
(20, 17, 1, 0, 0, 0, 0, 0, 0, 9, 'Warrior 3', 0, NULL, NULL),
(21, 17, 2, 0, 0, 0, 0, 0, 0, 0, 'Bridge Pose', 0, NULL, NULL),
(22, 17, 2, 0, 0, 0, 0, 0, 0, 1, 'Chair Pose', 0, NULL, NULL),
(23, 17, 2, 0, 0, 0, 0, 0, 0, 2, 'Downward Facing Dog', 0, NULL, NULL),
(24, 17, 2, 0, 0, 0, 0, 0, 0, 3, 'Locust Pose', 0, NULL, NULL),
(25, 17, 2, 0, 0, 0, 0, 0, 0, 4, 'Plank Pose', 0, NULL, NULL),
(26, 17, 2, 0, 0, 0, 0, 0, 0, 5, 'Staff Pose', 0, NULL, NULL),
(27, 17, 2, 0, 0, 0, 0, 0, 0, 6, 'Triangle Pose', 0, NULL, NULL),
(28, 17, 2, 0, 0, 0, 0, 0, 0, 7, 'Warrior 1', 0, NULL, NULL),
(29, 17, 2, 0, 0, 0, 0, 0, 0, 8, 'Warrior 2', 0, NULL, NULL),
(30, 17, 2, 0, 0, 0, 0, 0, 0, 9, 'Warrior 3', 0, NULL, NULL);

-- --------------------------------------------------------

--
-- 資料表結構 `record_picture`
--

CREATE TABLE `record_picture` (
  `id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `accuracy` float DEFAULT NULL,
  `mode` int(11) DEFAULT NULL,
  `posture_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `session_id` text COLLATE utf8_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `record_picture`
--

INSERT INTO `record_picture` (`id`, `timestamp`, `accuracy`, `mode`, `posture_id`, `user_id`, `session_id`) VALUES
(0, '2025-09-30 16:08:13', 99.28, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:13', 99.04, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:14', 98.94, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:14', 98.87, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:15', 98.69, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:15', 98.52, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:16', 98.48, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:16', 98.82, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:17', 98.93, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:17', 99.04, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:18', 98.5, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:08:18', 98.61, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:06', 99.01, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:07', 99, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:07', 99.07, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:08', 98.78, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:08', 98.36, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:09', 99.07, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:09', 98.92, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:10', 98.75, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:10', 98.71, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:11', 98.56, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:11', 98.7, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:10:12', 98.7, 0, 0, 17, '1759219667.391654'),
(0, '2025-09-30 16:16:17', 99.15, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:18', 98.73, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:18', 98.93, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:19', 99.17, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:19', 98.83, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:20', 99.02, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:20', 98.67, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:21', 98.76, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:21', 98.91, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:22', 98.8, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:22', 98.72, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:16:23', 98.8, 0, 0, 17, '1759220159.007322'),
(0, '2025-09-30 16:57:01', 99.92, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:02', 99.45, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:02', 99.46, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:03', 98.75, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:03', 99.35, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:04', 98.78, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:04', 99.09, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:05', 98.6, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:05', 98.21, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:06', 94.18, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:06', 97.98, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 16:57:07', 99.11, 0, 0, 17, '1759222557.427433'),
(0, '2025-09-30 17:07:24', 98.89, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:25', 98.88, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:25', 98.92, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:26', 99.06, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:26', 98.96, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:27', 98.94, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:27', 98.75, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:28', 98.78, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:28', 98.61, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:29', 98.6, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:29', 98.8, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:07:30', 98.8, 0, 0, 17, '1759223183.633535'),
(0, '2025-09-30 17:32:01', 99.02, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:01', 98.89, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:02', 98.81, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:02', 98.81, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:03', 98.99, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:03', 98.2, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:04', 98.57, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:04', 98.42, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:05', 98.82, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:05', 98.99, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:06', 98.97, 0, 0, 17, '1759224654.686609'),
(0, '2025-09-30 17:32:06', 98.69, 0, 0, 17, '1759224654.686609');

-- --------------------------------------------------------

--
-- 資料表結構 `record_session`
--

CREATE TABLE `record_session` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `session_id` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `mode` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `record_session`
--

INSERT INTO `record_session` (`id`, `user_id`, `session_id`, `start_time`, `end_time`, `mode`) VALUES
(1, 17, '1758968300.782232', '2025-09-27 18:18:20', '2025-09-27 18:20:02', 0),
(2, 17, '1758968402.013119', '2025-09-27 18:20:02', '2025-09-27 18:20:33', 0),
(3, 17, '1758968433.919593', '2025-09-27 18:20:33', '2025-09-27 18:20:51', 0),
(4, 17, '1758968712.554851', '2025-09-27 18:25:12', '2025-09-27 18:25:21', 0),
(5, 17, '1758968861.96385', '2025-09-27 18:27:41', '2025-09-27 18:28:33', 0),
(6, 17, '1758968913.915077', '2025-09-27 18:28:33', '2025-09-27 18:28:48', 0),
(7, 17, '1758968928.422343', '2025-09-27 18:28:48', '2025-09-27 18:29:20', 0),
(8, 17, '1758970859.876487', '2025-09-27 19:00:59', '2025-09-27 19:20:00', 0),
(9, 17, '1758972000.515102', '2025-09-27 19:20:00', '2025-09-27 19:23:34', 0),
(10, 17, '1758972214.408012', '2025-09-27 19:23:34', '2025-09-27 19:28:37', 0),
(11, 17, '1758972517.071974', '2025-09-27 19:28:37', '2025-09-27 19:30:59', 0),
(12, 17, '1758972688.601244', '2025-09-27 19:31:28', '2025-09-27 19:31:38', 0),
(13, 17, '1758989466.971978', '2025-09-28 00:11:06', '2025-09-28 00:11:14', 0),
(14, 17, '1758990572.491185', '2025-09-28 00:29:32', '2025-09-28 00:30:17', 0),
(15, 17, '1758990743.318297', '2025-09-28 00:32:23', '2025-09-28 00:37:48', 0),
(16, 17, '1758991068.886329', '2025-09-28 00:37:48', '2025-09-28 00:40:15', 0),
(17, 17, '1759217191.171869', '2025-09-30 15:26:31', '2025-09-30 15:30:32', 0),
(18, 17, '1759217878.894717', '2025-09-30 15:37:58', '2025-09-30 15:38:51', 0),
(19, 17, '1759219667.391654', '2025-09-30 16:07:47', '2025-09-30 16:11:05', 0),
(20, 17, '1759220159.007322', '2025-09-30 16:15:59', '2025-09-30 16:19:20', 0),
(21, 17, '1759220647.629164', '2025-09-30 16:24:07', '2025-09-30 16:46:30', 0),
(22, 17, '1759222292.316259', '2025-09-30 16:51:32', '2025-09-30 16:55:57', 0),
(23, 17, '1759222557.427433', '2025-09-30 16:55:57', '2025-09-30 16:57:47', 0),
(24, 17, '1759222844.048354', '2025-09-30 17:00:44', '2025-09-30 17:04:12', 0),
(25, 17, '1759223081.317457', '2025-09-30 17:04:41', '2025-09-30 17:05:45', 0),
(26, 17, '1759223145.39338', '2025-09-30 17:05:45', '2025-09-30 17:05:51', 0),
(27, 17, '1759223183.633535', '2025-09-30 17:06:23', '2025-09-30 17:07:57', 0),
(28, 17, '1759223277.358961', '2025-09-30 17:07:57', '2025-09-30 17:08:07', 0),
(29, 17, '1759223619.766896', '2025-09-30 17:13:39', '2025-09-30 17:13:44', 0),
(30, 17, '1759223947.400987', '2025-09-30 17:19:07', '2025-09-30 17:29:05', 0),
(31, 17, '1759224545.763633', '2025-09-30 17:29:05', '2025-09-30 17:30:54', 0),
(32, 17, '1759224654.686609', '2025-09-30 17:30:54', '2025-09-30 17:32:35', 0),
(33, 17, '1759224755.667126', '2025-09-30 17:32:35', '2025-09-30 17:33:26', 0),
(34, 17, '1759225377.980389', '2025-09-30 17:42:57', '2025-09-30 17:43:01', 0),
(35, 17, '1759320712.521954', '2025-10-01 20:11:52', '2025-10-01 20:16:56', 0),
(36, 17, '1759321946.486569', '2025-10-01 20:32:26', '2025-10-01 20:37:17', 0),
(37, 17, '1759323028.060473', '2025-10-01 20:50:28', '2025-10-01 21:05:15', 0),
(38, 17, '1759323915.510354', '2025-10-01 21:05:15', '2025-10-01 21:07:05', 0),
(39, 17, '1759324397.206714', '2025-10-01 21:13:17', '2025-10-01 21:13:55', 0),
(40, 17, '1759324489.696055', '2025-10-01 21:14:49', '2025-10-01 21:17:01', 0),
(41, 17, '1759324854.594987', '2025-10-01 21:20:54', '2025-10-01 21:25:47', 0),
(42, 17, '1759326541.012724', '2025-10-01 21:49:01', '2025-10-01 21:49:14', 0),
(43, 17, '1759326834.361859', '2025-10-01 21:53:54', '2025-10-01 22:01:29', 0),
(44, 17, '1759327289.886363', '2025-10-01 22:01:29', '2025-10-01 22:02:18', 0);

-- --------------------------------------------------------

--
-- 資料表結構 `share_page`
--

CREATE TABLE `share_page` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `share_date` date NOT NULL,
  `share_text` text COLLATE utf8_unicode_ci,
  `share_content` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `share_like` int(11) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `share_page`
--

INSERT INTO `share_page` (`id`, `user_id`, `share_date`, `share_text`, `share_content`, `share_like`) VALUES
(1, 1, '2025-07-21', 'D', 'post_images\\downwardfacingdog_1001.jpg', 0),
(2, 1, '2025-07-21', '', 'post_images\\apose_3001.jpg', 0),
(6, 1, '2025-07-22', '123456', 'post_images\\Cow Pose.jpg', 3),
(7, 1, '2025-07-22', '', 'post_images\\Cow Pose.jpg', 0),
(8, 1, '2025-07-22', '5737837wqddw', 'post_images\\Cow Pose.jpg', 0),
(11, 1, '2025-07-22', '123', NULL, 0),
(13, 1, '2025-07-22', '4562132131321321321321hawuidhauwidhawuid', NULL, 0),
(16, 1, '2025-07-22', '你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!', NULL, 0),
(18, 1, '2025-07-22', 'Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!Hello World!!!', NULL, 0),
(19, 1, '2025-07-22', 'Hello World!!!Hello World!!!Hello World!!!Hello World!!!', NULL, 0),
(20, 1, '2025-07-22', 'adwaw5d13a2d1aw321d3a21d32aw1da23wd132aw1d23aw1d32aw1dw32', NULL, 0),
(21, 1, '2025-07-22', '? look at me and dis HUNK-O-RAMAA ?', NULL, 0),
(22, 1, '2025-07-22', 'awdawdawdawdawdawdwad', NULL, 1),
(23, 1, '2025-07-22', 'abcdefghijklmnopqrstuvwxyz', NULL, 0),
(24, 1, '2025-07-22', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', NULL, 3),
(25, 1, '2025-07-22', '你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!你們好!!!', NULL, 1),
(26, 1, '2025-07-22', '你們好!!!你們好!!!你們好!!!1你們好!!!你們好!!!你們好!!!2你們好!!!你們好!!!你們好!!!3你們好!!!你們好!!!你們好!!!4你們好!!!你們好!!!你們好!!!5你們好!!!你們好!!!你們好!!!6你們好!!!你們好!!!你們好!!!7你們好!!!你們好!!!你們好!!!8你們好!!!你們好!!!你們好!!!9你們好!!!你們好!!!你們好!!!10', NULL, 16),
(27, 1, '2025-07-22', 'dwad', NULL, 1),
(28, 1, '2025-07-22', 'daw', NULL, 1),
(29, 1, '2025-07-22', 'dwa', NULL, 3),
(30, 1, '2025-07-22', 'wad', NULL, 5),
(31, 1, '2025-07-22', 'WDDWA', NULL, 3),
(32, 1, '2025-09-05', '1321', NULL, 0),
(33, 1, '2025-09-05', '', 'post_images\\chair_002.jpg', 0),
(34, 17, '2025-09-05', 'awdawd', NULL, 2),
(35, 17, '2025-09-05', 'wdawdawd', NULL, 1),
(36, 17, '2025-10-01', '測試123456789', 'record_pic\\17_group1.png', 0),
(37, 17, '2025-10-01', '第二次測試23456789', 'record_pic\\17_group3.png', 0);

-- --------------------------------------------------------

--
-- 資料表結構 `songs`
--

CREATE TABLE `songs` (
  `song_id` int(11) NOT NULL,
  `song_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `song_path` varchar(255) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `songs`
--

INSERT INTO `songs` (`song_id`, `song_name`, `song_path`) VALUES
(25, '周杰倫 - 七里香.mp3', 'music\\周杰倫 - 七里香.mp3'),
(26, '周杰倫 - 以父之名.mp3', 'music\\周杰倫 - 以父之名.mp3'),
(27, '周杰倫 - 白色風車.mp3', 'music\\周杰倫 - 白色風車.mp3'),
(28, '周杰倫 - 夜曲.mp3', 'music\\周杰倫 - 夜曲.mp3'),
(29, '周杰倫 - 青花瓷.mp3', 'music\\周杰倫 - 青花瓷.mp3'),
(30, '周杰倫 - 晴天.mp3', 'music\\周杰倫 - 晴天.mp3'),
(31, '周杰倫 - 最長的電影.mp3', 'music\\周杰倫 - 最長的電影.mp3'),
(32, '周杰倫 - 菊花台.mp3', 'music\\周杰倫 - 菊花台.mp3'),
(33, '周杰倫 - 黑色毛衣.mp3', 'music\\周杰倫 - 黑色毛衣.mp3'),
(34, '周杰倫 - 蒲公英的約定.mp3', 'music\\周杰倫 - 蒲公英的約定.mp3'),
(35, '周杰倫 - 髮如雪.mp3', 'music\\周杰倫 - 髮如雪.mp3'),
(36, '周杰倫 - 擱淺.mp3', 'music\\周杰倫 - 擱淺.mp3');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `user_account` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `user_password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `user_picture` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` enum('Male','Female','Non binary','Prefer not to say') COLLATE utf8_unicode_ci DEFAULT NULL,
  `register_date` datetime DEFAULT NULL,
  `email` varchar(100) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `user_account`, `user_password`, `user_picture`, `age`, `gender`, `register_date`, `email`) VALUES
(1, 'non', '00000000', 'icons/non user.png', 0, '', NULL, 'deafult'),
(2, 'bob456', 'bobpass456', 'icons/pre.png', 30, 'Male', '2024-06-03 14:20:00', 'bob@gmail.com'),
(3, 'charlie789', 'charlie789', 'icons/quit.png', 28, 'Male', '2024-06-05 09:45:00', 'charlie@gmail.com'),
(4, 'diana007', 'diana007pass', 'icons/remove.jpg', 22, 'Female', '2024-06-07 17:30:00', 'diana@gmail.com'),
(5, 'eve321', 'evesecret321', 'icons/stop.png', 26, '', '2024-06-10 11:00:00', 'eve@gmail.com'),
(6, 'David_Sun', 'ja0126047', 'icon/non user.png', 18, 'Male', '2025-05-16 15:44:02', 'vortexbluster@gmail.com'),
(10, 'alice123', 'password123', 'icons/play.png', 25, 'Female', '2024-06-01 10:00:00', 'alice@gmail.com'),
(12, 'a a', '3333', 'icons/non user.png', NULL, '', NULL, 'a@gmail.com'),
(13, 'g g', '9999', 'icons/non user.png', NULL, '', NULL, 'b@gmail.com'),
(14, 'q ', '111', 'icons/non user.png', NULL, '', '2025-06-11 22:32:44', 'q@gmail.com'),
(15, 'test', '444', 'icons/non user.png', 30, '', '2025-06-11 22:50:53', 'tset@gmail.com'),
(16, 'sun', '1234567', 'icons/non user.png', 32, '', '2025-06-12 01:06:09', 'sun@gmail.com'),
(17, 'w', '2222', 'icons/non user.png', 20, 'Male', '2025-06-12 01:56:49', 'w@gmail.com'),
(18, 'ui ', '888', 'icons/non user.png', NULL, '', '2025-06-12 20:37:00', 'ui@gmail.com'),
(19, 'lol James', 'loljames123', 'icons/non user.png', NULL, '', '2025-06-28 16:06:20', 'loljames123@gmail.com'),
(26, 'test test', 'Test123', 'icons/non user.png', 18, 'Female', '2025-07-08 20:48:20', 'test@test.com'),
(29, 'Yu Lun Wu', 'Gary123', 'icons/non user.png', 21, 'Male', '2025-07-08 21:46:27', 'gary8321233@gmail.com');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `comment_dislike`
--
ALTER TABLE `comment_dislike`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `comment_like`
--
ALTER TABLE `comment_like`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `comment_page`
--
ALTER TABLE `comment_page`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `comment_user_id` (`comment_user_id`);

--
-- 資料表索引 `favorite_songs`
--
ALTER TABLE `favorite_songs`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `post_like`
--
ALTER TABLE `post_like`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `record_detail`
--
ALTER TABLE `record_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `record_session`
--
ALTER TABLE `record_session`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `session_id` (`session_id`);

--
-- 資料表索引 `share_page`
--
ALTER TABLE `share_page`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `songs`
--
ALTER TABLE `songs`
  ADD PRIMARY KEY (`song_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `user_account` (`user_account`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 在傾印的資料表使用自動增長(AUTO_INCREMENT)
--

--
-- 使用資料表自動增長(AUTO_INCREMENT) `comment_dislike`
--
ALTER TABLE `comment_dislike`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `comment_like`
--
ALTER TABLE `comment_like`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `comment_page`
--
ALTER TABLE `comment_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `favorite_songs`
--
ALTER TABLE `favorite_songs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `post_like`
--
ALTER TABLE `post_like`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `record_detail`
--
ALTER TABLE `record_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `record_session`
--
ALTER TABLE `record_session`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `share_page`
--
ALTER TABLE `share_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `songs`
--
ALTER TABLE `songs`
  MODIFY `song_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- 已傾印資料表的限制(constraint)
--

--
-- 資料表的限制(constraint) `comment_page`
--
ALTER TABLE `comment_page`
  ADD CONSTRAINT `comment_page_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `share_page` (`id`),
  ADD CONSTRAINT `comment_page_ibfk_2` FOREIGN KEY (`comment_user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制(constraint) `share_page`
--
ALTER TABLE `share_page`
  ADD CONSTRAINT `share_page_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
