# Task 2 — Dữ liệu Lịch sử có Nguồn (Historical Data with Validated Sources)

Tài liệu hướng dẫn và đặc tả kỹ thuật cho **Task 2**: Xây dựng mô hình dữ liệu (Schema), nạp 30 sự kiện lịch sử Việt Nam chuẩn mực kèm nguồn tài liệu chính thống và bộ công cụ Demo tra cứu.

---

## 1. Kiến trúc Mô hình Dữ liệu (Schema)

Task 2 mô hình hóa 4 thực thể cốt lõi trong nghiên cứu lịch sử:

```
[Mốc Thời Gian] (MocThoiGian)
      ▲
      │ 1-N (Một mốc có nhiều sự kiện)
      │
[Sự Kiện Lịch Sử] (SuKienLichSu) ◄──── N-N ────► [Nhân Vật Lịch Sử] (NhanVatLichSu)
      │
      ▼ 1-N (Một sự kiện có thể có nhiều nguồn kiểm chứng)
[Nguồn Trích Dẫn] (NguonLichSu)
```

### Các bảng CSDL (MySQL / MariaDB):
1. **`moc_lich_su`**: Quản lý mốc năm, ngày tháng, thời kỳ lịch sử (`1858-1918`, `1919-1930`, `1930-1945`, `1945-1954`, `1954-1975`), ý nghĩa giai đoạn.
2. **`nguon_lich_su`**: Quản lý nguồn tài liệu học thuật (Tên tài liệu, Loại nguồn: *Sách giáo khoa, Văn kiện Đảng, Hồi ký, Báo chí*, Tác giả / Cơ quan ban hành, Nhà xuất bản, Năm xuất bản, Trích dẫn số trang/chương, Mức độ xác thực: *Chính thống - Cấp Quốc gia*).
3. **`nhan_vat_lich_su`**: Quản lý các nhân vật tiêu biểu (Tên nhân vật, Năm sinh - năm mất, Vai trò, Tiểu sử và công lao cách mạng).
4. **`su_kien_lich_su`**: Bảng sự kiện nòng cốt, chứa tên sự kiện, mốc thời gian, tóm tắt diễn biến, ý nghĩa lịch sử, cùng các khóa ngoại liên kết tới `moc_lich_su`, `nguon_lich_su` và `dia_diem`.
5. **`su_kien_nhan_vat`**: Bảng trung gian liên kết quan hệ nhiều - nhiều (N-N) giữa nhân vật và sự kiện.

---

## 2. Danh mục 30 Sự kiện Lịch sử Tiêu biểu

30 sự kiện được tuyển chọn và đối chiếu nghiêm ngặt theo các tài liệu chính thống:
- *Đại cương Lịch sử Việt Nam* (NXB Giáo dục)
- *Lịch sử Việt Nam* (Viện Sử học, NXB Khoa học Xã hội)
- *Văn kiện Đảng Toàn tập* (NXB Chính trị Quốc gia Sự thật)
- *Hồ Chí Minh Toàn tập / Biên niên tiểu sử* (NXB Chính trị Quốc gia Sự thật)
- *Lịch sử Quân đội Nhân dân Việt Nam* (Viện Lịch sử Quân sự)
- *Hồi ký Điện Biên Phủ - Điểm hẹn lịch sử* (Đại tướng Võ Nguyên Giáp)
- *Sách giáo khoa Lịch sử 11, 12* (Bộ GD&ĐT)

