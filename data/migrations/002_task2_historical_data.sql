-- ========================================================
-- TASK 2: SCHEMA DỮ LIỆU LỊCH SỬ CÓ NGUỒN TRÍCH DẪN
-- Áp dụng cho MySQL / MariaDB (WAMP & XAMPP)
-- ========================================================

USE `game`;

SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------------------
-- 1. BẢNG MỐC THỜI GIAN LỊCH SỬ (MILESTONES)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `moc_lich_su` (
  `ma_moc` int(11) NOT NULL AUTO_INCREMENT,
  `nam` int(11) NOT NULL,
  `ngay_thang` varchar(50) DEFAULT NULL,
  `thoi_ky` varchar(100) NOT NULL,
  `y_nghia_giai_doan` text DEFAULT NULL,
  PRIMARY KEY (`ma_moc`),
  KEY `idx_nam` (`nam`),
  KEY `idx_thoi_ky` (`thoi_ky`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. BẢNG NGUỒN TÀI LIỆU TRÍCH DẪN (SOURCES & CITATIONS)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `nguon_lich_su` (
  `ma_nguon` int(11) NOT NULL AUTO_INCREMENT,
  `ten_tai_lieu` varchar(255) NOT NULL,
  `loai_nguon` varchar(50) DEFAULT 'Sách', -- Sách, Văn kiện, Hồi ký, Hồ sơ bảo tàng...
  `tac_gia_co_quan` varchar(255) DEFAULT NULL,
  `nha_xuat_ban` varchar(150) DEFAULT NULL,
  `nam_xuat_ban` int(11) DEFAULT NULL,
  `trich_dan_chi_tiet` text DEFAULT NULL,
  `muc_do_xac_thuc` varchar(50) DEFAULT 'Chính thống - Cấp Quốc gia',
  PRIMARY KEY (`ma_nguon`),
  KEY `idx_loai_nguon` (`loai_nguon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 3. BẢNG NHÂN VẬT LỊCH SỬ (HISTORICAL CHARACTERS)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `nhan_vat_lich_su` (
  `ma_nhan_vat` int(11) NOT NULL AUTO_INCREMENT,
  `ten_nhan_vat` varchar(150) NOT NULL,
  `nam_sinh_mat` varchar(50) DEFAULT NULL,
  `vai_tro` varchar(150) DEFAULT NULL,
  `tieu_su_dong_gop` text DEFAULT NULL,
  PRIMARY KEY (`ma_nhan_vat`),
  KEY `idx_ten_nhan_vat` (`ten_nhan_vat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 4. BỔ SUNG & MỞ RỘNG CỘT CHO BẢNG `su_kien_lich_su`
-- --------------------------------------------------------
-- Mở rộng độ dài trường ngày tháng và tên sự kiện để không bị cắt cụt
ALTER TABLE `su_kien_lich_su`
  MODIFY COLUMN `ngay_thang_chi_tiet` varchar(50) DEFAULT NULL,
  MODIFY COLUMN `ten_su_kien` varchar(255) NOT NULL,
  ADD COLUMN IF NOT EXISTS `ma_moc` int(11) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `ma_nguon` int(11) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `nhan_vat_chinh` varchar(255) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `y_nghia_lich_su` text DEFAULT NULL;

-- --------------------------------------------------------
-- 5. BẢNG LIÊN KẾT NHÂN VẬT - SỰ KIỆN (N-N)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `su_kien_nhan_vat` (
  `ma_su_kien` int(11) NOT NULL,
  `ma_nhan_vat` int(11) NOT NULL,
  `vai_tro_trong_su_kien` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`ma_su_kien`, `ma_nhan_vat`),
  CONSTRAINT `fk_sknv_sukien` FOREIGN KEY (`ma_su_kien`) REFERENCES `su_kien_lich_su` (`ma_su_kien`) ON DELETE CASCADE,
  CONSTRAINT `fk_sknv_nhanvat` FOREIGN KEY (`ma_nhan_vat`) REFERENCES `nhan_vat_lich_su` (`ma_nhan_vat`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
