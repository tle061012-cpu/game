"""Task 5 Standalone Demo: Trình diễn màn hình Ôn tập kiến thức & Nguồn sử liệu.

Chạy độc lập:
  python -m task5.demo_task5
hoặc chạy từ thư mục gốc của project.
"""

import sys
import os
import pygame

# Đảm bảo đường dẫn import hoạt động độc lập
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from scenes.review_scene import ReviewScene
from task5.scoring_system import ScoringEngine
from task5.review_system import ReviewManager


def run_demo():
    pygame.init()
    WIDTH, HEIGHT = 1100, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DEMO TASK 5 - MÀN HÌNH ÔN TẬP VÀ KIỂM CHỨNG LỊCH SỬ")
    clock = pygame.time.Clock()

    # Khởi tạo dữ liệu mẫu cho demo
    scoring = ScoringEngine(initial_score=150)
    review_mgr = ReviewManager()

    # Nạp 3 câu hỏi mẫu điển hình gắn với 3 mốc lịch sử
    review_mgr.record_mistake(
        question_id="demo_1911",
        location_name="Bến Nhà Rồng (1911)",
        question_text="Nguyễn Tất Thành ra đi tìm đường cứu nước trên con tàu nào?",
        options=[
            "Tàu Đô đốc Latouche-Tréville",
            "Tàu Đô đốc Courbet",
            "Tàu D'Assas",
            "Tàu La Grandière",
        ],
        correct_index=0,
        user_choice=1,
        explanation="Ngày 5/6/1911, Nguyễn Tất Thành lấy tên Văn Ba rời bến cảng Nhà Rồng trên tàu buôn Latouche-Tréville.",
        source_title="Đại cương Lịch sử Việt Nam (Tập 2)",
        source_author="Đinh Xuân Lâm (Chủ biên)",
        source_publisher="NXB Giáo dục Việt Nam",
        source_citation="Chương 4: Phong trào yêu nước đầu TK XX, Tr. 182-185",
    )

    review_mgr.record_mistake(
        question_id="demo_1930",
        location_name="Hương Cảng (1930)",
        question_text="Đảng Cộng sản Việt Nam ra đời sau hội nghị hợp nhất vào thời gian nào?",
        options=[
            "Ngày 03/02/1930",
            "Ngày 19/05/1930",
            "Ngày 02/09/1930",
            "Ngày 28/01/1930",
        ],
        correct_index=0,
        user_choice=2,
        explanation="Hội nghị hợp nhất các tổ chức cộng sản diễn ra từ 6/1 đến đầu tháng 2/1930, lấy ngày 3/2 làm ngày thành lập Đảng.",
        source_title="Văn kiện Đảng Toàn tập (Tập 2)",
        source_author="Ban Chấp hành Trung ương Đảng",
        source_publisher="NXB Chính trị Quốc gia Sự thật",
        source_citation="Hội nghị hợp nhất Đảng đầu năm 1930, Tr. 1-15",
    )

    review_mgr.record_mistake(
        question_id="demo_1941",
        location_name="Hang Pác Bó (1941)",
        question_text="Hội nghị Trung ương Đảng lần thứ 8 họp tại Pác Bó đã đưa ra quyết sách gì?",
        options=[
            "Đặt nhiệm vụ giải phóng dân tộc lên hàng đầu và thành lập Mặt trận Việt Minh",
            "Phát động phong trào Cần Vương cứu nước",
            "Ký Hiệp định Sơ bộ",
            "Thực hiện phong trào Đông Du",
        ],
        correct_index=0,
        user_choice=3,
        explanation="Hội nghị Trung ương 8 (5/1941) khẳng định giải phóng dân tộc là nhiệm vụ bức thiết nhất và sáng lập Mặt trận Việt Minh.",
        source_title="Hồ Chí Minh: Biên niên tiểu sử (Tập 3)",
        source_author="Viện Lịch sử Đảng",
        source_publisher="NXB Chính trị Quốc gia",
        source_citation="Giai đoạn 1941-1945, Hội nghị TW 8, Tr. 120-135",
    )

    scene = ReviewScene(review_manager=review_mgr, scoring_engine=scoring)

    print("=" * 65)
    print(">> ĐANG CHẠY DEMO TASK 5 (MÀN HÌNH ÔN TẬP VÀ KIỂM CHỨNG SỬ LIỆU)")
    print(">> Nhấn phím 1-4: Thử lại câu trả lời")
    print(">> Nhấn Mũi tên Lên/Xuống: Đổi câu hỏi ôn tập")
    print(">> Nhấn ESC hoặc click 'Về Bản đồ': Thoát demo")
    print("=" * 65)

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            result = scene.handle_event(event)
            if result == "map":
                print(">> Người chơi bấm quay lại Bản đồ. Kết thúc phiên ôn tập!")
                running = False

        scene.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_demo()

