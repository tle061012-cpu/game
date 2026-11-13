
import pygame

BACKGROUND = (245, 239, 220)
RED = (180, 35, 45)
DARK = (50, 45, 40)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
GRAY = (210, 205, 195)

# Cau hoi suy luan cho TUNG dia diem (khoa la ten dia diem trong map_scene).
# "answer" la vi tri dap an dung trong "options" (tinh tu 0).
QUESTIONS = {
    "Ben Nha Rong": [
        {
            "question": "Nguyễn Tất Thành ra đi tìm đường cứu nước từ bến cảng Nhà Rồng vào năm nào?",
            "options": ["1905", "1911", "1919", "1925"],
            "answer": 1,
            "explanation": "Ngày 5/6/1911, Nguyễn Tất Thành ra đi từ bến cảng Nhà Rồng trên con tàu Đô đốc Latouche-Tréville."
        }
    ],
    "Hong Kong": [
        {
            "question": "Đảng Cộng sản Việt Nam được thành lập tại Hương Cảng vào thời gian nào?",
            "options": ["Tháng 2-1930", "Tháng 9-1930", "Tháng 5-1941", "Tháng 8-1945"],
            "answer": 0,
            "explanation": "Đảng Cộng sản Việt Nam ra đời ngày 3/2/1930 sau hội nghị hợp nhất do Nguyễn Ái Quốc chủ trì."
        }
    ],
    "Vinh - Ben Thuy": [
        {
            "question": "Phong trào đấu tranh tiêu biểu nhất ở Nghệ An - Hà Tĩnh năm 1930-1931 là gì?",
            "options": [
                "Xô viết Nghệ - Tĩnh",
                "Khởi nghĩa Yên Bái",
                "Phong trào Cần Vương",
                "Cách mạng tháng Tám"
            ],
            "answer": 0,
            "explanation": "Đỉnh cao của cao trào cách mạng 1930-1931 là phong trào Xô viết Nghệ - Tĩnh."
        }
    ],
    "Pac Bo": [
        {
            "question": "Lãnh tụ Nguyễn Ái Quốc trở về Tổ quốc tại Pác Bó (Cao Bằng) vào năm nào?",
            "options": ["1930", "1941", "1945", "1954"],
            "answer": 1,
            "explanation": "Ngày 28/01/1941, Bác vượt mốc 108 trở về Pác Bó trực tiếp lãnh đạo cách mạng."
        }
    ],
    "Tan Trao": [
        {
            "question": "Quốc dân Đại hội họp tại Tân Trào (16/8/1945) đã đưa ra quyết định quan trọng nào?",
            "options": [
                "Tán thành lệnh Tổng khởi nghĩa giành chính quyền",
                "Ký Hiệp định Sơ bộ",
                "Mở chiến dịch Biên giới",
                "Thành lập Mặt trận Việt Minh"
            ],
            "answer": 0,
            "explanation": "Quốc dân Đại hội Tân Trào đã thông qua lệnh Tổng khởi nghĩa giành chính quyền trong cả nước."
        }
    ],
    "Ba Dinh": [
        {
            "question": "Chủ tịch Hồ Chí Minh đọc bản Tuyên ngôn Độc lập tại Quảng trường Ba Đình vào ngày nào?",
            "options": ["19/08/1945", "02/09/1945", "07/05/1954", "19/12/1946"],
            "answer": 1,
            "explanation": "Ngày 2/9/1945 tại Ba Đình, Bác Hồ đọc Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa."
        }
    ],
    "Viet Bac": [
        {
            "question": "Chiến dịch Việt Bắc Thu - Đông đập tan cuộc tấn công của Pháp diễn ra vào năm nào?",
            "options": ["1945", "1947", "1950", "1954"],
            "answer": 1,
            "explanation": "Chiến thắng Việt Bắc Thu - Đông 1947 đã bảo vệ vững chắc cơ quan đầu não kháng chiến."
        }
    ],
    "Dien Bien Phu": [
        {
            "question": "Chiến dịch Điện Biên Phủ kết thúc thắng lợi hoàn toàn vào ngày nào?",
            "options": ["19/08/1945", "02/09/1945", "07/05/1954", "20/07/1954"],
            "answer": 2,
            "explanation": "Chiến dịch Điện Biên Phủ toàn thắng ngày 7/5/1954, 'lừng lẫy năm châu, chấn động địa cầu'."
        }
    ],
    "Dinh Doc Lap": [
        {
            "question": "Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam vào ngày nào?",
            "options": ["30/04/1975", "26/03/1975", "01/05/1975", "02/09/1975"],
            "answer": 0,
            "explanation": "11h30 ngày 30/4/1975, lá cờ cách mạng tung bay trên nóc Dinh Độc Lập, đánh dấu Chiến dịch Hồ Chí Minh toàn thắng."
        }
    ],
    "Hien Luong - Quang Tri": [
        {
            "question": "Hiệp định Genève năm 1954 lấy con sông nào làm giới tuyến quân sự tạm thời?",
            "options": ["Sông Bến Hải (Vĩ tuyến 17)", "Sông Gianh", "Sông Hương", "Sông Thạch Hãn"],
            "answer": 0,
            "explanation": "Hiệp định Genève 1954 quy định lấy sông Bến Hải (vĩ tuyến 17) làm giới tuyến quân sự tạm thời."
        }
    ],
    "Ha Noi 1972": [
        {
            "question": "Trận Điện Biên Phủ trên không đánh bại pháo đài bay B-52 diễn ra trong bao nhiêu ngày đêm?",
            "options": ["12 ngày đêm", "7 ngày đêm", "20 ngày đêm", "55 ngày đêm"],
            "answer": 0,
            "explanation": "Chiến thắng Điện Biên Phủ trên không 12 ngày đêm (18/12 - 30/12/1972) buộc Mỹ phải ký Hiệp định Paris 1973."
        }
    ]
}

