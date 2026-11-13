"""
================================================================================
CONFIG.PY - QUẢN LÝ CẤU HÌNH TẬP TRUNG TOÀN HỆ THỐNG (CENTRALIZED SETTINGS)
================================================================================
Tập trung toàn bộ hằng số, tham số đồ họa, cấu hình CSDL, máy chủ API và đường dẫn
tài nguyên của trò chơi theo chuẩn Kiến trúc Phần mềm Python.
"""

import os
from pathlib import Path

# --- ĐƯỜNG DẪN THƯ MỤC DỰ ÁN ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SCENES_DIR = PROJECT_ROOT / "scenes"
TASK1_DIR = PROJECT_ROOT / "task1"
TASK4_DIR = PROJECT_ROOT / "task4"

# Đảm bảo các thư mục dữ liệu tồn tại
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- THÔNG SỐ ĐỒ HỌA & MÀN HÌNH ---
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Hành Trình Lịch Sử Việt Nam - Game Giáo Dục Tương Tác"
TARGET_FPS = 60

# --- BẢNG MÀU CHỦ ĐẠO (HISTORICAL COLOR PALETTE) ---
COLOR_BG = (248, 244, 230)          # Nền giấy ngà cổ điển
COLOR_PRIMARY = (180, 35, 45)       # Đỏ son hào khí
COLOR_GOLD = (212, 160, 23)         # Vàng sao kim
COLOR_DARK = (45, 40, 35)           # Chữ đen than
COLOR_MUTED = (120, 115, 110)       # Xám tro ghi chú
COLOR_CARD_BG = (255, 255, 255)     # Trắng thẻ bài
COLOR_SUCCESS = (45, 125, 80)       # Xanh lá thành công
COLOR_PANEL_BG = (240, 234, 214)    # Nền bảng điều khiển
COLOR_BORDER = (215, 205, 180)      # Viền chỉ
COLOR_ACCENT = (50, 95, 150)        # Xanh dương thông tin

# --- CẤU HÌNH KẾT NỐI CƠ SỞ DỮ LIỆU MYSQL / MARIADB ---
DB_DEFAULT_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "game"),
    "charset": "utf8mb4",
    "connect_timeout": 3,
}

# --- CẤU HÌNH MÁY CHỦ REST API (TASK 1) ---
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}"

# --- CẤU HÌNH VÒNG CHƠI (GAME LOOP & GAMEPLAY) ---
TRANSITION_SPEED = 500.0  # Tốc độ mờ dần (alpha/giây)
DEFAULT_START_YEAR = 1911
MAX_TIMELINE_YEAR = 1975

