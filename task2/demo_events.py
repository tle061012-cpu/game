"""
================================================================================
TASK 2: DEMO XEM SỰ KIỆN LỊCH SỬ KÈM NGUỒN (HISTORICAL EVENTS & SOURCES DEMO)
================================================================================
Chạy chương trình demo tương tác:
1. Xem danh sách 30 sự kiện theo dòng thời gian kèm nguồn tóm tắt.
2. Xem chi tiết 1 sự kiện bất kỳ kèm hộp trích dẫn nguồn khoa học chính thống.
3. Tìm kiếm sự kiện theo từ khóa (tên sự kiện, năm, nhân vật, tài liệu nguồn).
4. Lọc sự kiện theo từng thời kỳ lịch sử.
5. Chạy giao diện đồ họa Pygame trực quan (GUI Timeline & Evidence Card).

Cách chạy:
    python -m task2.demo_events
hoặc:
    python -m task2.demo_events --gui
"""

import pygame
import os
import sys
import argparse
import textwrap

# Đảm bảo in tiếng Việt chuẩn trên Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from task2.schema import SuKienLichSu
from task2.event_service import event_service


# ==============================================================================
# PHẦN 1: GIAO DIỆN CONSOLE CLI (TEXT-BASED INTERACTIVE DEMO)
# ==============================================================================

def print_separator(char="=", length=85):
    print(char * length)


def print_event_card(sk: SuKienLichSu, index: int = None):
    """Hiển thị thẻ sự kiện chi tiết kèm nguồn trích dẫn lịch sử trang trọng"""
    print_separator("=")
    idx_str = f" [SỰ KIỆN #{index}] " if index else " "
    print(f"★{idx_str}{sk.ten_su_kien.upper()}")
    print_separator("-")
    
    print(f"⏰ Thời gian       : {sk.ngay_thang_chi_tiet} (Năm {sk.nam_dien_ra})")
    print(f"🏛 Thời kỳ         : {sk.thoi_ky}")
    if sk.dia_diem_lien_quan:
        print(f"📍 Địa điểm        : {sk.dia_diem_lien_quan}")
    if sk.nhan_vat_chinh:
        print(f"👤 Nhân vật chính  : {sk.nhan_vat_chinh}")
    
    # Nhân vật liên quan chi tiết
    if sk.danh_sach_nhan_vat:
        nv_names = [f"{nv.ten_nhan_vat} ({nv.vai_tro})" for nv in sk.danh_sach_nhan_vat]
        print(f"👥 Nhân vật chi tiết: {', '.join(nv_names)}")
    
    print("\n📜 TÓM TẮT DIỄN BIẾN:")
    wrapped_dien_bien = textwrap.fill(sk.tom_tat_dien_bien, width=82, initial_indent="   ", subsequent_indent="   ")
    print(wrapped_dien_bien)
    
    if sk.y_nghia_lich_su:
        print("\n🎯 Ý NGHĨA LỊCH SỬ:")
        wrapped_y_nghia = textwrap.fill(sk.y_nghia_lich_su, width=82, initial_indent="   ", subsequent_indent="   ")
        print(wrapped_y_nghia)
        
    print("\n" + "─" * 85)
    print("📖 NGUỒN TÀI LIỆU TRÍCH DẪN CHÍNH THỐNG (EVIDENCE & CITATION):")
    if sk.nguon:
        print(f"   • Tài liệu       : {sk.nguon.ten_tai_lieu}")
        print(f"   • Loại nguồn     : {sk.nguon.loai_nguon}")
        if sk.nguon.tac_gia_co_quan:
            print(f"   • Tác giả/Cơ quan: {sk.nguon.tac_gia_co_quan}")
        if sk.nguon.nha_xuat_ban:
            nam_xb = f" ({sk.nguon.nam_xuat_ban})" if sk.nguon.nam_xuat_ban else ""
            print(f"   • Nhà xuất bản   : NXB {sk.nguon.nha_xuat_ban}{nam_xb}")
        if sk.nguon.trich_dan_chi_tiet:
            print(f"   • Vị trí trích   : {sk.nguon.trich_dan_chi_tiet}")
        print(f"   • Xác thực       : ✔ {sk.nguon.muc_do_xac_thuc}")
        print(f"\n   -> Trích dẫn chuẩn: {sk.nguon.format_citation()}")
    else:
        print(f"   • {sk.nguon_trich_dan_text}")
    print_separator("=")


