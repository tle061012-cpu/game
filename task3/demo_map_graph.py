"""Task 3 Standalone Demo: Đồ thị địa điểm và cơ chế mở khóa theo tiến trình lịch sử.

Chạy độc lập:
  python -m task3.demo_map_graph
"""

import sys
import os
import pygame

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from task3.map_graph import HistoricalLocationGraph, LocationStatus

BACKGROUND = (245, 239, 220)
HEADER_RED = (180, 35, 45)
TEXT_DARK = (50, 45, 40)
TEXT_MUTED = (120, 115, 105)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
BLUE_EDGE = (35, 85, 145)
BORDER_GRAY = (200, 195, 185)
LOCKED_GRAY = (140, 135, 130)


def run_demo():
    pygame.init()
    WIDTH, HEIGHT = 1100, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DEMO TASK 3 - ĐỒ THỊ ĐỊA ĐIỂM & CƠ CHẾ MỞ KHÓA LỊCH SỬ")
    clock = pygame.time.Clock()

    graph = HistoricalLocationGraph()
    completed_nodes = set()  # Bắt đầu với tập rỗng
    selected_node_id = 1
    feedback = "Chọn một địa điểm bằng phím 1-8 hoặc Click chuột. Nhấn ENTER để hoàn thành nhiệm vụ!"

    title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 23, bold=True)
    body_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
    bold_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16, bold=True)
    small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 13)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif pygame.K_1 <= event.key <= pygame.K_8:
                    selected_node_id = event.key - pygame.K_0
                    feedback = f"Đã chọn mốc #{selected_node_id}: {graph.nodes[selected_node_id].name}"

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    status = graph.get_status(selected_node_id, completed_nodes)
                    if status == LocationStatus.LOCKED:
                        feedback = "✗ ĐỊA DANH ĐANG KHÓA! Hãy hoàn thành các sự kiện tiền đề trước."
                    elif status == LocationStatus.COMPLETED:
                        feedback = "✓ Địa danh này bạn đã hoàn thành rồi!"
                    else:
                        completed_nodes.add(selected_node_id)
                        # Tự động chọn địa danh tiếp theo nếu có
                        nexts = graph.adj_list.get(selected_node_id, [])
                        if nexts:
                            selected_node_id = nexts[0]
                        feedback = "✓ HOÀN THÀNH XUẤT SẮC! Cạnh đồ thị kích hoạt, đã mở khóa mốc tiếp theo!"

                elif event.key == pygame.K_r:
                    completed_nodes.clear()
                    selected_node_id = 1
                    feedback = "Đã đặt lại tiến trình đồ thị về mốc xuất phát ban đầu."

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for nid, node in graph.nodes.items():
                    # Tạo vị trí bố cục đồ thị trực quan trên màn hình
                    nx = 80 + ((nid - 1) % 4) * 230
                    ny = 160 + ((nid - 1) // 4) * 220
                    rect = pygame.Rect(nx, ny, 200, 160)
                    if rect.collidepoint((mx, my)):
                        selected_node_id = nid
                        feedback = f"Đã chọn: {node.name}"
                        break

        # ==================== VẼ GIAO DIỆN ====================
        screen.fill(BACKGROUND)

        # Header
        pygame.draw.rect(screen, (255, 252, 245), (0, 0, 1100, 85))
        pygame.draw.line(screen, BORDER_GRAY, (0, 85), (1100, 85), 2)
        screen.blit(title_font.render("TASK 3: ĐỒ THỊ ĐỊA ĐIỂM & ĐIỀU KIỆN MỞ KHÓA TIẾN TRÌNH LỊCH SỬ", True, HEADER_RED), (35, 15))
        screen.blit(small_font.render("Mô hình Directed Acyclic Graph (DAG) kết nối các sự kiện từ 1911 đến 1954", True, TEXT_MUTED), (38, 50))

        # Thống kê tiến trình
        pct = int(len(completed_nodes) / 8 * 100)
        prog_txt = f"Tiến độ đồ thị: {len(completed_nodes)}/8 ({pct}%)"
        screen.blit(bold_font.render(prog_txt, True, GREEN if pct == 100 else BLUE_EDGE), (850, 30))

        # Vẽ các cạnh đồ thị (Edges)
        for u, v_list in graph.adj_list.items():
            for v in v_list:
                ux = 80 + ((u - 1) % 4) * 230 + 100
                uy = 160 + ((u - 1) // 4) * 220 + 80
                vx = 80 + ((v - 1) % 4) * 230 + 100
                vy = 160 + ((v - 1) // 4) * 220 + 80

                u_status = graph.get_status(u, completed_nodes)
                edge_color = GREEN if u_status == LocationStatus.COMPLETED else BORDER_GRAY
                edge_width = 3 if u_status == LocationStatus.COMPLETED else 1
                pygame.draw.line(screen, edge_color, (ux, uy), (vx, vy), edge_width)

        # Vẽ 8 đỉnh đồ thị (Nodes)
        for nid, node in graph.nodes.items():
            nx = 80 + ((nid - 1) % 4) * 230
            ny = 160 + ((nid - 1) // 4) * 220
            rect = pygame.Rect(nx, ny, 200, 160)
            status = graph.get_status(nid, completed_nodes)
            is_selected = (nid == selected_node_id)

            # Màu sắc theo trạng thái
            if status == LocationStatus.COMPLETED:
                bg = (235, 250, 240)
                border = GREEN
                tag = "[✓ HOÀN THÀNH]"
                tag_col = GREEN
            elif status == LocationStatus.UNLOCKED:
                bg = (255, 248, 235)
                border = HEADER_RED
                tag = "[★ ĐANG MỞ KHÓA]"
                tag_col = HEADER_RED
            else:
                bg = (240, 238, 235)
                border = LOCKED_GRAY
                tag = "[🔒 ĐANG KHÓA]"
                tag_col = LOCKED_GRAY

            pygame.draw.rect(screen, bg, rect, border_radius=10)
            bw = 4 if is_selected else 2
            pygame.draw.rect(screen, (205, 145, 30) if is_selected else border, rect, bw, border_radius=10)

            # Text trên thẻ Node
            screen.blit(small_font.render(tag, True, tag_col), (nx + 10, ny + 10))
            screen.blit(bold_font.render(f"#{nid}. {node.year_period}", True, TEXT_DARK), (nx + 10, ny + 30))

            # Tên địa danh (xuống dòng nếu dài)
            name_words = node.name.split("(")
            screen.blit(bold_font.render(name_words[0].strip(), True, TEXT_DARK), (nx + 10, ny + 55))
            if len(name_words) > 1:
                screen.blit(small_font.render(f"({name_words[1]}", True, TEXT_MUTED), (nx + 10, ny + 78))

            # Điều kiện tiền đề
            if node.prerequisites:
                prereq_text = f"Yêu cầu: Mốc #{','.join(map(str, node.prerequisites))}"
            else:
                prereq_text = "Mốc khởi đầu"
            screen.blit(small_font.render(prereq_text, True, TEXT_MUTED), (nx + 10, ny + 130))

        # Thanh chi tiết địa danh đang chọn
        detail_box = pygame.Rect(30, 560, 1040, 75)
        pygame.draw.rect(screen, WHITE, detail_box, border_radius=8)
        pygame.draw.rect(screen, BORDER_GRAY, detail_box, 1, border_radius=8)

        sel_node = graph.nodes[selected_node_id]
        sel_status = graph.get_status(selected_node_id, completed_nodes)
        screen.blit(bold_font.render(f"Chi tiết Mốc #{selected_node_id}: {sel_node.name} ({sel_node.year_period})", True, TEXT_DARK), (45, 570))
        screen.blit(body_font.render(f"Sự kiện nòng cốt: {sel_node.description}", True, TEXT_DARK), (45, 595))
        screen.blit(small_font.render(f"Trạng thái: {sel_status.value} (Nhấn ENTER để hoàn thành và mở khóa tiếp theo)", True, BLUE_EDGE), (45, 618))

        # Footer hướng dẫn
        fb_rect = pygame.Rect(30, 648, 1040, 36)
        pygame.draw.rect(screen, (255, 252, 245), fb_rect, border_radius=6)
        screen.blit(bold_font.render(feedback, True, HEADER_RED if "✗" in feedback else GREEN), (45, 655))
        screen.blit(small_font.render("Phím tắt: [1-8]: Chọn mốc | [ENTER]: Hoàn thành | [R]: Reset | [ESC]: Thoát", True, TEXT_MUTED), (580, 658))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_demo()
