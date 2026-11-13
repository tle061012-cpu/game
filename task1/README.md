# Task 1 — Cách Chơi, Khung Kiến Trúc & Triển Khai Pygbag (Architecture & Web Deployment)

Tài liệu hướng dẫn và đặc tả kỹ thuật cho **Task 1: Khung kiến trúc và Vòng chơi**.

---

## 1. Kiến trúc Khung Game (Architecture Overview)

Dự án áp dụng mô hình **Director & Scene Manager Pattern** trên nền tảng Pygame:
- **Director / Game Loop (`main.py`):**
  - Quản lý vòng đời trò chơi: `init` -> `handle_events` -> `update(dt)` -> `draw` -> `flip`.
  - Bộ điều hướng cảnh (Scene Switcher): `login` -> `map` -> `investigation` -> `task4_timeline` -> `task4_quiz` -> `review` (Task 5) -> `quit`.
  - Chuyển tiếp hiệu ứng mờ dần (Alpha Transition) mượt mà 60 FPS tính theo Delta Time ($dt$).
- **REST API Đồng bộ Đa chế độ (`task1/`):**
  - **FastAPI Chuẩn Doanh Nghiệp (`task1/fastapi_server.py`):** Chạy với Uvicorn, tự động sinh tài liệu Swagger UI tương tác tại `http://localhost:8000/docs`, Pydantic Schema kiểm tra kiểu dữ liệu tự động.
  - **Zero-Dependency Server (`task1/api_server.py`):** Sẵn sàng chạy ngay lập tức bằng thư viện chuẩn của Python mà không cần cài đặt thêm.
  - Cung cấp API lưu trữ tiến độ chơi, điểm tri thức và xếp hạng người chơi qua JSON/MySQL.

---

## 2. Hướng dẫn Khởi chạy Máy chủ REST API (FastAPI & Swagger UI)

### Cách 1: Khởi động FastAPI Server chuẩn (Khuyên dùng)
```powershell
python -m task1.fastapi_server
```
Sau đó mở trình duyệt tại:
- **Swagger UI (Test trực tiếp trên Web):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Cách 2: Khởi động Server tích hợp sẵn (Zero-Dependency)
```powershell
python -m task1.api_server
```

### Kiểm thử tự động nhanh các Endpoint:
```powershell
python -m task1.demo_api
```

---

## 3. Hướng dẫn Triển khai Web bằng Pygbag (Web Deployment)

Để chạy Game trực tiếp trên trình duyệt web (WebGL / WebAssembly HTML5):

### Bước 1: Cài đặt pygbag (khi có kết nối mạng)
```powershell
pip install pygbag
```

### Bước 2: Chạy thử nghiệm máy chủ web cục bộ
Tại thư mục dự án:
```powershell
pygbag --ume_block 0 main.py
```
Sau đó mở trình duyệt tại địa chỉ `http://localhost:8000` để chơi game trực tiếp trên Web!

### Bước 3: Đóng gói xuất bản lên GitHub Pages / Itch.io
```powershell
pygbag --build main.py
```
Thư mục `build/web` sinh ra sẽ chứa toàn bộ file HTML, WebAssembly, Canvas để người dùng tải lên bất kỳ host web tĩnh nào.
