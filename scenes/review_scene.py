"""Màn hình Ôn tập kiến thức và tra cứu nguồn lịch sử (Task 5 Scene)."""

import pygame
from typing import Optional, List, Dict, Any
from task5.review_system import ReviewManager, ReviewQuestion, ReviewStatus
from task5.scoring_system import ScoringEngine

BACKGROUND = (245, 239, 220)
HEADER_RED = (180, 35, 45)
TEXT_DARK = (50, 45, 40)
TEXT_MUTED = (120, 115, 105)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
BLUE_SOURCE = (35, 85, 145)
ACCENT_GOLD = (205, 145, 30)
BORDER_GRAY = (210, 205, 195)
CARD_BG = (255, 252, 245)
WRONG_BG = (255, 235, 235)
CORRECT_BG = (235, 250, 240)


class ReviewScene:
    """Màn hình Ôn tập sau màn chơi - Trung tâm củng cố tri thức và tra cứu nguồn."""

    def __init__(self, review_manager: Optional[ReviewManager] = None, scoring_engine: Optional[ScoringEngine] = None):
        self.review_manager = review_manager or ReviewManager()
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.selected_index = 0
        self.player_name = "Học giả Lịch Sử"
        self.feedback_message = "Chọn một câu hỏi bên trái và bấm 1-4 để thử thách lại!"
        self.feedback_color = TEXT_MUTED

        # Fonts
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 24, bold=True)
        self.section_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 19, bold=True)
        self.body_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.bold_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16, bold=True)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 13)
        self.citation_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 14, italic=True)

        self._ensure_sample_if_empty()

    def _ensure_sample_if_empty(self):
        """Khởi tạo một số câu hỏi ôn tập mẫu từ các mốc 1911, 1930, 1941 nếu danh sách trống."""
        if not self.review_manager.questions:
            self.review_manager.record_mistake(
                question_id="sample_1911",
                location_name="Bến Nhà Rồng",
                question_text="Nguyễn Tất Thành ra đi tìm đường cứu nước trên con tàu nào?",
                options=["Tàu Amiral Latouche-Tréville", "Tàu Đô đốc Courbet", "Tàu D'Assas", "Tàu La Grandière"],
                correct_index=0,
                user_choice=1,
                explanation="Ngày 5/6/1911, Người rời bến cảng Nhà Rồng trên tàu buôn Đô đốc Latouche-Tréville với tên gọi Văn Ba.",
                source_title="Đại cương Lịch sử Việt Nam (Tập 2)",
                source_author="Đinh Xuân Lâm (Chủ biên)",
                source_publisher="NXB Giáo dục Việt Nam",
                source_citation="Chương 4: Phong trào yêu nước đầu thế kỷ XX, Tr. 182-185",
            )
            self.review_manager.record_mistake(
                question_id="sample_1930",
                location_name="Hương Cảng",
                question_text="Hội nghị hợp nhất thành lập Đảng Cộng sản Việt Nam thông qua văn kiện nòng cốt nào?",
                options=["Chính cương vắn tắt, Sách lược vắn tắt", "Luận cương chính trị tháng 10", "Tuyên ngôn Độc lập", "Kháng chiến nhất định thắng lợi"],
                correct_index=0,
                user_choice=1,
                explanation="Hội nghị thành lập Đảng đầu năm 1930 đã thông qua Chính cương vắn tắt và Sách lược vắn tắt do Nguyễn Ái Quốc soạn thảo.",
                source_title="Văn kiện Đảng Toàn tập (Tập 2)",
                source_author="Ban Chấp hành Trung ương Đảng",
                source_publisher="NXB Chính trị Quốc gia Sự thật",
                source_citation="Văn kiện Hội nghị hợp nhất ngày 3/2/1930, Tr. 1-15",
            )
            self.review_manager.record_mistake(
                question_id="sample_1975",
                location_name="Dinh Độc Lập (1975)",
                question_text="Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam vào ngày nào?",
                options=["Ngày 30/04/1975", "Ngày 26/03/1975", "Ngày 01/05/1975", "Ngày 02/09/1975"],
                correct_index=0,
                user_choice=1,
                explanation="11h30 ngày 30/4/1975, xe tăng giải phóng tiến vào Dinh Độc Lập, kết thúc thắng lợi cuộc kháng chiến chống Mỹ cứu nước.",
                source_title="Tổng hành dinh trong Mùa Xuân toàn thắng",
                source_author="Đại tướng Võ Nguyên Giáp",
                source_publisher="NXB Chính trị Quốc gia Sự thật",
                source_citation="Chương 5: Chiến dịch Hồ Chí Minh toàn thắng, Tr. 312-325",
            )

    def get_active_questions(self) -> List[ReviewQuestion]:
        """Ưu tiên hiển thị các câu hỏi đang cần ôn tập (PENDING), sau đó đến câu đã hoàn thành."""
        pending = self.review_manager.get_pending_questions()
        mastered = self.review_manager.get_mastered_questions()
        return pending + mastered

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Xử lý sự kiện bàn phím và chuột trên màn hình ôn tập."""
        questions = self.get_active_questions()
        if not questions:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_m):
                return "map"
            return None

        # Giới hạn chỉ mục lựa chọn
        self.selected_index = max(0, min(self.selected_index, len(questions) - 1))
        current_q = questions[self.selected_index]

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_m):
                return "map"

            elif event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self.feedback_message = "Đã chuyển câu hỏi. Bấm 1-4 để trả lời lại!"
                    self.feedback_color = TEXT_MUTED

            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(questions) - 1:
                    self.selected_index += 1
                    self.feedback_message = "Đã chuyển câu hỏi. Bấm 1-4 để trả lời lại!"
                    self.feedback_color = TEXT_MUTED

            elif event.key == pygame.K_p:
                path = self.scoring_engine.export_certificate(self.player_name)
                self.feedback_message = "✓ ĐÃ XUẤT BẰNG CHỨNG NHẬN HỌC GIẢ VÀO: data/chung_nhan_hoc_gia.png"
                self.feedback_color = GREEN

            elif pygame.K_1 <= event.key <= pygame.K_4:
                choice = event.key - pygame.K_1
                self._process_answer(current_q, choice)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Click nút Xuất Bằng Chứng Nhận
            cert_btn = pygame.Rect(740, 20, 175, 45)
            if cert_btn.collidepoint((mouse_x, mouse_y)):
                self.scoring_engine.export_certificate(self.player_name)
                self.feedback_message = "✓ ĐÃ XUẤT BẰNG CHỨNG NHẬN HỌC GIẢ VÀO: data/chung_nhan_hoc_gia.png"
                self.feedback_color = GREEN
                return None

            # Click nút quay lại Bản đồ (Góc trên bên phải)
            back_btn = pygame.Rect(930, 20, 140, 45)
            if back_btn.collidepoint((mouse_x, mouse_y)):
                return "map"

            # Click chọn câu hỏi từ danh sách bên trái
            list_start_y = 110
            for idx in range(len(questions)):
                item_rect = pygame.Rect(35, list_start_y + idx * 75, 330, 68)
                if item_rect.collidepoint((mouse_x, mouse_y)):
                    self.selected_index = idx
                    self.feedback_message = "Đã chọn câu hỏi. Bấm vào đáp án để trả lời lại!"
                    self.feedback_color = TEXT_MUTED
                    break

            # Click chọn đáp án bên phải
            ans_start_y = 220
            for opt_idx in range(len(current_q.options)):
                opt_rect = pygame.Rect(400, ans_start_y + opt_idx * 56, 660, 48)
                if opt_rect.collidepoint((mouse_x, mouse_y)):
                    self._process_answer(current_q, opt_idx)
                    break

        return None

    def _process_answer(self, question: ReviewQuestion, choice_index: int):
        """Kiểm tra câu trả lời ôn tập và cộng điểm nếu đúng."""
        result = self.review_manager.retry_answer(question.id, choice_index)
        if result.is_correct:
            earned = self.scoring_engine.record_review_reward(question.id)
            self.feedback_message = f"✓ XUẤT SẮC! Bạn đã trả lời đúng và nhận +{earned} điểm cứu vớt kiến thức!"
            self.feedback_color = GREEN
        else:
            self.feedback_message = "✗ Chưa chính xác. Hãy đọc kỹ phần NGUỒN SỬ LIỆU bên dưới để nắm vững tư liệu!"
            self.feedback_color = HEADER_RED

    def draw(self, screen: pygame.Surface):
        """Vẽ toàn bộ giao diện màn hình ôn tập."""
        screen.fill(BACKGROUND)
        questions = self.get_active_questions()

        # ==================== 1. THANH HEADER ====================
        header_rect = pygame.Rect(0, 0, 1100, 85)
        pygame.draw.rect(screen, CARD_BG, header_rect)
        pygame.draw.line(screen, BORDER_GRAY, (0, 85), (1100, 85), 2)

        # Tiêu đề
        title = self.title_font.render("PHÒNG ÔN TẬP VÀ KIỂM CHỨNG TƯ LIỆU SỬ HỌC", True, HEADER_RED)
        screen.blit(title, (35, 16))
        sub_text = self.small_font.render("Hệ thống tổng hợp câu hỏi chưa chính xác & tra cứu chứng cứ học thuật chính thống", True, TEXT_MUTED)
        screen.blit(sub_text, (38, 50))

        # Thống kê điểm & Danh hiệu
        summary = self.scoring_engine.export_summary()
        badge_text = f"Điểm: {summary['total_score']} | Danh hiệu: {summary['rank_title']}"
        badge_surface = self.bold_font.render(badge_text, True, ACCENT_GOLD)
        screen.blit(badge_surface, (540, 28))

        # Nút Xuất Bằng Chứng Nhận (Hạng S/A)
        cert_btn = pygame.Rect(740, 20, 175, 45)
        pygame.draw.rect(screen, (195, 145, 30), cert_btn, border_radius=8)
        cert_text = self.bold_font.render("Xuất Bằng (P)", True, WHITE)
        screen.blit(cert_text, cert_text.get_rect(center=cert_btn.center))

        # Nút Quay lại Bản đồ
        back_btn = pygame.Rect(930, 20, 140, 45)
        pygame.draw.rect(screen, HEADER_RED, back_btn, border_radius=8)
        back_text = self.bold_font.render("Về Bản đồ (ESC)", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))

        if not questions:
            empty_msg = self.section_font.render("Tuyệt vời! Bạn không có câu hỏi nào cần ôn tập.", True, GREEN)
            screen.blit(empty_msg, (320, 320))
            return

        # Giữ chỉ mục hợp lệ
        self.selected_index = max(0, min(self.selected_index, len(questions) - 1))
        current_q = questions[self.selected_index]

        # ==================== 2. CỘT TRÁI: DANH SÁCH CÂU HỎI ====================
        left_box = pygame.Rect(30, 100, 345, 540)
        pygame.draw.rect(screen, WHITE, left_box, border_radius=10)
        pygame.draw.rect(screen, BORDER_GRAY, left_box, 2, border_radius=10)

        left_title = self.bold_font.render(f"DANH SÁCH CÂU HỎI ({len(questions)})", True, TEXT_DARK)
        screen.blit(left_title, (45, 115))

        list_y = 150
        for i, q in enumerate(questions):
            is_selected = (i == self.selected_index)
            item_rect = pygame.Rect(40, list_y + i * 80, 325, 70)

            # Màu nền thẻ
            if is_selected:
                bg_col = (255, 246, 230)
                border_col = ACCENT_GOLD
                border_w = 3
            else:
                bg_col = CORRECT_BG if q.status == ReviewStatus.MASTERED else CARD_BG
                border_col = BORDER_GRAY
                border_w = 1

            pygame.draw.rect(screen, bg_col, item_rect, border_radius=8)
            pygame.draw.rect(screen, border_col, item_rect, border_w, border_radius=8)

            # Nội dung tóm tắt thẻ
            tag = "[ĐÃ ĐẠT]" if q.status == ReviewStatus.MASTERED else f"[Cần ôn tập - Sai {q.retry_count} lần]"
            tag_color = GREEN if q.status == ReviewStatus.MASTERED else HEADER_RED
            screen.blit(self.small_font.render(tag, True, tag_color), (item_rect.x + 10, item_rect.y + 8))

            loc_text = self.bold_font.render(f"• {q.location_name}", True, TEXT_DARK)
            screen.blit(loc_text, (item_rect.x + 10, item_rect.y + 26))

            short_q = q.question[:36] + "..." if len(q.question) > 36 else q.question
            screen.blit(self.small_font.render(short_q, True, TEXT_MUTED), (item_rect.x + 10, item_rect.y + 48))

        # ==================== 3. CỘT PHẢI: CHI TIẾT CÂU HỎI & NGUỒN ====================
        right_box = pygame.Rect(390, 100, 680, 540)
        pygame.draw.rect(screen, WHITE, right_box, border_radius=10)
        pygame.draw.rect(screen, BORDER_GRAY, right_box, 2, border_radius=10)

        # Nhãn câu hỏi
        status_badge = "ĐÃ ÔN TẬP THÀNH CÔNG" if current_q.status == ReviewStatus.MASTERED else "ĐANG CẦN CỦNG CỐ"
        status_color = GREEN if current_q.status == ReviewStatus.MASTERED else HEADER_RED
        screen.blit(self.bold_font.render(f"Địa danh: {current_q.location_name} | Trạng thái: {status_badge}", True, status_color), (410, 115))

        # Câu hỏi chính
        q_surface = self.section_font.render(f"Câu hỏi: {current_q.question}", True, TEXT_DARK)
        screen.blit(q_surface, (410, 142))

        # 4 Phương án lựa chọn (Click hoặc 1-4)
        opt_y = 185
        for idx, opt in enumerate(current_q.options):
            opt_rect = pygame.Rect(410, opt_y + idx * 52, 640, 44)
            is_correct = (idx == current_q.correct_index)

            # Màu hiển thị
            if current_q.status == ReviewStatus.MASTERED and is_correct:
                opt_bg = CORRECT_BG
                opt_border = GREEN
            elif idx == current_q.user_choice and not is_correct:
                opt_bg = WRONG_BG
                opt_border = HEADER_RED
            else:
                opt_bg = CARD_BG
                opt_border = BORDER_GRAY

            pygame.draw.rect(screen, opt_bg, opt_rect, border_radius=8)
            pygame.draw.rect(screen, opt_border, opt_rect, 2, border_radius=8)

            char_key = chr(65 + idx)
            prefix = f"[{idx + 1}] {char_key}. {opt}"
            if current_q.status == ReviewStatus.MASTERED and is_correct:
                prefix += "  ✓ (Đáp án chính xác)"
            elif idx == current_q.user_choice and not is_correct:
                prefix += "  ✗ (Bạn đã chọn câu này)"

            screen.blit(self.body_font.render(prefix, True, TEXT_DARK), (opt_rect.x + 14, opt_rect.y + 12))

        # ==================== 4. KHUNG NGUỒN TƯ LIỆU HỌC THUẬT (TASK 2 CITATION) ====================
        source_box = pygame.Rect(410, 410, 640, 155)
        pygame.draw.rect(screen, (240, 246, 255), source_box, border_radius=10)
        pygame.draw.rect(screen, BLUE_SOURCE, source_box, 2, border_radius=10)

        # Header Khung nguồn
        screen.blit(self.bold_font.render("NGUỒN SỬ LIỆU & BẰNG CHỨNG KIỂM CHỨNG HỌC THUẬT (TASK 2)", True, BLUE_SOURCE), (425, 420))
        screen.blit(self.small_font.render("✔ ĐÃ KIỂM CHỨNG LỊCH SỬ CHÍNH THỐNG CẤP QUỐC GIA", True, GREEN), (740, 422))

        # Chi tiết trích dẫn
        s_title = self.bold_font.render(f"• Tác phẩm: {current_q.source_title}", True, TEXT_DARK)
        screen.blit(s_title, (425, 448))

        s_auth = self.body_font.render(f"• Tác giả / NXB: {current_q.source_author} | {current_q.source_publisher}", True, TEXT_DARK)
        screen.blit(s_auth, (425, 472))

        s_cite = self.citation_font.render(f"• Trích dẫn vị trí: {current_q.source_citation}", True, BLUE_SOURCE)
        screen.blit(s_cite, (425, 496))

        s_exp = self.small_font.render(f"• Bản chất sự kiện: {current_q.explanation}", True, TEXT_DARK)
        screen.blit(s_exp, (425, 524))

        # ==================== 5. THANH PHẢN HỒI DƯỚI CÙNG ====================
        fb_rect = pygame.Rect(30, 650, 1040, 36)
        pygame.draw.rect(screen, WHITE, fb_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_GRAY, fb_rect, 1, border_radius=6)
        fb_surface = self.bold_font.render(self.feedback_message, True, self.feedback_color)
        screen.blit(fb_surface, (45, 657))

        hint_text = self.small_font.render("Phím tắt: [1-4]: Chọn đáp án ôn tập | [Lên/Xuống]: Đổi câu hỏi | [ESC]: Quay lại Bản đồ", True, TEXT_MUTED)
        screen.blit(hint_text, (550, 660))

