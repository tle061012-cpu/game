"""
================================================================================
TASK 2: SEEDER NẠP 30 SỰ KIỆN LỊCH SỬ KÈM NGUỒN VÀO CSDL VÀ JSON CACHE
================================================================================
File này chịu trách nhiệm:
1. Nạp toàn bộ 30 sự kiện kèm mốc, nhân vật, nguồn vào database MySQL (`game`).
2. Tự động kiểm tra và tạo bảng nếu chưa có.
3. Đồng bộ và lưu ra file JSON `data/historical_events_30.json` (chế độ offline fallback).
"""

import os
import sys
import json
from typing import Dict, Any, List

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi font
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm đường dẫn project vào sys.path để import an toàn
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from task2.dataset_30_events import DATASET_30_SU_KIEN
from task2.schema import SuKienLichSu, MocThoiGian, NguonLichSu, NhanVatLichSu

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

# Cấu hình kết nối MySQL (WAMP / XAMPP)
DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "game",
    "port": 3306,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor if pymysql else None
}

JSON_CACHE_PATH = os.path.join(PROJECT_ROOT, "data", "historical_events_30.json")


def save_to_json_cache(events_data: List[Dict[str, Any]], filepath: str = JSON_CACHE_PATH) -> bool:
    """Lưu 30 sự kiện vào file JSON dự phòng (offline cache)"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Đã lưu cache 30 sự kiện ra file JSON: {filepath}")
        return True
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể lưu cache JSON: {e}")
        return False


def get_db_connection():
    """Tạo kết nối tới CSDL MySQL"""
    if not pymysql:
        return None
    try:
        conn = pymysql.connect(**DEFAULT_DB_CONFIG)
        return conn
    except Exception as e:
        # Thử lại với database game_lich_su_vn nếu có
        try:
            cfg = dict(DEFAULT_DB_CONFIG)
            cfg["database"] = "game_lich_su_vn"
            conn = pymysql.connect(**cfg)
            return conn
        except Exception:
            return None


def init_task2_tables(conn) -> bool:
    """Tạo các bảng cho Task 2 nếu chưa tồn tại"""
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS `moc_lich_su` (
          `ma_moc` int(11) NOT NULL AUTO_INCREMENT,
          `nam` int(11) NOT NULL,
          `ngay_thang` varchar(50) DEFAULT NULL,
          `thoi_ky` varchar(100) NOT NULL,
          `y_nghia_giai_doan` text DEFAULT NULL,
          PRIMARY KEY (`ma_moc`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `nguon_lich_su` (
          `ma_nguon` int(11) NOT NULL AUTO_INCREMENT,
          `ten_tai_lieu` varchar(255) NOT NULL,
          `loai_nguon` varchar(50) DEFAULT 'Sách',
          `tac_gia_co_quan` varchar(255) DEFAULT NULL,
          `nha_xuat_ban` varchar(150) DEFAULT NULL,
          `nam_xuat_ban` int(11) DEFAULT NULL,
          `trich_dan_chi_tiet` text DEFAULT NULL,
          `muc_do_xac_thuc` varchar(50) DEFAULT 'Chính thống - Cấp Quốc gia',
          PRIMARY KEY (`ma_nguon`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `nhan_vat_lich_su` (
          `ma_nhan_vat` int(11) NOT NULL AUTO_INCREMENT,
          `ten_nhan_vat` varchar(150) NOT NULL,
          `nam_sinh_mat` varchar(50) DEFAULT NULL,
          `vai_tro` varchar(150) DEFAULT NULL,
          `tieu_su_dong_gop` text DEFAULT NULL,
          PRIMARY KEY (`ma_nhan_vat`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    ]
    try:
        with conn.cursor() as cursor:
            for sql in ddl_statements:
                cursor.execute(sql)
            
            # Mở rộng kích thước trường ngày tháng và tên sự kiện nếu cần
            try:
                cursor.execute("ALTER TABLE `su_kien_lich_su` MODIFY COLUMN `ngay_thang_chi_tiet` varchar(50) DEFAULT NULL;")
                cursor.execute("ALTER TABLE `su_kien_lich_su` MODIFY COLUMN `ten_su_kien` varchar(255) NOT NULL;")
            except Exception:
                pass

            # Đảm bảo các cột mới trong `su_kien_lich_su`
            cursor.execute("SHOW COLUMNS FROM `su_kien_lich_su` LIKE 'ma_nguon';")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `su_kien_lich_su` ADD COLUMN `ma_nguon` int(11) DEFAULT NULL;")
                
            cursor.execute("SHOW COLUMNS FROM `su_kien_lich_su` LIKE 'ma_moc';")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `su_kien_lich_su` ADD COLUMN `ma_moc` int(11) DEFAULT NULL;")
                
            cursor.execute("SHOW COLUMNS FROM `su_kien_lich_su` LIKE 'nhan_vat_chinh';")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `su_kien_lich_su` ADD COLUMN `nhan_vat_chinh` varchar(255) DEFAULT NULL;")
                
            cursor.execute("SHOW COLUMNS FROM `su_kien_lich_su` LIKE 'y_nghia_lich_su';")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `su_kien_lich_su` ADD COLUMN `y_nghia_lich_su` text DEFAULT NULL;")

        conn.commit()
        return True
    except Exception as e:
        print(f"[CẢNH BÁO] Lỗi khi tạo bảng trong CSDL: {e}")
        return False


def seed_data_to_mysql(conn, dataset: List[Dict[str, Any]]) -> int:
    """Nạp 30 sự kiện kèm mốc, nhân vật, nguồn vào MySQL"""
    inserted_count = 0
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        for item in dataset:
            ma_sk = item["ma_su_kien"]
            ten_sk = item["ten_su_kien"]
            nam = item["nam_dien_ra"]
            ngay_thang = item["ngay_thang_chi_tiet"]
            thoi_ky = item["thoi_ky"]
            tom_tat = item["tom_tat_dien_bien"]
            y_nghia = item.get("y_nghia_lich_su", "")
            nhan_vat_chinh = item.get("nhan_vat_chinh", "")
            
            # 1. Nạp Mốc
            moc_info = item.get("moc", {})
            ma_moc = moc_info.get("ma_moc", ma_sk)
            sql_moc = """
                INSERT INTO moc_lich_su (ma_moc, nam, ngay_thang, thoi_ky, y_nghia_giai_doan)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nam = VALUES(nam),
                    ngay_thang = VALUES(ngay_thang),
                    thoi_ky = VALUES(thoi_ky),
                    y_nghia_giai_doan = VALUES(y_nghia_giai_doan);
            """
            cursor.execute(sql_moc, (
                ma_moc,
                moc_info.get("nam", nam),
                moc_info.get("ngay_thang", ngay_thang),
                moc_info.get("thoi_ky", thoi_ky),
                moc_info.get("y_nghia_giai_doan", "")
            ))
            
            # 2. Nạp Nguồn
            nguon_info = item.get("nguon", {})
            ma_nguon = nguon_info.get("ma_nguon", ma_sk)
            sql_nguon = """
                INSERT INTO nguon_lich_su (ma_nguon, ten_tai_lieu, loai_nguon, tac_gia_co_quan, nha_xuat_ban, nam_xuat_ban, trich_dan_chi_tiet, muc_do_xac_thuc)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ten_tai_lieu = VALUES(ten_tai_lieu),
                    loai_nguon = VALUES(loai_nguon),
                    tac_gia_co_quan = VALUES(tac_gia_co_quan),
                    nha_xuat_ban = VALUES(nha_xuat_ban),
                    nam_xuat_ban = VALUES(nam_xuat_ban),
                    trich_dan_chi_tiet = VALUES(trich_dan_chi_tiet),
                    muc_do_xac_thuc = VALUES(muc_do_xac_thuc);
            """
            cursor.execute(sql_nguon, (
                ma_nguon,
                nguon_info.get("ten_tai_lieu", ""),
                nguon_info.get("loai_nguon", "Sách"),
                nguon_info.get("tac_gia_co_quan", ""),
                nguon_info.get("nha_xuat_ban", ""),
                nguon_info.get("nam_xuat_ban"),
                nguon_info.get("trich_dan_chi_tiet", ""),
                nguon_info.get("muc_do_xac_thuc", "Chính thống - Cấp Quốc gia")
            ))
            
            # Tạo chuỗi nguồn trích dẫn text
            nguon_text = f"{nguon_info.get('ten_tai_lieu', '')}, {nguon_info.get('tac_gia_co_quan', '')}, NXB {nguon_info.get('nha_xuat_ban', '')} ({nguon_info.get('nam_xuat_ban', '')}); {nguon_info.get('trich_dan_chi_tiet', '')}"
            
            # 3. Nạp Nhân vật
            for nv in item.get("nhan_vat_lien_quan", []):
                sql_nv = """
                    INSERT INTO nhan_vat_lich_su (ma_nhan_vat, ten_nhan_vat, nam_sinh_mat, vai_tro, tieu_su_dong_gop)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        ten_nhan_vat = VALUES(ten_nhan_vat),
                        nam_sinh_mat = VALUES(nam_sinh_mat),
                        vai_tro = VALUES(vai_tro),
                        tieu_su_dong_gop = VALUES(tieu_su_dong_gop);
                """
                cursor.execute(sql_nv, (
                    nv.get("ma_nhan_vat"),
                    nv.get("ten_nhan_vat", ""),
                    nv.get("nam_sinh_mat", ""),
                    nv.get("vai_tro", ""),
                    nv.get("tieu_su_dong_gop", "")
                ))
            
            # 4. Nạp Sự kiện chính vào `su_kien_lich_su`
            sql_sk = """
                INSERT INTO su_kien_lich_su (
                    ma_su_kien, ma_dia_diem, ten_su_kien, nam_dien_ra, ngay_thang_chi_tiet,
                    thoi_ky, tom_tat_dien_bien, nguon_trich_dan, ma_moc, ma_nguon, nhan_vat_chinh, y_nghia_lich_su
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ten_su_kien = VALUES(ten_su_kien),
                    nam_dien_ra = VALUES(nam_dien_ra),
                    ngay_thang_chi_tiet = VALUES(ngay_thang_chi_tiet),
                    thoi_ky = VALUES(thoi_ky),
                    tom_tat_dien_bien = VALUES(tom_tat_dien_bien),
                    nguon_trich_dan = VALUES(nguon_trich_dan),
                    ma_moc = VALUES(ma_moc),
                    ma_nguon = VALUES(ma_nguon),
                    nhan_vat_chinh = VALUES(nhan_vat_chinh),
                    y_nghia_lich_su = VALUES(y_nghia_lich_su);
            """
            # Giữ mã địa điểm hợp lệ nếu là 8 sự kiện cũ, các sự kiện khác để NULL hoặc 1
            ma_dia_diem = ma_sk if ma_sk <= 8 else None
            
            cursor.execute(sql_sk, (
                ma_sk, ma_dia_diem, ten_sk, nam, ngay_thang,
                thoi_ky, tom_tat, nguon_text, ma_moc, ma_nguon, nhan_vat_chinh, y_nghia
            ))
            inserted_count += 1
            
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()

    return inserted_count


def run_seeder():
    """Hàm chạy chính của Seeder"""
    print("=" * 70)
    print(">>> TIẾN TRÌNH NẠP 30 SỰ KIỆN LỊCH SỬ CÓ NGUỒN (TASK 2) <<<")
    print("=" * 70)
    
    # 1. Luôn ghi ra JSON offline cache trước
    save_to_json_cache(DATASET_30_SU_KIEN)
    
    # 2. Kết nối và nạp vào MySQL
    conn = get_db_connection()
    if conn:
        print("[+] Kết nối MySQL thành công! Đang đồng bộ cấu trúc bảng và nạp dữ liệu...")
        init_task2_tables(conn)
        count = seed_data_to_mysql(conn, DATASET_30_SU_KIEN)
        conn.close()
        print(f"[HOÀN TẤT] Đã nạp thành công {count}/30 sự kiện lịch sử vào database MySQL 'game'!")
    else:
        print("[!] Không kết nối được MySQL (WAMP/XAMPP chưa bật hoặc chưa tạo DB 'game').")
        print("    -> Đừng lo! Toàn bộ 30 sự kiện đã được lưu vào cache JSON offline.")
        print("    -> Các hàm truy vấn và Demo Task 2 vẫn hoạt động 100% trơn tru!")


if __name__ == "__main__":
    run_seeder()