def demo_list_all_events():
    """Hiển thị danh sách 30 sự kiện theo bảng rút gọn"""
    events = event_service.get_all_events()
    print_separator("=")
    print(f"{'STT':<4} | {'NĂM':<6} | {'THỜI KỲ':<14} | {'TÊN SỰ KIỆN':<50}")
    print_separator("-")
    for idx, sk in enumerate(events, 1):
        ten_rut_gon = (sk.ten_su_kien[:47] + "...") if len(sk.ten_su_kien) > 50 else sk.ten_su_kien
        print(f"{idx:<4} | {sk.nam_dien_ra:<6} | {sk.thoi_ky[:14]:<14} | {ten_rut_gon:<50}")
    print_separator("=")
    print(f"Tổng số sự kiện đã nạp: {len(events)} sự kiện có nguồn trích dẫn.")


def demo_search_events():
    """Tìm kiếm sự kiện tương tác"""
    kw = input("\nNhập từ khóa tìm kiếm (tên, năm, nhân vật, tác giả, tài liệu): ").strip()
    if not kw:
        print("Từ khóa trống!")
        return
    results = event_service.search_events(kw)
    print(f"\nTìm thấy {len(results)} sự kiện phù hợp với từ khóa '{kw}':")
    for idx, sk in enumerate(results, 1):
        print(f"\n[{idx}] Năm {sk.nam_dien_ra}: {sk.ten_su_kien}")
        if sk.nguon:
            print(f"    Nguồn: {sk.nguon.format_citation()}")
        else:
            print(f"    Nguồn: {sk.nguon_trich_dan_text}")


def demo_filter_period():
    """Lọc sự kiện theo thời kỳ"""
    periods = event_service.get_all_periods()
    print("\nDanh sách các thời kỳ lịch sử:")
    for idx, p in enumerate(periods, 1):
        print(f"  {idx}. {p}")
    chon = input("\nChọn số thứ tự thời kỳ muốn lọc (1-{}): ".format(len(periods))).strip()
    try:
        idx_chon = int(chon) - 1
        if 0 <= idx_chon < len(periods):
            selected_period = periods[idx_chon]
            results = event_service.filter_by_period(selected_period)
            print(f"\nCó {len(results)} sự kiện thuộc thời kỳ '{selected_period}':")
            for sk in results:
                print(f"  - [{sk.nam_dien_ra}] {sk.ten_su_kien}")
        else:
            print("Lựa chọn không hợp lệ!")
    except ValueError:
        print("Vui lòng nhập số!")


def run_cli_menu():
    """Vòng lặp menu điều khiển CLI"""
    while True:
        print("\n" + "=" * 65)
        print("          DEMO TASK 2: DỮ LIỆU LỊCH SỬ CÓ NGUỒN")
        print("=" * 65)
        print("  1. Xem danh sách toàn bộ 30 sự kiện (Bảng tóm tắt)")
        print("  2. Xem chi tiết 1 sự kiện kèm hộp Nguồn trích dẫn (1-30)")
        print("  3. Tìm kiếm sự kiện theo từ khóa (Nhân vật, Địa danh, Nguồn)")
        print("  4. Lọc sự kiện theo thời kỳ lịch sử")
        print("  5. Khởi chạy Giao diện Đồ họa Pygame (GUI Timeline & Evidence)")
        print("  0. Thoát")
        print("-" * 65)
        choice = input("Nhập lựa chọn của bạn (0-5): ").strip()

        if choice == "1":
            demo_list_all_events()
        elif choice == "2":
            num = input("Nhập số thứ tự sự kiện cần xem chi tiết (1-30): ").strip()
            try:
                val = int(num)
                events = event_service.get_all_events()
                if 1 <= val <= len(events):
                    print_event_card(events[val - 1], index=val)
                else:
                    print(f"Số thứ tự phải từ 1 đến {len(events)}!")
            except ValueError:
                print("Vui lòng nhập số hợp lệ!")
        elif choice == "3":
            demo_search_events()
        elif choice == "4":
            demo_filter_period()
        elif choice == "5":
            run_pygame_gui_demo()
        elif choice == "0":
            print("\nCảm ơn bạn đã theo dõi Demo Task 2! Hẹn gặp lại.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 5!")


