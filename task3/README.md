# Task 3 — Bản Đồ Tương Tác & Đồ Thị Mở Khóa Địa Điểm (Interactive Map & Progression Graph)

Tài liệu hướng dẫn và đặc tả kỹ thuật cho **Task 3: Bản đồ tương tác và Đồ thị địa điểm**.

---

## 1. Mô hình Đồ thị có hướng (Directed Acyclic Graph - DAG)

Hệ thống bản đồ sử dụng mô hình Đồ thị có hướng để ràng buộc cây tiến trình lịch sử Việt Nam từ 1911 đến 1954:

```
[1. Bến Nhà Rồng (1911)] ──► [2. Hương Cảng (1930)] ──► [3. Vinh - Bến Thủy (1930)]
                                                                  │
                                                                  ▼
[6. Quảng trường Ba Đình (1945)] ◄── [5. Tân Trào (1945)] ◄── [4. Hang Pác Bó (1941)]
             │
             ▼
[7. Chiến khu Việt Bắc (1947)] ──► [8. Điện Biên Phủ (1954)]
```

### Các trạng thái của nút địa danh (Node States):
1. **`LOCKED` (Khóa):** Chưa hoàn thành tất cả các sự kiện tiền đề (Prerequisites). Node hiển thị màu xám cùng biểu tượng ổ khóa.
2. **`UNLOCKED` (Mở khóa):** Đã thỏa mãn tiền đề, sẵn sàng để người chơi di chuyển tới và kích hoạt màn hình Điều tra.
3. **`COMPLETED` (Hoàn thành):** Đã thu thập đủ manh mối và giải quyết thành công câu đố suy luận timeline. Node hiển thị màu xanh lá cùng huy hiệu vinh danh.

---

## 2. Cấu trúc Module Code Task 3

```
task3/
├── __init__.py           # Package exports
├── map_graph.py          # Lớp HistoricalLocationGraph, LocationNode, LocationStatus
├── demo_map_graph.py     # Script Demo trực quan hóa đồ thị và mô phỏng cơ chế mở khóa
└── README.md             # Tài liệu Task 3
```

Màn hình bản đồ tích hợp:
- `scenes/map_scene.py`: Bản đồ địa lý Việt Nam (`bando.jpg`) với các điểm nút tương tác.

---

## 3. Hướng dẫn Chạy thử Demo Task 3

```powershell
python -m task3.demo_map_graph
```

**Thao tác điều khiển:**
- **Phím 1-8 hoặc Click chuột:** Chọn địa danh cần xem.
- **Phím ENTER hoặc Space:** Giả lập hoàn thành địa danh -> Quan sát cạnh đồ thị kích hoạt và mở khóa địa danh tiếp theo.
- **Phím R:** Reset toàn bộ tiến trình đồ thị.
- **Phím ESC:** Thoát demo.