| STT | Năm | Sự kiện lịch sử | Nhân vật tiêu biểu | Nguồn trích dẫn chính |
| :---: | :---: | :--- | :--- | :--- |
| **1** | 1858 | Pháp tấn công bán đảo Sơn Trà (Đà Nẵng) | Nguyễn Tri Phương | Đại cương Lịch sử VN, NXB Giáo dục |
| **2** | 1862 | Triều đình ký Hiệp ước Nhâm Tuất | Phan Thanh Giản | Lịch sử Việt Nam, T.6, Viện Sử học |
| **3** | 1864 | Khởi nghĩa Trương Định tại Gò Công | Trương Định | SGK Lịch sử 11, Bộ GD&ĐT |
| **4** | 1884 | Ký Hiệp ước Patenôtre (Giáp Thân) | Nguyễn Văn Tường | Lịch sử bang giao VN cận đại |
| **5** | 1885 | Vua Hàm Nghi hạ chiếu Cần Vương | Hàm Nghi, Tôn Thất Thuyết | Phong trào Cần Vương, NXB Thuận Hóa |
| **6** | 1887 | Khởi nghĩa nông dân Yên Thế | Hoàng Hoa Thám (Đề Thám) | Khởi nghĩa Yên Thế, NXB CTQG |
| **7** | 1904 | Sáng lập Hội Duy Tân & Phong trào Đông Du | Phan Bội Châu, Cường Để | Phan Bội Châu Toàn tập, T.3 |
| **8** | 1907 | Phong trào Đông Kinh Nghĩa Thục tại Hà Nội | Lương Văn Can, Nguyễn Quyền | Phong trào Đông Kinh Nghĩa Thục |
| **9** | 1911 | Nguyễn Tất Thành rời Bến Nhà Rồng | Nguyễn Tất Thành (Văn Ba) | HCM Biên niên tiểu sử, T.1, NXB CTQG |
| **10** | 1919 | Bản Yêu sách của nhân dân An Nam (Versailles) | Nguyễn Ái Quốc | Hồ Chí Minh Toàn tập, T.1, NXB CTQG |
| **11** | 1920 | Bỏ phiếu Quốc tế Ba & sáng lập ĐCS Pháp | Nguyễn Ái Quốc | Hồ Chí Minh: Tiểu sử, Ban Tuyên giáo TW |
| **12** | 1925 | Thành lập Hội VN Cách mạng Thanh niên | Nguyễn Ái Quốc | Lịch sử ĐCSVN, T.1, NXB CTQG |
| **13** | 1927 | Xuất bản tác phẩm "Đường Kách mệnh" | Nguyễn Ái Quốc | Hồ Chí Minh Toàn tập, T.2, NXB CTQG |
| **14** | 1930 | Hội nghị thành lập Đảng Cộng sản Việt Nam | Nguyễn Ái Quốc, Trịnh Đình Cửu | Văn kiện Đảng toàn tập, T.2 |
| **15** | 1930 | Khởi nghĩa Yên Bái của VN Quốc dân Đảng | Nguyễn Thái Học, Phó Đức Chính | SGK Lịch sử 12, Bộ GD&ĐT |
| **16** | 1930 | Đỉnh cao phong trào Xô viết Nghệ - Tĩnh | Lê Mao, Nguyễn Phong Sắc | Lịch sử giai cấp công nhân VN |
| **17** | 1930 | Hội nghị TW 1 thông qua Luận cương chính trị | Trần Phú | Văn kiện Đảng toàn tập, T.2 |
| **18** | 1936 | Phong trào Dân chủ 1936 - 1939 | Lê Hồng Phong, Nguyễn Văn Cừ | Lịch sử ĐCSVN, T.1, NXB CTQG |
| **19** | 1940 | Khởi nghĩa Bắc Sơn & Khởi nghĩa Nam Kỳ | Chu Văn Tấn, Nguyễn Thị Minh Khai | Lịch sử Nam Bộ kháng chiến, T.1 |
| **20** | 1941 | Nguyễn Ái Quốc về nước tại hang Pác Bó | Hồ Chí Minh | Bác Hồ ở Pác Bó, NXB Kim Đồng |
| **21** | 1941 | Hội nghị Trung ương 8 lập Mặt trận Việt Minh | Hồ Chí Minh, Trường Chinh | Văn kiện Đảng toàn tập, T.7 |
| **22** | 1944 | Thành lập Đội VN Tuyên truyền Giải phóng quân | Võ Nguyên Giáp, Hoàng Sâm | Lịch sử QĐND Việt Nam, T.1 |
| **23** | 1945 | Quốc dân Đại hội Tân Trào phát lệnh Khởi nghĩa | Hồ Chí Minh, Võ Nguyên Giáp | Cách mạng Tháng Tám 1945, NXB QĐND |
| **24** | 1945 | Khởi nghĩa giành chính quyền ở Hà Nội | Nguyễn Khang | Lịch sử Thủ đô Hà Nội, NXB Sử học |
| **25** | 1945 | Chủ tịch HCM đọc Tuyên ngôn Độc lập | Hồ Chí Minh | Tuyên ngôn Độc lập 1945, NXB CTQG |
| **26** | 1946 | Lời kêu gọi Toàn quốc kháng chiến | Hồ Chí Minh | Hồ Chí Minh Toàn tập, T.4 |
| **27** | 1947 | Chiến dịch phản công Việt Bắc Thu - Đông 1947 | Võ Nguyên Giáp | Lịch sử kháng chiến chống Pháp, T.1 |
| **28** | 1950 | Chiến dịch Biên Giới Thu - Đông 1950 | Hồ Chí Minh, Võ Nguyên Giáp | Chiến dịch Biên giới Thu Đông 1950 |
| **29** | 1954 | Chiến thắng lịch sử Điện Biên Phủ | Võ Nguyên Giáp, De Castries | Điểm hẹn lịch sử, Đại tướng Võ Nguyên Giáp |
| **30** | 1975 | Chiến dịch Hồ Chí Minh, giải phóng miền Nam | Văn Tiến Dũng, Bùi Quang Thận | Tổng hành dinh trong Mùa Xuân toàn thắng |