# ==============================================================================
# PHẦN 2: GIAO DIỆN ĐỒ HỌA PYGAME (GUI TIMELINE & EVIDENCE CARD)
# ==============================================================================

def get_vietnamese_font(size: int, bold: bool = False):
    """Tìm font hỗ trợ 100% tiếng Việt Unicode trên Windows (Tahoma, Arial, Segoe UI)"""
    candidate_paths = [
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\timesbd.ttf" if bold else r"C:\Windows\Fonts\times.ttf",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                continue
    return pygame.font.SysFont("tahoma,arial,timesnewroman", size, bold=bold)


def run_pygame_gui_demo():
    """Khởi chạy cửa sổ Pygame hiển thị danh sách 30 sự kiện kèm thẻ nguồn"""
    try:
        import pygame
    except ImportError:
        print("[LỖI] Chưa cài đặt Pygame trong môi trường!")
        return

    pygame.init()
    pygame.font.init()

    WIDTH, HEIGHT = 1120, 680
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task 2 Demo: 30 Sự kiện Lịch sử có nguồn trích dẫn")
    clock = pygame.time.Clock()

    # Màu sắc thiết kế mang phong cách sử học trang trọng
    BG_COLOR = (248, 245, 238)          # Giấy cổ điển ấm áp
    SIDEBAR_BG = (235, 230, 220)        # Cột danh sách
    HEADER_BG = (139, 35, 35)           # Đỏ cờ / đỏ gạch lịch sử
    TEXT_MAIN = (30, 30, 30)            # Đen sẫm
    TEXT_MUTED = (90, 85, 80)           # Xám nâu
    CARD_BG = (255, 255, 255)           # Trắng
    CARD_BORDER = (210, 200, 185)       # Viền thẻ
    SOURCE_BG = (240, 246, 252)         # Xanh nhạt học thuật
    SOURCE_BORDER = (88, 166, 255)      # Viền xanh kiểm chứng
    GOLD_ACCENT = (197, 134, 40)        # Vàng đồng
    HOVER_BG = (220, 212, 198)
    ACTIVE_BG = (139, 35, 35)

    # Khởi tạo font hệ thống hỗ trợ 100% tiếng Việt Unicode chuẩn
    font_title = get_vietnamese_font(20, bold=True)
    font_header = get_vietnamese_font(16, bold=True)
    font_bold = get_vietnamese_font(14, bold=True)
    font_text = get_vietnamese_font(14, bold=False)
    font_small = get_vietnamese_font(12, bold=False)

    events = event_service.get_all_events()
    selected_idx = 0
    scroll_offset = 0
    item_height = 54
    visible_items = 10

    running = True
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    if selected_idx > 0:
                        selected_idx -= 1
                        if selected_idx < scroll_offset:
                            scroll_offset = selected_idx
                elif event.key == pygame.K_DOWN:
                    if selected_idx < len(events) - 1:
                        selected_idx += 1
                        if selected_idx >= scroll_offset + visible_items:
                            scroll_offset = selected_idx - visible_items + 1
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(len(events) - visible_items, scroll_offset - event.y))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click chuột vào danh sách bên trái
                if mouse_pos[0] < 420 and 70 <= mouse_pos[1] <= 640:
                    clicked_rel = (mouse_pos[1] - 70) // item_height
                    clicked_idx = scroll_offset + clicked_rel
                    if 0 <= clicked_idx < len(events):
                        selected_idx = clicked_idx

        # ======================================================================
        # VẼ GIAO DIỆN
        # ======================================================================
        screen.fill(BG_COLOR)

        # 1. HEADER TRÊN CÙNG
        pygame.draw.rect(screen, HEADER_BG, (0, 0, WIDTH, 60))
        header_surf = font_title.render("TASK 2: DỮ LIỆU 30 SỰ KIỆN LỊCH SỬ VIỆT NAM CÓ NGUỒN TRÍCH DẪN", True, (255, 255, 255))
        screen.blit(header_surf, (25, 18))
        sub_surf = font_small.render("Dùng phím Mũi tên Lên / Xuống hoặc Cuộn chuột để xem chi tiết • ESC để đóng", True, (240, 220, 220))
        screen.blit(sub_surf, (WIDTH - sub_surf.get_width() - 25, 24))

        # 2. CỘT DANH SÁCH BÊN TRÁI (SIDEBAR)
        sidebar_w = 420
        pygame.draw.rect(screen, SIDEBAR_BG, (0, 60, sidebar_w, HEIGHT - 60))
        pygame.draw.line(screen, CARD_BORDER, (sidebar_w, 60), (sidebar_w, HEIGHT), 2)

        # Vẽ từng item sự kiện
        y_cursor = 65
        for i in range(scroll_offset, min(len(events), scroll_offset + visible_items)):
            sk = events[i]
            is_active = (i == selected_idx)
            item_rect = pygame.Rect(10, y_cursor, sidebar_w - 20, item_height - 6)

            if is_active:
                pygame.draw.rect(screen, ACTIVE_BG, item_rect, border_radius=6)
                badge_color = (255, 215, 0)
                title_color = (255, 255, 255)
                desc_color = (240, 230, 230)
            else:
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, HOVER_BG, item_rect, border_radius=6)
                else:
                    pygame.draw.rect(screen, CARD_BG, item_rect, border_radius=6)
                badge_color = GOLD_ACCENT
                title_color = TEXT_MAIN
                desc_color = TEXT_MUTED

            pygame.draw.rect(screen, CARD_BORDER, item_rect, width=1, border_radius=6)

            # Vẽ Badge Năm
            nam_surf = font_bold.render(f"[{sk.nam_dien_ra}]", True, badge_color)
            screen.blit(nam_surf, (item_rect.x + 10, item_rect.y + 8))

            # Tên sự kiện rút gọn
            ten_text = sk.ten_su_kien
            if len(ten_text) > 34:
                ten_text = ten_text[:33] + "..."
            ten_surf = font_bold.render(ten_text, True, title_color)
            screen.blit(ten_surf, (item_rect.x + 70, item_rect.y + 7))

            # Thời kỳ
            tk_surf = font_small.render(f"Thời kỳ: {sk.thoi_ky} • {sk.ngay_thang_chi_tiet}", True, desc_color)
            screen.blit(tk_surf, (item_rect.x + 70, item_rect.y + 28))

            y_cursor += item_height

        # Thanh cuộn nhỏ bên trái
        scrollbar_rect = pygame.Rect(sidebar_w - 6, 65, 4, HEIGHT - 75)
        pygame.draw.rect(screen, (200, 195, 185), scrollbar_rect, border_radius=2)
        if len(events) > visible_items:
            thumb_h = int((visible_items / len(events)) * (HEIGHT - 75))
            thumb_y = 65 + int((scroll_offset / (len(events) - visible_items)) * (HEIGHT - 75 - thumb_h))
            pygame.draw.rect(screen, GOLD_ACCENT, (sidebar_w - 6, thumb_y, 4, thumb_h), border_radius=2)

        # 3. KHUNG CHI TIẾT SỰ KIỆN VÀ NGUỒN (DETAIL PANEL - BÊN PHẢI)
        detail_x = sidebar_w + 20
        detail_y = 75
        detail_w = WIDTH - detail_x - 20
        detail_h = HEIGHT - detail_y - 20

        # Thẻ nền trắng
        card_rect = pygame.Rect(detail_x, detail_y, detail_w, detail_h)
        pygame.draw.rect(screen, CARD_BG, card_rect, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, card_rect, width=2, border_radius=10)

        current_event = events[selected_idx]

        # Tiêu đề sự kiện
        title_lines = textwrap.wrap(current_event.ten_su_kien, width=50)
        cur_y = detail_y + 16
        for line in title_lines:
            t_surf = font_title.render(line, True, HEADER_BG)
            screen.blit(t_surf, (detail_x + 20, cur_y))
            cur_y += 26

        # Dòng thông số nhanh: Mốc, Ngày tháng, Địa điểm, Nhân vật
        cur_y += 6
        info_str = f"[MỐC]: {current_event.ngay_thang_chi_tiet} (Năm {current_event.nam_dien_ra})   |   [THỜI KỲ]: {current_event.thoi_ky}"
        screen.blit(font_bold.render(info_str, True, GOLD_ACCENT), (detail_x + 20, cur_y))
        cur_y += 24

        if current_event.nhan_vat_chinh:
            screen.blit(font_text.render(f"• Nhân vật tiêu biểu: {current_event.nhan_vat_chinh}", True, TEXT_MAIN), (detail_x + 20, cur_y))
            cur_y += 22

        if current_event.dia_diem_lien_quan:
            screen.blit(font_text.render(f"• Địa điểm: {current_event.dia_diem_lien_quan}", True, TEXT_MAIN), (detail_x + 20, cur_y))
            cur_y += 24

        pygame.draw.line(screen, CARD_BORDER, (detail_x + 20, cur_y), (detail_x + detail_w - 20, cur_y), 1)
        cur_y += 12

        # Tóm tắt diễn biến
        screen.blit(font_header.render("Tóm tắt diễn biến lịch sử:", True, TEXT_MAIN), (detail_x + 20, cur_y))
        cur_y += 24
        desc_lines = textwrap.wrap(current_event.tom_tat_dien_bien, width=64)
        for dline in desc_lines:
            screen.blit(font_text.render(dline, True, TEXT_MAIN), (detail_x + 25, cur_y))
            cur_y += 20

        # Ý nghĩa lịch sử
        if current_event.y_nghia_lich_su:
            cur_y += 8
            screen.blit(font_header.render("Ý nghĩa lịch sử:", True, TEXT_MAIN), (detail_x + 20, cur_y))
            cur_y += 22
            yn_lines = textwrap.wrap(current_event.y_nghia_lich_su, width=64)
            for yline in yn_lines:
                screen.blit(font_text.render(yline, True, TEXT_MAIN), (detail_x + 25, cur_y))
                cur_y += 20

        # 4. HỘP NGUỒN TÀI LIỆU TRÍCH DẪN (EVIDENCE CITATION BOX)
        box_y = max(cur_y + 12, detail_y + detail_h - 145)
        box_rect = pygame.Rect(detail_x + 20, box_y, detail_w - 40, detail_y + detail_h - box_y - 15)
        pygame.draw.rect(screen, SOURCE_BG, box_rect, border_radius=8)
        pygame.draw.rect(screen, SOURCE_BORDER, box_rect, width=1, border_radius=8)

        # Header hộp nguồn
        screen.blit(font_bold.render("NGUỒN TRÍCH DẪN CHÍNH THỐNG (ACADEMIC EVIDENCE):", True, (12, 84, 155)), (box_rect.x + 12, box_rect.y + 8))
        
        # Huy hiệu kiểm chứng
        badge_rect = pygame.Rect(box_rect.x + box_rect.w - 205, box_rect.y + 6, 195, 22)
        pygame.draw.rect(screen, (220, 245, 225), badge_rect, border_radius=4)
        pygame.draw.rect(screen, (46, 160, 67), badge_rect, width=1, border_radius=4)
        screen.blit(font_bold.render("[V] ĐÃ KIỂM CHỨNG LỊCH SỬ", True, (25, 120, 45)), (badge_rect.x + 8, badge_rect.y + 3))

        if current_event.nguon:
            citation_str = current_event.nguon.format_citation()
            cit_lines = textwrap.wrap(citation_str, width=65)
            line_y = box_rect.y + 32
            for c_line in cit_lines:
                screen.blit(font_text.render(c_line, True, TEXT_MAIN), (box_rect.x + 15, line_y))
                line_y += 20
            
            extra_info = f"Loại tư liệu: {current_event.nguon.loai_nguon} | Mức độ: {current_event.nguon.muc_do_xac_thuc}"
            screen.blit(font_small.render(extra_info, True, TEXT_MUTED), (box_rect.x + 15, line_y + 4))
        else:
            screen.blit(font_text.render(current_event.nguon_trich_dan_text, True, TEXT_MAIN), (box_rect.x + 15, box_rect.y + 35))

        pygame.display.flip()

    pygame.quit()


# ==============================================================================
# HÀM MAIN ĐIỀU PHỐI DEMO
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Task 2: Demo Dữ liệu Lịch sử có nguồn")
    parser.add_argument("--gui", action="store_true", help="Chạy thẳng giao diện đồ họa Pygame")
    args = parser.parse_args()

    if args.gui:
        run_pygame_gui_demo()
    else:
        run_cli_menu()


if __name__ == "__main__":
    main()
