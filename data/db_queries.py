"""
================================================================================
PHẦN 1: TẦNG CÂU LỆNH SQL & TRUY VẤN CƠ SỞ DỮ LIỆU (DATA ACCESS LAYER)
================================================================================
File này chịu trách nhiệm:
1. Quản lý kết nối tới MySQL / MariaDB (XAMPP).
2. Định nghĩa toàn bộ câu lệnh SQL thuần (SELECT, INSERT, UPDATE).
3. Thực thi truy vấn trả về dữ liệu thô (raw dict) từ CSDL.
"""

import sys
import json

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cấu hình kết nối MySQL tập trung từ config.py
try:
    from config import DB_DEFAULT_CONFIG
    DB_CONFIGS = [
        DB_DEFAULT_CONFIG,
        {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "game_lich_su_vn",  # Tên database dự phòng
            "port": 3306,
            "charset": "utf8mb4"
        }
    ]
except ImportError:
    DB_CONFIGS = [
        {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "game",
            "port": 3306,
            "charset": "utf8mb4"
        },
        {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "game_lich_su_vn",
            "port": 3306,
            "charset": "utf8mb4"
        }
    ]

# ------------------------------------------------------------------------------
# 1. ĐỊNH NGHĨA CÁC CÂU LỆNH SQL THUẦN (PURE SQL QUERIES)
# ------------------------------------------------------------------------------
SQL_SELECT_ALL_DIA_DIEM = """
    SELECT ma_dia_diem, ten_dia_diem, toa_do_x, toa_do_y, khu_vuc, mo_ta, mo_khoa_mac_dinh
    FROM dia_diem
    ORDER BY ma_dia_diem ASC;
"""

SQL_SELECT_ALL_SU_KIEN = """
    SELECT ma_su_kien, ma_dia_diem, ten_su_kien, nam_dien_ra, ngay_thang_chi_tiet,
           thoi_ky, tom_tat_dien_bien, nguon_trich_dan
    FROM su_kien_lich_su
    ORDER BY ma_su_kien ASC;
"""

SQL_SELECT_ALL_NHAN_VAT = """
    SELECT ma_nhan_vat, ma_dia_diem, ten_nhan_vat, loai_nhan_vat, loi_thoai
    FROM nhan_vat
    ORDER BY ma_nhan_vat ASC;
"""

SQL_SELECT_ALL_MANH_MOI = """
    SELECT ma_manh_moi, ma_su_kien, ma_nhan_vat, tieu_de_manh_moi, loai_manh_moi,
           noi_dung_chi_tiet, thu_tu_timeline_dung
    FROM manh_moi
    ORDER BY ma_su_kien ASC, thu_tu_timeline_dung ASC;
"""

SQL_SELECT_ALL_CAU_HOI = """
    SELECT ma_cau_hoi, ma_su_kien, noi_dung_cau_hoi,
           dap_an_a, dap_an_b, dap_an_c, dap_an_d,
           dap_an_dung, giai_thich_chi_tiet
    FROM cau_hoi_on_tap
    ORDER BY ma_cau_hoi ASC;
"""

SQL_SELECT_ALL_NGUOI_DUNG = """
    SELECT ma_nguoi_dung, ten_dang_nhap, mat_khau_ma_hoa, ho_va_ten, vai_tro, ngay_tao
    FROM nguoi_dung;
"""

SQL_LOGIN_USER = """
    SELECT ma_nguoi_dung, ten_dang_nhap, mat_khau_ma_hoa, ho_va_ten, vai_tro
    FROM nguoi_dung
    WHERE ten_dang_nhap = %s;
"""

SQL_REGISTER_USER = """
    INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_ma_hoa, ho_va_ten, vai_tro)
    VALUES (%s, %s, %s, 'player');
"""

