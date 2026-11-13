# Task 5 — Điểm Kiến thức, Ôn tập Câu sai và Deploy (Knowledge Scoring, Review System & Deployment)

Tài liệu kỹ thuật và hướng dẫn thực thi cho **Task 5: Game Lịch sử Việt Nam**.

---

## 1. Mục tiêu & Nghiệp vụ Task 5

1. **Thuật toán tính điểm tri thức (Knowledge Scoring Algorithm):**
   - **Điểm cơ bản (Base Points):** +30 điểm cho mỗi câu hỏi trắc nghiệm đúng, +40 điểm cho ghép đúng timeline.
   - **Thưởng tốc độ (Time Bonus):** Người chơi trả lời nhanh hơn thời gian tiêu chuẩn (30s) được cộng thưởng:
     $$\text{Bonus} = \lfloor(30 - \text{Thời gian}) \times 0.8\rfloor$$
   - **Hệ số chuỗi đúng (Streak Multiplier):** Trả lời đúng liên tiếp nhân hệ số từ $1.0\times$ đến tối đa $1.5\times$:
     $$\text{Multiplier} = \min(1.0 + (\text{Streak} - 1) \times 0.1, 1.5)$$
   - **Điểm trừ sai lệch (Penalty):** -10 điểm khi trả lời sai.
   - **Hệ thống Danh hiệu Lịch sử (5 cấp bậc):**
     * `< 100 điểm`: *Tập Sự Lịch Sử*
     * `100 – 299 điểm`: *Người Tìm Kiếm Tư Liệu*
     * `300 – 599 điểm`: *Học Giả Sử Học*
     * `600 – 999 điểm`: *Nhà Nghiên Cứu Lịch Sử*
     * `≥ 1000 điểm`: *Bậc Thầy Sử Học Việt Nam*

2. **Hệ thống Ôn tập & Kiểm chứng Sử liệu (`ReviewScene` & `ReviewManager`):**
   - Tự động bắt và lưu trữ tất cả các câu hỏi người chơi đã trả lời sai trong suốt quá trình điều tra.
   - Cung cấp giao diện tra cứu 2 cột:
     * Cột trái: Danh sách các câu hỏi chưa đạt yêu cầu theo từng địa danh.
     * Cột phải: Chi tiết câu hỏi, các phương án lựa chọn, và **khung Trích dẫn Sử liệu học thuật chính thống (kế thừa từ CSDL Task 2)**.
   - Cho phép người chơi **thử thách lại trực tiếp (Retry)**: Bấm 1-4 hoặc click chuột. Nếu trả lời đúng, nhận điểm thưởng cứu vớt (+15 điểm) và chuyển trạng thái sang `MASTERED`.

3. **Đóng gói & Triển khai (Deploy):**
   - Tương thích với `pygbag` để chạy trên nền tảng WebGL/Trình duyệt HTML5.
   - Kết nối lưu trữ tiến độ và điểm số lên MySQL và REST API backend.

---

## 2. Cấu trúc Module Code Task 5

```
task5/
├── __init__.py           # Package exports
├── scoring_system.py     # ScoringEngine, KnowledgeScore, HistoryRank
├── review_system.py      # ReviewManager, ReviewQuestion, ReviewStatus
├── demo_task5.py         # Script chạy Demo độc lập cho Task 5 (phục vụ quay video/ảnh slide 9)
└── README.md             # Tài liệu đặc tả kỹ thuật Task 5
```

Màn hình giao diện:
- `scenes/review_scene.py`: Giao diện Pygame chuẩn 1100x700 cho màn hình Ôn tập.

---

## 3. Hướng dẫn chạy thử Demo Task 5

Mở terminal/PowerShell tại thư mục `PythonProject16\PythonProject16\PythonProject16\PythonProject16`:

```powershell
python -m task5.demo_task5
```

**Thao tác điều khiển trên màn hình:**
- **Phím 1, 2, 3, 4 hoặc Click chuột:** Chọn phương án để trả lời lại câu hỏi sai.
- **Phím Mũi tên Lên / Xuống hoặc Click danh sách trái:** Chuyển đổi qua lại giữa các câu hỏi cần ôn tập.
- **Phím ESC hoặc click nút "Về Bản đồ":** Hoàn tất ôn tập và quay lại màn hình chính.

