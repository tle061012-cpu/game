-- Run this once in phpMyAdmin after selecting the `game` database.
-- Stores collected clue IDs and quiz attempts per player and location.
CREATE TABLE IF NOT EXISTS `task4_quest_progress` (
  `ma_nguoi_dung` int(11) NOT NULL,
  `ma_dia_diem` int(11) NOT NULL,
  `clue_ids` longtext NOT NULL,
  `quiz_attempts` int(11) NOT NULL DEFAULT 0,
  `thoi_gian_cap_nhat` timestamp NOT NULL DEFAULT current_timestamp()
    ON UPDATE current_timestamp(),
  PRIMARY KEY (`ma_nguoi_dung`, `ma_dia_diem`),
  CONSTRAINT `fk_task4_progress_user`
    FOREIGN KEY (`ma_nguoi_dung`) REFERENCES `nguoi_dung` (`ma_nguoi_dung`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;