SQL_SELECT_TIEN_DO = """
    SELECT ma_tien_do, ma_nguoi_dung, ma_dia_diem_hien_tai, nam_mo_khoa_cao_nhat,
           diem_tri_thuc, danh_sach_dia_diem_da_mo, thoi_gian_cap_nhat, du_lieu_nhiem_vu
    FROM tien_do_choi
    WHERE ma_nguoi_dung = %s;
"""

SQL_UPSERT_TIEN_DO = """
    INSERT INTO tien_do_choi (ma_nguoi_dung, ma_dia_diem_hien_tai, nam_mo_khoa_cao_nhat, diem_tri_thuc, danh_sach_dia_diem_da_mo, du_lieu_nhiem_vu)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        ma_dia_diem_hien_tai = VALUES(ma_dia_diem_hien_tai),
        nam_mo_khoa_cao_nhat = VALUES(nam_mo_khoa_cao_nhat),
        diem_tri_thuc = VALUES(diem_tri_thuc),
        danh_sach_dia_diem_da_mo = VALUES(danh_sach_dia_diem_da_mo),
        du_lieu_nhiem_vu = COALESCE(VALUES(du_lieu_nhiem_vu), du_lieu_nhiem_vu);
"""


# ------------------------------------------------------------------------------
# 2. HÀM KẾT NỐI CƠ SỞ DỮ LIỆU
# ------------------------------------------------------------------------------
def get_db_connection():
    """Tạo kết nối tới CSDL MySQL trong XAMPP (thử cả DB 'game' và 'game_lich_su_vn')."""
    if pymysql is None:
        return None, "Chưa cài đặt thư viện pymysql (chạy: pip install pymysql)"

    last_error = None
    for config in DB_CONFIGS:
        try:
            conn = pymysql.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
                port=config["port"],
                charset=config["charset"],
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn, f"Kết nối MySQL thành công! (DB: {config['database']})"
        except Exception as e:
            last_error = str(e)
            continue

    return None, f"Không thể kết nối MySQL XAMPP: {last_error}"


# ------------------------------------------------------------------------------
# 3. CÁC HÀM TRUY VẤN TRẢ VỀ DỮ LIỆU THÔ (RAW DATA FETCHERS)
# ------------------------------------------------------------------------------
def execute_select_query(sql_query, params=None):
    """Hàm bổ trợ thực thi câu lệnh SELECT an toàn và tự động đóng kết nối."""
    conn, status = get_db_connection()
    if not conn:
        return None, status

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, params or ())
            rows = cursor.fetchall()
        return rows, status
    except Exception as e:
        return None, f"Lỗi thực thi SQL: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def fetch_raw_dia_diem():
    """Lấy toàn bộ dữ liệu từ bảng dia_diem."""
    return execute_select_query(SQL_SELECT_ALL_DIA_DIEM)


def fetch_raw_su_kien():
    """Lấy toàn bộ dữ liệu từ bảng su_kien_lich_su."""
    return execute_select_query(SQL_SELECT_ALL_SU_KIEN)


def fetch_raw_nhan_vat():
    """Lấy toàn bộ dữ liệu từ bảng nhan_vat."""
    return execute_select_query(SQL_SELECT_ALL_NHAN_VAT)


def fetch_raw_manh_moi():
    """Lấy toàn bộ dữ liệu từ bảng manh_moi."""
    return execute_select_query(SQL_SELECT_ALL_MANH_MOI)


def fetch_raw_cau_hoi():
    """Lấy toàn bộ dữ liệu từ bảng cau_hoi_on_tap."""
    return execute_select_query(SQL_SELECT_ALL_CAU_HOI)


def fetch_raw_nguoi_dung():
    """Lấy danh sách người dùng từ bảng nguoi_dung."""
    return execute_select_query(SQL_SELECT_ALL_NGUOI_DUNG)