# Dung khi mot dia diem chua co cau hoi rieng
DEFAULT_QUESTIONS = [
    {
        "question": "Giai đoạn lịch sử trong trò chơi này bắt đầu từ năm nào?",
        "options": ["1911", "1914", "1930", "1945"],
        "answer": 1,
        "explanation": "Trò chơi tái hiện lịch sử hào hùng của dân tộc Việt Nam giai đoạn 1914 - 1975."
    }
]


class DeductionScene:
    """Man hinh suy luan.

    handle_event tra ve:
      "completed" -> vua tra loi dung het cau hoi cua dia diem (main se danh dau hoan thanh)
      "map"       -> nguoi choi muon ve ban do sau khi hoan thanh
    """

    def __init__(self, questions=None):
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 21)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 28, bold=True)

        self.questions_bank = questions if questions is not None else QUESTIONS
        self.location = None
        self.score = 0
        self.questions = DEFAULT_QUESTIONS
        self.question_index = 0
        self.finished = False
        self.last_answer_correct = None
        self.last_answer_recorded = None
        self.feedback = "Chọn đáp án đúng (bấm chuột hoặc nhấn phím 1-4)."

        self.retry_button = pygame.Rect(850, 590, 190, 46)
        self.map_button = pygame.Rect(850, 535, 190, 46)

    # ------------------------------------------------------------
    def set_location(self, location):
        self.location = location
        self.questions = self.questions_bank.get(location["name"], DEFAULT_QUESTIONS)
        self.restart()

    def restart(self):
        self.question_index = 0
        self.finished = False
        self.last_answer_correct = None
        self.last_answer_recorded = None
        self.feedback = "Chọn đáp án đúng (bấm chuột hoặc nhấn phím 1-4)."

    def choose(self, index):
        """Nguoi choi chon dap an so `index`."""
        if self.finished:
            return None

        question = self.questions[self.question_index]

        if not 0 <= index < len(question["options"]):
            return None

        if index != question["answer"]:
            self.last_answer_correct = False
            self.feedback = "Chưa chính xác! Hãy đọc lại manh mối và thử lại."
            return None

        self.last_answer_correct = True
        self.feedback = "Chính xác! " + question["explanation"]

        if self.question_index < len(self.questions) - 1:
            self.question_index += 1
            return "correct_question"

        self.finished = True
        self.feedback += " Địa điểm đã hoàn thành - nhấn ENTER để về bản đồ."
        return "completed"

    # ------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "map" if self.finished else None

            if pygame.K_1 <= event.key <= pygame.K_4:
                return self.choose(event.key - pygame.K_1)

            return None

        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        x, y = event.pos
        question = self.questions[self.question_index]

        if not self.finished:
            for index in range(len(question["options"])):
                button_y = 300 + index * 65

                if 150 <= x <= 850 and button_y <= y <= button_y + 48:
                    return self.choose(index)

        if self.finished and self.map_button.collidepoint(event.pos):
            return "map"

        if self.retry_button.collidepoint(event.pos):
            self.restart()

        return None

    def wrap_text(self, text, max_length=75):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()

            if len(candidate) > max_length:
                if current:
                    lines.append(current)
                current = word
            else:
                current = candidate

        if current:
            lines.append(current)

        return lines

    def draw_wrapped(self, screen, text, rect, font, color=DARK, max_lines=None):
        words = str(text).split()
        lines, current = [], ""
        for word in words:
            # Split even a single overlong word so it cannot escape the text box.
            chunks = []
            chunk = ""
            for char in word:
                if chunk and font.size(chunk + char)[0] > rect.width:
                    chunks.append(chunk)
                    chunk = char
                else:
                    chunk += char
            if chunk:
                chunks.append(chunk)
            for part in chunks:
                candidate = f"{current} {part}".strip()
                if current and font.size(candidate)[0] > rect.width:
                    lines.append(current)
                    current = part
                else:
                    current = candidate
        if current:
            lines.append(current)
        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while last and font.size(last + "…")[0] > rect.width:
                last = last[:-1]
            lines[-1] = last.rstrip() + "…"
        old_clip = screen.get_clip()
        screen.set_clip(rect)
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, color), (rect.x, rect.y + i * font.get_linesize()))
        screen.set_clip(old_clip)

    def draw(self, screen):
        screen.fill(BACKGROUND)

        title = self.title_font.render("SUY LUẬN & ÔN TẬP LỊCH SỬ", True, RED)
        screen.blit(title, (60, 35))

        score_box = pygame.Rect(790, 32, 215, 46)
        pygame.draw.rect(screen, WHITE, score_box, border_radius=10)
        pygame.draw.rect(screen, GREEN, score_box, 2, border_radius=10)
        score_text = self.font.render(f"Điểm : {self.score}", True, GREEN)
        screen.blit(score_text, score_text.get_rect(center=score_box.center))

        if getattr(self, "last_score_delta", 0) > 0 and self.last_answer_correct:
            plus_badge = self.font.render(f"+{self.last_score_delta}", True, (35, 155, 70))
            screen.blit(plus_badge, (score_box.right + 10, score_box.y + 10))

        name = (self.location.get("display_name") or self.location.get("name", "")) if self.location else ""
        total = max(1, len(self.questions))
        shown = total if self.finished else self.question_index + 1
        info = self.small_font.render(
            f"Địa điểm: {name}  |  Câu hỏi: {shown}/{total}  (+30 điểm/câu)",
            True,
            DARK
        )
        screen.blit(info, (60, 85))

        question = self.questions[min(self.question_index, total - 1)] if self.questions else {
            "question": "Chưa có câu hỏi cho địa điểm này.", "options": ["Quay lại bản đồ"], "answer": 0
        }

        pygame.draw.rect(screen, WHITE, (60, 130, 980, 130), border_radius=12)

        self.draw_wrapped(screen, question["question"], pygame.Rect(90, 150, 920, 90), self.font, max_lines=3)

        for index, option in enumerate(question["options"]):
            button_y = 300 + index * 65
            if button_y + 48 > 555:
                break

            pygame.draw.rect(
                screen, WHITE, (150, button_y, 700, 48), border_radius=8
            )
            pygame.draw.rect(
                screen, GRAY, (150, button_y, 700, 48), width=2, border_radius=8
            )

            self.draw_wrapped(screen, f"{index + 1}. {option}", pygame.Rect(175, button_y + 6, 650, 38), self.font, max_lines=2)

        pygame.draw.rect(screen, WHITE, (60, 570, 760, 76), border_radius=10)
        self.draw_wrapped(screen, self.feedback, pygame.Rect(80, 580, 720, 56), self.small_font, GREEN, max_lines=3)

        pygame.draw.rect(screen, RED, self.retry_button, border_radius=8)
        retry_text = self.small_font.render("Làm lại", True, WHITE)
        screen.blit(retry_text, (self.retry_button.centerx - retry_text.get_width() // 2, self.retry_button.centery - retry_text.get_height() // 2))

        if self.finished:
            pygame.draw.rect(screen, GREEN, self.map_button, border_radius=8)
            map_text = self.small_font.render("Về bản đồ (ENTER)", True, WHITE)
            screen.blit(map_text, (self.map_button.centerx - map_text.get_width() // 2, self.map_button.centery - map_text.get_height() // 2))

        hint = self.small_font.render("1-4: Chọn đáp án  |  ESC: Quay lại điều tra  |  Q: Thoát", True, DARK)
        screen.blit(hint, (60, 670))
