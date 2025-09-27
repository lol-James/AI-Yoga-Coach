-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-09-05 13:16:27
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `comment_text` text NOT NULL,
  `comment_like` int(11) DEFAULT 0,
  `comment_dislike` int(11) DEFAULT 0
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `mode` int(11) NOT NULL, -- 0=Practice, 1=Easy, 2=Hard
  `total_posture_count` int(11) DEFAULT 0,
  `daily_max_app_opens` int(11) DEFAULT 0,
  `max_daily_usage_hours` float DEFAULT 0,
  `min_daily_usage_hours` float DEFAULT 0,
  `longest_streak_days` int(11) DEFAULT 0,
  `total_usage_hours` float DEFAULT 0,         
  `posture_id` int(11) DEFAULT NULL,
  `posture_name` text DEFAULT NULL,
  `total_completed` int(11) DEFAULT 0,
  `max_accuracy` float DEFAULT NULL,
  `min_accuracy` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `record_session`
--

CREATE TABLE `record_session` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `session_id` VARCHAR(64) NOT NULL,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME DEFAULT NULL,
  `mode` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `session_id` (`session_id`)
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
  `session_id` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `share_page`
--

CREATE TABLE `share_page` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `share_date` date NOT NULL,
  `share_text` text DEFAULT NULL,
  `share_content` varchar(255) DEFAULT NULL,
  `share_like` int(11) DEFAULT 0
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
(35, 17, '2025-09-05', 'wdawdawd', NULL, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `songs`
--

CREATE TABLE `songs` (
  `song_id` int(11) NOT NULL,
  `song_name` varchar(255) NOT NULL,
  `song_path` varchar(255) NOT NULL
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
  `user_account` varchar(50) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_picture` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` enum('Male','Female','Non binary','Prefer not to say') DEFAULT NULL,
  `register_date` datetime DEFAULT NULL,
  `email` varchar(100) NOT NULL
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
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `comment_dislike`
--
ALTER TABLE `comment_dislike`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `comment_like`
--
ALTER TABLE `comment_like`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `comment_page`
--
ALTER TABLE `comment_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `favorite_songs`
--
ALTER TABLE `favorite_songs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `post_like`
--
ALTER TABLE `post_like`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `record_detail`
--
ALTER TABLE `record_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `record_picture`
--
ALTER TABLE `record_picture`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `share_page`
--
ALTER TABLE `share_page`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `songs`
--
ALTER TABLE `songs`
  MODIFY `song_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `comment_page`
--
ALTER TABLE `comment_page`
  ADD CONSTRAINT `comment_page_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `share_page` (`id`),
  ADD CONSTRAINT `comment_page_ibfk_2` FOREIGN KEY (`comment_user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制式 `record_detail`
--
ALTER TABLE `record_detail`
  ADD CONSTRAINT `record_detail_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制式 `record_picture`
--
ALTER TABLE `record_picture`
  ADD CONSTRAINT `record_picture_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制式 `share_page`
--
ALTER TABLE `share_page`
  ADD CONSTRAINT `share_page_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