def authenticate_user(ten_dang_nhap, mat_khau):
    """
    Xác thực đăng nhập người dùng từ MySQL.
    Trả về (user_dict, message) nếu thành công, hoặc (None, error_message).
    """
    conn, status = get_db_connection()
    if not conn:
        return None, status

    try:
        with conn.cursor() as cursor:
            cursor.execute(SQL_LOGIN_USER, (ten_dang_nhap,))
            user = cursor.fetchone()

        if not user:
            return None, "Tên đăng nhập không tồn tại!"

        # Kiểm tra mật khẩu (so sánh trực tiếp theo dữ liệu CSDL)
        if str(user.get("mat_khau_ma_hoa")) != str(mat_khau):
            return None, "Mật khẩu không chính xác!"

        return user, "Đăng nhập thành công!"
    except Exception as e:
        return None, f"Lỗi truy vấn đăng nhập: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def register_user(ten_dang_nhap, mat_khau, ho_va_ten):
    """
    Đăng ký tài khoản người chơi mới vào bảng nguoi_dung.
    Tự động khởi tạo tiến trình ban đầu trong bảng tien_do_choi.
    """
    conn, status = get_db_connection()
    if not conn:
        return None, status

    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem tên đăng nhập đã tồn tại chưa
            cursor.execute("SELECT ma_nguoi_dung FROM nguoi_dung WHERE ten_dang_nhap = %s;", (ten_dang_nhap,))
            existing = cursor.fetchone()
            if existing:
                return None, "Tên đăng nhập đã được sử dụng!"

            cursor.execute(SQL_REGISTER_USER, (ten_dang_nhap, mat_khau, ho_va_ten))
            new_user_id = cursor.lastrowid

            # Khởi tạo tiến trình mặc định
            cursor.execute(
                SQL_UPSERT_TIEN_DO,
                (new_user_id, 1, 1914, 0, "[]", None)
            )

        conn.commit()
        return {
            "ma_nguoi_dung": new_user_id,
            "ten_dang_nhap": ten_dang_nhap,
            "ho_va_ten": ho_va_ten,
            "vai_tro": "player"
        }, "Đăng ký tài khoản thành công!"
    except Exception as e:
        return None, f"Lỗi đăng ký tài khoản: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def fetch_user_progress(ma_nguoi_dung):
    """Lấy thông tin tiến độ chơi của người dùng từ bảng tien_do_choi."""
    conn, status = get_db_connection()
    if not conn:
        return None, status

    try:
        with conn.cursor() as cursor:
            cursor.execute(SQL_SELECT_TIEN_DO, (ma_nguoi_dung,))
            row = cursor.fetchone()
        return row, "Lấy tiến độ thành công!"
    except Exception as e:
        return None, f"Lỗi truy vấn tiến độ: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def save_user_progress(ma_nguoi_dung, ma_dia_diem, nam_mo_khoa, diem_tri_thuc, ds_dia_diem_json, du_lieu_nhiem_vu=None):
    """Lưu tiến độ chơi của người dùng vào bảng tien_do_choi."""
    conn, status = get_db_connection()
    if not conn:
        return False, status

    try:
        with conn.cursor() as cursor:
            # Đảm bảo cột du_lieu_nhiem_vu tồn tại trong tien_do_choi
            cursor.execute("""
                ALTER TABLE tien_do_choi 
                ADD COLUMN IF NOT EXISTS du_lieu_nhiem_vu TEXT DEFAULT NULL;
            """)
            cursor.execute(
                SQL_UPSERT_TIEN_DO,
                (ma_nguoi_dung, ma_dia_diem, nam_mo_khoa, diem_tri_thuc, ds_dia_diem_json, du_lieu_nhiem_vu)
            )
        conn.commit()
        return True, "Lưu tiến trình thành công vào MySQL!"
    except Exception as e:
        return False, f"Lỗi lưu tiến trình: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def fetch_task4_progress(ma_nguoi_dung):
    """Tải tiến trình Task 4 trực tiếp từ cột du_lieu_nhiem_vu của bảng tien_do_choi."""
    conn, status = get_db_connection()
    if not conn:
        return [], status
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung = %s",
                (ma_nguoi_dung,)
            )
            row = cursor.fetchone()
        if not row or not row.get("du_lieu_nhiem_vu"):
            return [], "Chưa có tiến trình Task 4 trong tien_do_choi"
        
        try:
            raw = json.loads(row["du_lieu_nhiem_vu"])
            if not isinstance(raw, dict):
                return [], "Dữ liệu nhiệm vụ không hợp lệ"
        except Exception:
            return [], "Lỗi giải mã JSON du_lieu_nhiem_vu"

        rows = []
        for loc_id_str, val in raw.items():
            try:
                lid = int(loc_id_str)
            except ValueError:
                continue
            rows.append({
                "ma_dia_diem": lid,
                "clue_ids": json.dumps(val.get("clue_ids", []), ensure_ascii=False),
                "quiz_attempts": val.get("quiz_attempts", 0)
            })
        return rows, "Thành công"
    except Exception as e:
        return [], f"Lỗi nạp tiến trình Task 4 từ tien_do_choi: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def save_task4_progress(ma_nguoi_dung, ma_dia_diem, clue_ids_json, quiz_attempts):
    """Lưu tiến trình Task 4 trực tiếp vào cột du_lieu_nhiem_vu của bảng tien_do_choi."""
    conn, status = get_db_connection()
    if not conn:
        return False, status
    try:
        with conn.cursor() as cursor:
            # Đảm bảo cột tồn tại
            cursor.execute("""
                ALTER TABLE tien_do_choi 
                ADD COLUMN IF NOT EXISTS du_lieu_nhiem_vu TEXT DEFAULT NULL;
            """)
            cursor.execute(
                "SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung = %s",
                (ma_nguoi_dung,)
            )
            row = cursor.fetchone()
            current_data = {}
            if row and row.get("du_lieu_nhiem_vu"):
                try:
                    current_data = json.loads(row["du_lieu_nhiem_vu"])
                    if not isinstance(current_data, dict):
                        current_data = {}
                except Exception:
                    current_data = {}

            try:
                c_ids = json.loads(clue_ids_json) if isinstance(clue_ids_json, str) else list(clue_ids_json)
            except Exception:
                c_ids = []

            current_data[str(ma_dia_diem)] = {
                "clue_ids": c_ids,
                "quiz_attempts": int(quiz_attempts)
            }
            updated_json = json.dumps(current_data, ensure_ascii=False)

            cursor.execute("""
                UPDATE tien_do_choi 
                SET du_lieu_nhiem_vu = %s 
                WHERE ma_nguoi_dung = %s
            """, (updated_json, ma_nguoi_dung))
        conn.commit()
        return True, "Đã lưu tiến trình Task 4 vào tien_do_choi."
    except Exception as e:
        return False, f"Lỗi lưu tiến trình Task 4 vào tien_do_choi: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ------------------------------------------------------------------------------
# 8. ĐỒNG BỘ VẬT PHẨM VÀO BẢNG TÚI ĐỒ NGƯỜI CHƠI (tui_do_nguoi_choi)
# ------------------------------------------------------------------------------
SQL_INSERT_TUI_DO = """
INSERT INTO tui_do_nguoi_choi (ma_nguoi_dung, ma_manh_moi)
SELECT %s, %s FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM tui_do_nguoi_choi WHERE ma_nguoi_dung = %s AND ma_manh_moi = %s
);
"""

def add_clue_to_inventory(ma_nguoi_dung, clue_id):
    """Lưu trữ manh mối đã nhặt vào bảng tui_do_nguoi_choi trong CSDL MySQL."""
    if not ma_nguoi_dung or not clue_id:
        return False

    try:
        numeric_id = int(clue_id)
    except (ValueError, TypeError):
        numeric_id = abs(hash(str(clue_id))) % 100000 + 1

    conn, _ = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(SQL_INSERT_TUI_DO, (ma_nguoi_dung, numeric_id, ma_nguoi_dung, numeric_id))
            conn.commit()
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass

