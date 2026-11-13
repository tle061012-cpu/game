import pymysql
import sys

# Đảm bảo in tiếng Việt trên Terminal Windows không bị lỗi font
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cấu hình kết nối MySQL từ XAMPP
DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # Mặc định XAMPP là root
    "password": "",          # Mặc định XAMPP để trống
    "database": "game",      # Tên database thực tế trong phpMyAdmin
    "port": 3306,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor  # Trả về kết quả dạng từ điển (dict)
}

def get_connection():
    """Tạo và trả về một kết nối đến CSDL"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Lỗi kết nối CSDL: {e}")
        return None

# ==================== CÁC HÀM TRUY VẤN MẪU CHO GAME ====================

def lay_danh_sach_dia_diem():
    """Lấy danh sách địa điểm để hiển thị lên bản đồ (Task của Trúc)"""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM dia_diem")
            ket_qua = cursor.fetchall()
        conn.close()
        return ket_qua
    return []

def dang_nhap(ten_dang_nhap, mat_khau):
    """Kiểm tra đăng nhập người dùng (Task của Trà)"""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            sql = "SELECT ma_nguoi_dung, ho_va_ten, vai_tro FROM nguoi_dung WHERE ten_dang_nhap = %s AND mat_khau_ma_hoa = %s"
            cursor.execute(sql, (ten_dang_nhap, mat_khau))
            user = cursor.fetchone()
        conn.close()
        return user
    return None

def lay_manh_moi_theo_su_kien(ma_su_kien):
    """Lấy các mảnh ghép tư liệu của 1 sự kiện (Task của Thắng)"""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM manh_moi WHERE ma_su_kien = %s ORDER BY thu_tu_timeline_dung"
            cursor.execute(sql, (ma_su_kien,))
            danh_sach = cursor.fetchall()
        conn.close()
        return danh_sach
    return []

# Chạy thử kiểm tra kết nối ngay trên PyCharm:
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print(">> KẾT NỐI DATABASE TRÊN PYCHARM THÀNH CÔNG RỰC RỠ!")
        dia_diem = lay_danh_sach_dia_diem()
        print(f">> Số địa danh tìm thấy trong CSDL: {len(dia_diem)}")
        for d in dia_diem:
            print(f"   - [{d['ma_dia_diem']}] {d['ten_dia_diem']} ({d['khu_vuc']})")
        conn.close()
    else:
        print(">> KẾT NỐI THẤT BẠI. Hãy kiểm tra xem XAMPP (MySQL) đã bấm Start chưa!")
