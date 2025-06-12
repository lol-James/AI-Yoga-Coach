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

-- --------------------------------------------------------

--
-- 資料表結構 `favorite_songs`
--

CREATE TABLE `favorite_songs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `song_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `record_detail`
--

CREATE TABLE `record_detail` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `total_posture_count` int(11) DEFAULT NULL,
  `daily_max_app_opens` int(11) DEFAULT NULL,
  `max_daily_usage_hours` int(11) DEFAULT NULL,
  `min_daily_usage_hours` int(11) DEFAULT NULL,
  `max_posture_name` text COLLATE utf8_unicode_ci,
  `max_posture_count` int(11) DEFAULT NULL,
  `min_posture_name` text COLLATE utf8_unicode_ci,
  `min_posture_count` int(11) DEFAULT NULL,
  `longest_streak_days` int(11) DEFAULT NULL,
  `posture_id` int(11) DEFAULT NULL,
  `posture_name` text COLLATE utf8_unicode_ci,
  `total_completed` int(11) DEFAULT NULL,
  `max_accuracy` float DEFAULT NULL,
  `min_accuracy` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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

-- --------------------------------------------------------

--
-- 資料表結構 `songs`
--

CREATE TABLE `songs` (
  `song_id` int(11) NOT NULL,
  `song_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `song_path` varchar(255) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
  `gender` enum('male','female','other') COLLATE utf8_unicode_ci DEFAULT 'other',
  `register_date` datetime DEFAULT NULL,
  `email` varchar(100) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `user_account`, `user_password`, `user_picture`, `age`, `gender`, `register_date`, `email`) VALUES
(1, 'non', '00000000', 'icons/non user.png', NULL, 'other', NULL, 'deafult'),
(2, 'bob456', 'bobpass456', 'icons/pre.png', 30, 'male', '2024-06-03 14:20:00', 'bob@gmail.com'),
(3, 'charlie789', 'charlie789', 'icons/quit.png', 28, 'male', '2024-06-05 09:45:00', 'charlie@gmail.com'),
(4, 'diana007', 'diana007pass', 'icons/remove.jpg', 22, 'female', '2024-06-07 17:30:00', 'diana@gmail.com'),
(5, 'eve321', 'evesecret321', 'icons/stop.png', 26, 'other', '2024-06-10 11:00:00', 'eve@gmail.com'),
(6, 'David_Sun', 'ja0126047', 'icon/non user.png', 18, 'male', '2025-05-16 15:44:02', 'vortexbluster@gmail.com'),
(10, 'alice123', 'password123', 'icons/play.png', 25, 'female', '2024-06-01 10:00:00', 'alice@gmail.com'),
(12, 'a a', '3333', 'icons/non user.png', NULL, 'other', NULL, 'a@gmail.com'),
(13, 'g g', '9999', 'icons/non user.png', NULL, 'other', NULL, 'b@gmail.com'),
(14, 'q ', '111', 'icons/non user.png', NULL, 'other', '2025-06-11 22:32:44', 'q@gmail.com'),
(15, 'test', '444', 'icons/non user.png', 30, 'other', '2025-06-11 22:50:53', 'tset@gmail.com'),
(16, 'sun', '1234567', 'icons/non user.png', 32, 'other', '2025-06-12 01:06:09', 'sun@gmail.com'),
(17, 'w ', '2222', 'icons/non user.png', 20, 'other', '2025-06-12 01:56:49', 'w@gmail.com'),
(18, 'ui ', '888', 'icons/non user.png', NULL, 'other', '2025-06-12 20:37:00', 'ui@gmail.com');

--
-- 已傾印資料表的索引
--

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
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`song_id`),
  ADD KEY `song_id` (`song_id`);

--
-- 資料表索引 `record_detail`
--
ALTER TABLE `record_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `record_picture`
--
ALTER TABLE `record_picture`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

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
-- 使用資料表自動增長(AUTO_INCREMENT) `comment_page`
--
ALTER TABLE `comment_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `favorite_songs`
--
ALTER TABLE `favorite_songs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `record_detail`
--
ALTER TABLE `record_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `record_picture`
--
ALTER TABLE `record_picture`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `share_page`
--
ALTER TABLE `share_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `songs`
--
ALTER TABLE `songs`
  MODIFY `song_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動增長(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

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
-- 資料表的限制(constraint) `favorite_songs`
--
ALTER TABLE `favorite_songs`
  ADD CONSTRAINT `favorite_songs_ibfk_1` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `favorite_songs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- 資料表的限制(constraint) `record_detail`
--
ALTER TABLE `record_detail`
  ADD CONSTRAINT `record_detail_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制(constraint) `record_picture`
--
ALTER TABLE `record_picture`
  ADD CONSTRAINT `record_picture_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制(constraint) `share_page`
--
ALTER TABLE `share_page`
  ADD CONSTRAINT `share_page_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
