"""
================================================================================
SERVICES/LOGGER.PY - DỊCH VỤ GHI NHẬT KÝ CHUẨN HOÁ (STRUCTURED LOGGING)
================================================================================
Thay thế toàn bộ print() tự do bằng hệ thống logging chuẩn của Python.
Hỗ trợ hiển thị phân cấp: INFO, WARNING, ERROR, DEBUG và ghi file log data/game.log.
"""

import logging
import os
import sys
from pathlib import Path

# Thư mục chứa log
LOG_DIR = Path(__file__).resolve().parent.parent / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "game.log"

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | [%(name)s]: %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def setup_logger(name: str = "GameLichSu", level: int = logging.INFO) -> logging.Logger:
    """Khởi tạo và cấu hình một logger chuẩn cho module."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # 1. Console Handler (Đảm bảo in UTF-8 không lỗi font tiếng Việt trên Windows)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler (Lưu trữ nhật ký chạy game vào data/game.log)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

    logger.propagate = False
    return logger


def get_logger(name: str = "Game") -> logging.Logger:
    """Hàm tiện ích lấy logger nhanh cho bất kỳ file nào."""
    return logging.getLogger(name)

