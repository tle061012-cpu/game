
import pygame

BACKGROUND = (245, 239, 220)
RED = (180, 35, 45)
DARK = (50, 45, 40)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
GOLD = (210, 160, 55)
GRAY = (210, 205, 195)


class InvestigationScene:
    def __init__(self, investigation_data=None):
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 21)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 28, bold=True)

        self.location = None
        self.message = "Hãy đọc tư liệu và thu thập manh mối lịch sử."
        self.collected_clues = set()
        self.evidence_options = {}
        self.active_evidence_index = None
        self.dialogue_pages = []
        self.dialogue_page = 0

        # Đổ dữ liệu vào: nếu có dữ liệu từ Service/MySQL thì lấy, ngược lại dùng fallback
        if investigation_data:
            self.investigation_data = investigation_data
        else:
            self.investigation_data = {
            "Ben Nha Rong": {
                "event": "Hanh trinh tim duong cuu nuoc",
                "year": "1911",
                "witness": "Nguoi dan cang",
                "dialogue": (
                    "Toi van nho nhung con tau roi ben cang. "
                    "Day la noi gan voi hanh trinh ra di cua "
                    "Nguyen Tat Thanh nam 1911."
                ),
                "clues": [
                    {
                        "id": "ben_1",
                        "name": "Thong tin ve ben cang",
                        "detail": "Ben Nha Rong nam tai Sai Gon."
                    },
                    {
                        "id": "ben_2",
                        "name": "Moc thoi gian 1911",
                        "detail": "Nguyen Tat Thanh roi Viet Nam nam 1911."
                    }
                ]
            },
            "Hong Kong": {
                "event": "Thanh lap Dang Cong san Viet Nam",
                "year": "1930",
                "witness": "Nguoi lien lac",
                "dialogue": (
                    "Nhieu to chuc cong san da duoc hop nhat "
                    "duoi su chu tri cua Nguyen Ai Quoc vao nam 1930."
                ),
                "clues": [
                    {
                        "id": "hk_1",
                        "name": "Moc thoi gian 1930",
                        "detail": "Su kien thanh lap Dang dien ra nam 1930."
                    },
                    {
                        "id": "hk_2",
                        "name": "Vai tro chu tri",
                        "detail": "Nguyen Ai Quoc chu tri hoi nghi hop nhat."
                    }
                ]
            },
            "Vinh - Ben Thuy": {
                "event": "Phong trao cach mang 1930-1931",
                "year": "1930-1931",
                "witness": "Nguoi dan dia phuong",
                "dialogue": (
                    "Vinh va Ben Thuy la mot trong nhung dia ban "
                    "noi bat cua phong trao cach mang 1930-1931."
                ),
                "clues": [
                    {
                        "id": "vinh_1",
                        "name": "Dia ban phong trao",
                        "detail": "Vinh - Ben Thuy gan voi phong trao 1930-1931."
                    }
                ]
            },
            "Pac Bo": {
                "event": "Nguyen Ai Quoc tro ve Viet Nam",
                "year": "1941",
                "witness": "Can bo cach mang",
                "dialogue": (
                    "Pac Bo gan voi su kien Nguyen Ai Quoc tro ve "
                    "Viet Nam dau nam 1941."
                ),
                "clues": [
                    {
                        "id": "pacbo_1",
                        "name": "Moc thoi gian 1941",
                        "detail": "Nguyen Ai Quoc tro ve Viet Nam nam 1941."
                    },
                    {
                        "id": "pacbo_2",
                        "name": "Dia diem Pac Bo",
                        "detail": "Pac Bo thuoc Cao Bang."
                    }
                ]
            },
            "Tan Trao": {
                "event": "Chuan bi Tong khoi nghia",
                "year": "1945",
                "witness": "Can bo Viet Minh",
                "dialogue": (
                    "Tan Trao la dia diem quan trong trong qua trinh "
                    "chuan bi Tong khoi nghia Thang Tam."
                ),
                "clues": [
                    {
                        "id": "tant_1",
                        "name": "Tan Trao",
                        "detail": "Tan Trao gan voi qua trinh chuan bi Tong khoi nghia."
                    }
                ]
            },
            "Ba Dinh": {
                "event": "Doc Tuyen ngon Doc lap",
                "year": "1945",
                "witness": "Nguoi dan Ha Noi",
                "dialogue": (
                    "Ngay 2 thang 9 nam 1945, Chu tich Ho Chi Minh "
                    "doc Tuyen ngon Doc lap tai Quang truong Ba Dinh."
                ),
                "clues": [
                    {
                        "id": "badinh_1",
                        "name": "Ngay 2-9-1945",
                        "detail": "Tuyen ngon Doc lap duoc doc ngay 2-9-1945."
                    }
                ]
            },
            "Viet Bac": {
                "event": "Can cu dia khang chien",
                "year": "1946-1950",
                "witness": "Nguoi dan Viet Bac",
                "dialogue": (
                    "Viet Bac la can cu dia quan trong cua cuoc "
                    "khang chien chong thuc dan Phap."
                ),
                "clues": [
                    {
                        "id": "vietbac_1",
                        "name": "Can cu Viet Bac",
                        "detail": "Viet Bac giu vai tro quan trong trong khang chien."
                    }
                ]
            },
            "Dien Bien Phu": {
                "event": "Chien dich Dien Bien Phu",
                "year": "1954",
                "witness": "Nguoi dan cong hoa tuyen",
                "dialogue": (
                    "Chien dich Dien Bien Phu ket thuc thang loi "
                    "ngay 7 thang 5 nam 1954."
                ),
                "clues": [
                    {
                        "id": "dbp_1",
                        "name": "Ngay 7-5-1954",
                        "detail": "Chien dich Dien Bien Phu ket thuc thang loi ngay 7-5-1954."
                    },
                    {
                        "id": "dbp_2",
                        "name": "Ket qua chien dich",
                        "detail": "Chien thang tao buoc ngoat quan trong trong cuoc khang chien."
                    }
                ]
            }
        }

    def set_location(self, location):
        self.location = location
        self.message = "Hoàn thành các mục tiêu bên dưới để thu thập manh mối."
        self.active_evidence_index = None
        self.evidence_options = {}
        data = self.investigation_data.get(location["name"], {})
        dialogue = data.get("dialogue", "")
        if isinstance(dialogue, (list, tuple)):
            full_text = " ".join(str(line) for line in dialogue)
        else:
            full_text = str(dialogue)
        lines = self.wrap_text(full_text, max_length=70)
        self.dialogue_pages = [" ".join(lines[i:i + 3]) for i in range(0, len(lines), 3)] or [""]
        self.dialogue_page = 0
        clues = data.get("clues", [])
        for index, clue in enumerate(clues):
            # Use evidence from other locations as plausible distractors.
            distractors = []
            for other_location, other_data in self.investigation_data.items():
                if other_location == location["name"]:
                    continue
                for other_clue in other_data.get("clues", []):
                    candidate = other_clue.get("name", "")
                    if candidate and candidate != clue.get("name") and candidate not in distractors:
                        distractors.append(candidate)
                    if len(distractors) == 2:
                        break
                if len(distractors) == 2:
                    break
            while len(distractors) < 2:
                distractors.append("Tài liệu không trùng khớp với sự kiện này")
            options = [clue["name"], *distractors]
            # Stable deterministic shuffle to avoid always placing the correct item first.
            correct_index = (index + len(location.get("name", ""))) % len(options)
            options[0], options[correct_index] = options[correct_index], options[0]
            self.evidence_options[index] = {
                "options": options,
                "correct_index": correct_index,
                "attempts": 0,
                "hint": clue.get("detail", "Đối chiếu tên tư liệu với sự kiện đang điều tra."),
            }

    def quest_objectives(self):
        """Return actionable objectives; each objective rewards one clue."""
        if not self.location:
            return []
        data = self.investigation_data.get(self.location["name"], {})
        return [
            {
                "clue": clue,
                "complete": clue["id"] in self.collected_clues,
                "objective": (
                    "Đã hoàn thành - manh mối đã ghi vào nhật ký"
                    if clue["id"] in self.collected_clues
                    else clue.get("objective", "Đối chiếu tư liệu với lời kể của nhân chứng")
                ),
            }
            for clue in data.get("clues", [])
        ]

    def draw_text(self, screen, text, x, y, font, color=DARK):
        image = font.render(text, True, color)
        screen.blit(image, (x, y))

    def draw_wrapped(self, screen, text, rect, font, color=DARK, line_gap=3, max_lines=None):
        """Render text wrapped by actual pixel width and clipped to its area."""
        words = str(text).split()
        lines = []
        current = ""
        for word in words:
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
        line_height = font.get_linesize() + line_gap
        for index, line in enumerate(lines):
            screen.blit(font.render(line, True, color), (rect.x, rect.y + index * line_height))
        screen.set_clip(old_clip)
        return len(lines)

    def wrap_text(self, text, max_length=65):
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

    def is_complete(self, location=None):
        """True neu da thu thap du MANH MOI cua dia diem."""
        location = location or self.location

        if not location:
            return False

        data = self.investigation_data.get(location["name"])

        if not data:
            return False

        return all(c["id"] in self.collected_clues for c in data["clues"])

    def collect(self, index):
        """Open a clue's evidence challenge; do not award the clue yet."""
        if not self.location:
            return

        data = self.investigation_data.get(self.location["name"])

        if not data:
            self.message = "Chua co du lieu dieu tra cho dia diem nay."
            return

        if not 0 <= index < len(data["clues"]):
            return

        clue = data["clues"][index]

        if self.active_evidence_index is not None:
            self.message = "Hãy hoàn tất phần chọn bằng chứng trước."
            return

        if clue["id"] in self.collected_clues:
            self.message = "Bạn đã thu thập manh mối này rồi."
        else:
            self.active_evidence_index = index
            self.message = "Hãy chọn tư liệu liên quan đến sự kiện để nhận manh mối."

    def choose_evidence(self, option_index):
        if self.active_evidence_index is None or not self.location:
            return False
        index = self.active_evidence_index
        data = self.investigation_data.get(self.location["name"], {})
        clues = data.get("clues", [])
        if not 0 <= index < len(clues):
            return False
        challenge = self.evidence_options.get(index)
        if not challenge or not 0 <= option_index < len(challenge["options"]):
            return False
        challenge["attempts"] += 1
        clue = clues[index]
        if option_index == challenge["correct_index"]:
            self.collected_clues.add(clue["id"])
            self.active_evidence_index = None
            self.message = "Chính xác! Đã ghi vào nhật ký: " + clue["name"]
            if self.is_complete():
                self.message += ". Đã đủ manh mối - nhấn D để suy luận!"
            return True
        hint = challenge["hint"] if challenge["attempts"] >= 2 else "Chưa đúng. Hãy đọc lại lời nhân chứng và đối chiếu sự kiện, thời gian, địa điểm."
        self.message = "Bằng chứng chưa phù hợp. " + hint
        return False

    def handle_event(self, event):
        # Ban phim: phim 1-9 thu thap manh moi tuong ung
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                if self.dialogue_page < len(self.dialogue_pages) - 1:
                    self.dialogue_page += 1
                    return
            if self.active_evidence_index is not None:
                if pygame.K_1 <= event.key <= pygame.K_3:
                    self.choose_evidence(event.key - pygame.K_1)
                elif event.key == pygame.K_ESCAPE:
                    self.active_evidence_index = None
                    self.message = "Đã đóng phần đối chiếu tư liệu."
                return
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.collect(event.key - pygame.K_1)
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if not self.location:
            return

        mouse_x, mouse_y = event.pos
        if self.active_evidence_index is not None:
            for option_index in range(3):
                option_rect = pygame.Rect(355, 275 + option_index * 46, 390, 40)
                if option_rect.collidepoint(event.pos):
                    self.choose_evidence(option_index)
                    return
            if not pygame.Rect(340, 195, 420, 315).collidepoint(event.pos):
                self.active_evidence_index = None
                return
        data = self.investigation_data.get(self.location["name"])

        if not data:
            self.message = "Chưa có dữ liệu điều tra cho địa điểm này."
            return

        for index in range(len(data["clues"])):
            button_y = 420 + index * 65

            if 80 <= mouse_x <= 720 and button_y <= mouse_y <= button_y + 48:
                self.collect(index)
                return

    def draw(self, screen):
        screen.fill(BACKGROUND)

        self.draw_text(
            screen, "MÀN HÌNH ĐIỀU TRA & THU THẬP MANH MỐI",
            60, 35, self.title_font, RED
        )

        self.draw_text(
            screen, "ESC: Về bản đồ  |  D: Suy luận (khi đủ manh mối)  |  Q: Thoát",
            60, 80, self.small_font
        )

        if not self.location:
            self.draw_text(
                screen, "Chưa chọn địa điểm.",
                60, 150, self.font
            )
            return

        location_name = self.location.get("display_name") or self.location.get("name", "")
        data = self.investigation_data.get(self.location["name"])

        self.draw_text(
            screen, location_name,
            60, 135, self.title_font, GREEN
        )

        if not data:
            self.draw_text(
                screen,
                "Chưa có nội dung điều tra cho địa điểm này.",
                60, 190, self.font
            )
            return

        # Khung su kien
        pygame.draw.rect(
            screen, WHITE,
            (50, 185, 700, 210),
            border_radius=12
        )

        event_rect = pygame.Rect(75, 195, 650, 62)
        lines_count = self.draw_wrapped(screen, "Sự kiện: " + data["event"], event_rect, self.font, RED, max_lines=2)

        time_y = 195 + lines_count * (self.font.get_linesize() + 3) + 2
        self.draw_text(
            screen, "Thời gian: " + str(data.get("year", "")),
            75, time_y, self.small_font
        )

        # NPC dialogue panel
        npc_panel = pygame.Rect(50, 300, 700, 92)
        pygame.draw.rect(screen, (255, 252, 245), npc_panel, border_radius=10)
        pygame.draw.rect(screen, GOLD, npc_panel, 2, border_radius=10)
        pygame.draw.circle(screen, (218, 190, 145), (88, 346), 25)
        pygame.draw.circle(screen, DARK, (88, 337), 8)
        pygame.draw.arc(screen, DARK, pygame.Rect(76, 340, 24, 20), 0, 3.14, 2)
        self.draw_wrapped(
            screen, str(data.get("witness", "Nhân chứng lịch sử")),
            pygame.Rect(125, 307, 600, 22), self.small_font, GREEN, max_lines=1
        )
        page_text = self.dialogue_pages[self.dialogue_page] if self.dialogue_pages else str(data.get("dialogue", ""))
        self.draw_wrapped(
            screen, page_text, pygame.Rect(125, 332, 600, 48),
            self.small_font, DARK, max_lines=2
        )
        if self.dialogue_page < len(self.dialogue_pages) - 1:
            self.draw_text(screen, "Space / Enter: tiếp tục", 545, 369, self.small_font, RED)

        # Quest objectives; each completed objective awards its corresponding clue.
        self.draw_text(
            screen, "NHIỆM VỤ THU THẬP MANH MỐI",
            60, 400, self.font, RED
        )

        objectives = self.quest_objectives()
        for index, objective in enumerate(objectives):
            clue = objective["clue"]
            button_y = 420 + index * 65
            if button_y + 58 > screen.get_height() - 45:
                continue
            collected = objective["complete"]

            color = GREEN if collected else WHITE

            pygame.draw.rect(
                screen, color,
                (80, button_y, 640, 48),
                border_radius=8
            )

            pygame.draw.rect(
                screen, GRAY,
                (80, button_y, 640, 48),
                width=2,
                border_radius=8
            )

            prefix = (
                f"{index + 1}. [ĐÃ GHI] {clue['name']}"
                if collected else f"{index + 1}. [NHIỆM VỤ] Đối chiếu tư liệu"
            )

            self.draw_wrapped(
                screen, prefix + clue["name"], pygame.Rect(95, button_y + 5, 605, 22),
                self.small_font, WHITE if collected else DARK, max_lines=1
            )
            self.draw_wrapped(
                screen, objective["objective"], pygame.Rect(95, button_y + 27, 605, 22),
                self.small_font, WHITE if collected else GREEN, max_lines=1
            )

        if self.active_evidence_index is not None:
            challenge = self.evidence_options[self.active_evidence_index]
            clue = data["clues"][self.active_evidence_index]
            panel = pygame.Rect(340, 195, 420, 315)
            pygame.draw.rect(screen, (255, 252, 245), panel, border_radius=12)
            pygame.draw.rect(screen, GOLD, panel, 2, border_radius=12)
            self.draw_text(screen, "CHỌN BẰNG CHỨNG", 365, 206, self.font, RED)
            self.draw_wrapped(screen, "Tư liệu nào liên quan đến sự kiện đang điều tra?", pygame.Rect(365, 235, 370, 36), self.small_font, max_lines=2)
            for option_index, option in enumerate(challenge["options"]):
                rect = pygame.Rect(355, 275 + option_index * 46, 390, 40)
                pygame.draw.rect(screen, WHITE, rect, border_radius=7)
                pygame.draw.rect(screen, GRAY, rect, 1, border_radius=7)
                self.draw_wrapped(screen, f"{option_index + 1}. {option}", rect.inflate(-16, -6), self.small_font, DARK, max_lines=2)
            self.draw_wrapped(screen, "Sự kiện: " + data["event"], pygame.Rect(365, 418, 370, 48), self.small_font, GREEN, max_lines=2)
            self.draw_text(screen, "ESC: đóng | Chọn 1-3", 365, 474, self.small_font)

        # Khung thong bao
        pygame.draw.rect(
            screen, WHITE,
            (770, 185, 290, 280),
            border_radius=12
        )

        self.draw_text(
            screen, "NHẬT KÝ",
            795, 205, self.title_font, RED
        )

        self.draw_wrapped(screen, self.message, pygame.Rect(795, 255, 235, 85), self.small_font, max_lines=4)

        collected_here = sum(
            1 for c in data["clues"] if c["id"] in self.collected_clues
        )

        self.draw_text(
            screen,
            f"Manh mối đã thu thập: {collected_here}/{len(data['clues'])}",
            795, 365, self.small_font, GREEN
        )

        if self.active_evidence_index is not None:
            self.draw_wrapped(
                screen, self.message, pygame.Rect(795, 390, 235, 65),
                self.small_font, RED, max_lines=3
            )

        if self.is_complete():
            self.draw_text(
                screen,
                "Đã đủ manh mối! Nhấn D để suy luận.",
                795, 395, self.small_font, RED
            )