---

## 3. Cấu trúc Module Code của Task 2

```
task2/
├── __init__.py               # Package export
├── schema.py                 # Định nghĩa Dataclasses: MocThoiGian, NguonLichSu, NhanVatLichSu, SuKienLichSu
├── dataset_30_events.py      # Bộ dữ liệu 30 sự kiện đầy đủ nguồn học thuật
├── seeder.py                 # Script nạp tự động vào MySQL và JSON Cache
├── event_service.py          # Service nghiệp vụ tìm kiếm, lọc, lấy trích dẫn
├── demo_events.py            # Demo CLI menu và Giao diện đồ họa Pygame
└── README.md                 # Tài liệu hướng dẫn Task 2
```

Ngoài ra:
- `data/migrations/002_task2_historical_data.sql`: File SQL DDL schema & nạp dữ liệu độc lập cho phpMyAdmin trên WAMP/XAMPP.
- `data/historical_events_30.json`: Tệp lưu trữ dữ liệu offline (bảo đảm hệ thống hoạt động 100% kể cả khi chưa bật MySQL).

---

## 4. Hướng dẫn Chạy Thử và Demo

Mở Terminal / PowerShell tại thư mục gốc của dự án (`d:\PythonProject\PythonProject16\PythonProject16\PythonProject16`):

### Bước 1: Kích hoạt môi trường ảo (Virtualenv)
```powershell
& "..\..\.venv\Scripts\Activate.ps1"
```

### Bước 2: Nạp dữ liệu vào CSDL (Seeder)
```powershell
python -m task2.seeder
```
*Kết quả:* Hệ thống sẽ tự động cập nhật bảng trong MySQL (WAMP/XAMPP) và tạo file cache `data/historical_events_30.json`.

### Bước 3: Chạy Demo

#### Cách 1: Chạy Menu CLI Console (Tra cứu dòng thời gian, tìm kiếm, xem chi tiết nguồn)
```powershell
python -m task2.demo_events
```
- Phím `1`: Xem danh sách 30 sự kiện theo bảng thời gian.
- Phím `2`: Nhập số thứ tự (ví dụ `29`) để xem chi tiết thẻ sự kiện **Chiến thắng Điện Biên Phủ** kèm trích dẫn sách Hồi ký Đại tướng Võ Nguyên Giáp.
- Phím `3`: Tìm kiếm sự kiện theo từ khóa (ví dụ: `Hồ Chí Minh`, `Tân Trào`, `1945`, `Điện Biên Phủ`).
- Phím `4`: Lọc theo từng thời kỳ lịch sử.
- Phím `5`: Mở giao diện đồ họa Pygame.

#### Cách 2: Chạy trực tiếp Giao diện Đồ họa Pygame
```powershell
python -m task2.demo_events --gui
```
- **Thanh bên trái**: Danh sách 30 sự kiện cuộn mượt mà theo năm.
- **Khung bên phải**: Thẻ sự kiện chi tiết gồm tiêu đề, mốc thời gian, nhân vật, tóm tắt diễn biến, ý nghĩa lịch sử.
- **Hộp Nguồn tài liệu (Xanh dương)**: Hiển thị đầy đủ tên sách, tác giả, nhà xuất bản, số trang và huy hiệu `✔ ĐÃ KIỂM CHỨNG LỊCH SỬ`.
- **Phím điều khiển**:
  - `Mũi tên Lên / Xuống`: Di chuyển chọn sự kiện.
  - `Cuộn chuột`: Cuộn danh sách.
  - `Click chuột`: Chọn sự kiện trực tiếp.
  - `ESC`: Đóng demo.
