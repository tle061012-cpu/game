import os
import math
import pygame

# Mau sac
BACKGROUND = (245, 239, 220)
RED = (180, 35, 45)
DARK = (50, 45, 40)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
GRAY = (190, 185, 175)
BLUE = (60, 110, 160)
GOLD = (224, 168, 50)
SEA = (216, 246, 255)
LAND = (234, 214, 170)
LAND_EDGE = (140, 100, 60)

# Mau theo trang thai dia diem
COLOR_LOCKED = (140, 140, 140)   # chua mo khoa
COLOR_OPEN = GOLD                # co the kham pha
COLOR_DONE = GREEN               # da hoan thanh

# Khung ban do tren man hinh (x, y, rong, cao)
MAP_RECT = (40, 145, 700, 430)

# Duong vien Viet Nam don gian hoa (kinh do, vi do), theo chieu kim dong ho.
# Day la hinh minh hoa chu S, khong phai ban do dia ly chinh xac.
VIETNAM_OUTLINE = [
    (102.15, 22.40), (102.55, 22.75), (103.00, 22.45), (103.90, 22.50),
    (104.40, 22.80), (105.00, 23.20), (105.45, 23.35), (106.00, 22.95),
    (106.70, 22.85), (107.40, 22.00), (108.05, 21.53),
    (107.60, 21.35), (107.00, 20.95), (106.80, 20.70), (106.60, 20.35),
    (106.20, 20.00), (105.90, 19.85), (105.85, 19.30), (105.70, 18.80),
    (106.10, 18.30), (106.50, 17.60), (107.10, 16.90), (107.60, 16.40),
    (108.20, 16.10), (108.90, 15.10), (109.20, 13.80), (109.30, 13.00),
    (109.20, 12.20), (109.00, 11.50), (108.10, 10.90), (107.10, 10.40),
    (106.90, 10.30), (106.60, 9.90), (106.10, 9.50), (105.40, 8.65),
    (104.80, 8.60), (104.80, 9.20), (105.05, 9.90), (104.50, 10.40),
    (105.00, 10.90), (105.80, 11.60), (106.40, 11.70), (106.80, 11.80),
    (107.50, 12.30), (107.55, 13.20), (107.50, 14.40), (107.20, 15.20),
    (107.30, 16.15), (106.70, 16.90), (105.60, 17.90), (105.00, 18.60),
    (104.20, 19.10), (104.00, 19.70), (104.60, 20.30), (104.40, 20.80),
    (103.80, 21.30), (103.10, 21.90), (102.80, 22.30),
]


def project(lon, lat):
    """Doi (kinh do, vi do) sang toa do (x, y) tren man hinh."""
    x = 250 + (lon - 102.0) * 24.0
    y = 170 + (23.6 - lat) * 26.0
    return int(x), int(y)


class MapScene:
    def __init__(self, locations=None, db_status=""):
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 15)
        self.small_bold = pygame.font.SysFont("segoeui,arial,timesnewroman", 15, bold=True)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 30, bold=True)

        self.selected_year = 1914
        self.selected_location = None
        self.dragging = False

        # main.py se gan tap ten cac dia diem da hoan thanh vao day
        self.completed = set()
        self.quest_manager = None
        self.animation_time = 0.0
        self.message = ""
        self.db_status = db_status
        self.player_name = ""
        self.score = 0
        self.show_leaderboard = False
        self.show_inventory = False
        self.inventory_page = 0
        self.investigation_data = {}
        # Thanh công cụ nằm ngang trên cùng
        self.leaderboard_btn = pygame.Rect(720, 6, 160, 32)
        self.inventory_btn = pygame.Rect(895, 6, 155, 32)

        # Tai hinh anh ban do thuc te
        self.map_img_x = 240
        self.map_img_y = 147
        self.map_img_w = 304
        self.map_img_h = 426
        self.map_image = None

        map_path = os.path.join(os.path.dirname(__file__), "..", "bando.jpg")
        if os.path.exists(map_path):
            raw_img = pygame.image.load(map_path)
            self.map_image = pygame.transform.smoothscale(raw_img, (self.map_img_w, self.map_img_h))

        # Lấy dữ liệu địa điểm trực tiếp từ database (không dùng mock fallback)
        if locations is not None:
            self.locations = locations
        else:
            from services.game_data_service import game_data_service
            self.locations = game_data_service.get_locations_from_db()

        for location in self.locations:
            if "x" not in location or "y" not in location:
                location["x"], location["y"] = project(location.get("lon", 105.0), location.get("lat", 21.0))

        self.outline = [project(lon, lat) for lon, lat in VIETNAM_OUTLINE]

    # ------------------------------------------------------------
    # TRANG THAI DIA DIEM
    # ------------------------------------------------------------
    def status(self, location):
        """Tra ve "done", "open" hoac "locked".

        Mot dia diem chi duoc mo khoa khi moi dia diem o cac giai doan
        truoc do (start nho hon) da hoan thanh.
        """
        if self.quest_manager:
            quest_status = self.quest_manager.state(location)
            if quest_status == "completed":
                return "done"
            if quest_status == "locked":
                if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
                    return "open"
                return "locked"
            return "open"

        if location["name"] in self.completed:
            return "done"

        # Nếu đã hoàn thành Ba Đình thì luôn mở khóa Điện Biên Phủ
        if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
            return "open"

        for other in self.locations:
            if other["start"] < location["start"] and other["name"] not in self.completed:
                if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
                    continue
                return "locked"

        return "open"

    def in_year(self, location):
        return location["start"] <= self.selected_year <= location["end"]

    # ------------------------------------------------------------
    # VE
    # ------------------------------------------------------------
    def draw_text(self, screen, text, x, y, font, color=DARK):
        image = font.render(text, True, color)
        screen.blit(image, (x, y))

    def draw_label(self, screen, location, bold, occupied=None):
        font = self.small_bold if bold else self.small_font
        label_text = location.get("display_name") or location.get("name", "")
        original_name = label_text.split(" (")[0] if " (" in label_text else label_text
        short_name = original_name
        available_width = 210
        while short_name and font.size(short_name)[0] > available_width:
            short_name = short_name[:-1]
        if short_name != original_name:
            short_name = short_name.rstrip() + "…"
        image = font.render(short_name, True, DARK)
        width, height = image.get_size()

        # Try several nearby positions to prevent dense historical locations
        # from drawing their labels on top of one another.
        preferred_right = location.get("side", "r") == "r"
        base_y = location["y"] - height // 2 + location.get("dy", 0)
        offsets = [0, -24, 24, -44, 44, -62, 62, -82, 82, -104, 104, -128, 128]
        candidates = []
        for offset in offsets:
            for right in (preferred_right, not preferred_right):
                x = location["x"] + 14 if right else location["x"] - 14 - width
                y = base_y + offset
                rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
                if rect.left < MAP_RECT[0] + 4 or rect.right > MAP_RECT[0] + MAP_RECT[2] - 4:
                    continue
                if rect.top < MAP_RECT[1] + 4 or rect.bottom > MAP_RECT[1] + MAP_RECT[3] - 4:
                    continue
                if not any(rect.colliderect(other) for other in (occupied or [])):
                    candidates.append((rect, x, y))
                    break
            if candidates:
                break
        if not candidates:
            # Keep label visible even in crowded clusters by placing compactly
            # close to its marker; panel clip prevents screen overflow.
            # Search the panel for the closest non-overlapping slot rather than
            # stacking labels on the dense northern markers.
            slots = []
            for y in range(MAP_RECT[1] + 6, MAP_RECT[1] + MAP_RECT[3] - height - 6, 22):
                for x in range(MAP_RECT[0] + 6, MAP_RECT[0] + MAP_RECT[2] - width - 6, 12):
                    rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
                    if not any(rect.colliderect(other) for other in (occupied or [])):
                        slots.append((abs(y - base_y) + abs(x - location["x"]), rect, x, y))
            if slots:
                _, rect, x, y = min(slots, key=lambda slot: slot[0])
            else:
                x = min(max(location["x"] + 14, MAP_RECT[0] + 4), MAP_RECT[0] + MAP_RECT[2] - width - 12)
                y = min(max(base_y, MAP_RECT[1] + 4), MAP_RECT[1] + MAP_RECT[3] - height - 8)
                rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
        else:
            rect, x, y = candidates[0]
        if occupied is not None:
            occupied.append(rect)
        location["label_rect"] = rect

        box = pygame.Surface((width + 8, height + 4), pygame.SRCALPHA)
        box.fill((255, 255, 255, 220))
        pygame.draw.rect(box, (180, 180, 180), box.get_rect(), 1)
        screen.blit(box, (x - 4, y - 2))
        screen.blit(image, (x, y))

    def draw_map_panel(self, screen):
        panel = pygame.Rect(MAP_RECT)
        old_clip = screen.get_clip()

        # Bien
        pygame.draw.rect(screen, SEA, panel, border_radius=15)
        screen.set_clip(panel)

        # Ve ban do thuc te bando.jpg neu co
        if self.map_image:
            screen.blit(self.map_image, (self.map_img_x, self.map_img_y))
            pygame.draw.rect(
                screen, (180, 205, 220),
                (self.map_img_x, self.map_img_y, self.map_img_w, self.map_img_h),
                1
            )
        else:
            # Dat lien Viet Nam du phong (hinh chu S)
            pygame.draw.polygon(screen, LAND, self.outline)
            pygame.draw.polygon(screen, LAND_EDGE, self.outline, 2)

            grey_blue = (90, 120, 150)
            self.draw_text(screen, "BIỂN ĐÔNG", 430, 420, self.small_bold, grey_blue)
            self.draw_text(screen, "Q.đ Hoàng Sa (VN)", 440, 340, self.small_font, grey_blue)
            self.draw_text(screen, "Q.đ Trường Sa (VN)", 440, 520, self.small_font, grey_blue)
            self.draw_text(screen, "LÀO", 232, 345, self.small_font, (120, 130, 140))
            self.draw_text(screen, "CAMPUCHIA", 255, 466, self.small_font, (120, 130, 140))

        # Cac diem dia danh
        for location in self.locations:
            status = self.status(location)
            active = self.in_year(location)

            if status == "done":
                color = COLOR_DONE
            elif status == "open":
                color = COLOR_OPEN
            else:
                color = COLOR_LOCKED

            pulse = (1.0 + math.sin(self.animation_time * 3.2)) * 0.5
            radius = (10 if active else 7) + (int(pulse * 3) if status == "open" else 0)
            position = (location["x"], location["y"])

            if status == "open":
                halo_radius = radius + 5 + int(pulse * 3)
                halo = pygame.Surface((halo_radius * 2 + 2, halo_radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    halo, (*color, max(20, 65 - int(pulse * 30))),
                    (halo_radius + 1, halo_radius + 1), halo_radius, 2
                )
                screen.blit(halo, (position[0] - halo_radius - 1, position[1] - halo_radius - 1))

            pygame.draw.circle(screen, color, position, radius)
            pygame.draw.circle(screen, WHITE, position, radius, 2)

            if status == "done":
                x, y = position
                pygame.draw.lines(
                    screen, WHITE, False,
                    [(x - 4, y), (x - 1, y + 4), (x + 5, y - 4)], 2
                )

            # Danh dau dia diem dang duoc chon
            if location == self.selected_location:
                pygame.draw.circle(screen, BLUE, position, 17, 3)

        # Ve ten sau cung de khong bi cham tron che
        occupied_labels = []
        for location in sorted(self.locations, key=lambda item: item == self.selected_location):
            self.draw_label(
                screen, location,
                bold=(location == self.selected_location or self.in_year(location)),
                occupied=occupied_labels,
            )

        screen.set_clip(old_clip)
        pygame.draw.rect(screen, GREEN, panel, width=3, border_radius=15)

        self.draw_text(screen, "BẢN ĐỒ", 60, 158, self.font, GREEN)

        self.draw_legend(screen)

    def draw_legend(self, screen):
        # Use the empty right side of the map panel instead of covering labels.
        x = 555
        y = 205
        legend_rect = pygame.Rect(x - 12, y - 10, 165, 172)
        pygame.draw.rect(screen, WHITE, legend_rect, border_radius=10)
        pygame.draw.rect(screen, (180, 205, 220), legend_rect, 1, border_radius=10)

        self.draw_text(screen, "Chú giải", x, y, self.small_bold, DARK)

        items = [
            (COLOR_LOCKED, "Chưa mở khóa"),
            (COLOR_OPEN, "Có thể khám phá"),
            (COLOR_DONE, "Đã hoàn thành"),
        ]

        for index, (color, text) in enumerate(items):
            cy = y + 32 + index * 26
            pygame.draw.circle(screen, color, (x + 9, cy), 8)
            pygame.draw.circle(screen, WHITE, (x + 9, cy), 8, 2)
            self.draw_text(screen, text, x + 26, cy - 8, self.small_font)

        done = len(self.completed)
        self.draw_text(
            screen, f"Tiến độ: {done}/{len(self.locations)}",
            x, y + 125, self.small_bold, GREEN
        )

    def draw_timeline(self, screen):
        slider_x = 280
        slider_y = 605
        slider_width = 560

        pygame.draw.line(
            screen, GRAY,
            (slider_x, slider_y),
            (slider_x + slider_width, slider_y),
            8
        )

        ratio = (self.selected_year - 1914) / 61
        knob_x = slider_x + int(ratio * slider_width)

        pygame.draw.line(
            screen, RED,
            (slider_x, slider_y),
            (knob_x, slider_y),
            8
        )

        pygame.draw.circle(screen, RED, (knob_x, slider_y), 12)

        self.draw_text(screen, "1914", slider_x - 15, slider_y + 12, self.small_font)
        self.draw_text(
            screen, "1975",
            slider_x + slider_width - 20, slider_y + 12,
            self.small_font
        )

        self.draw_text(
            screen,
            f"Năm đang chọn: {self.selected_year}",
            450, 568,
            self.font, RED
        )

        if self.quest_manager:
            states = {"completed": "✓", "available": "●", "investigating": "◉", "quiz": "?", "locked": "○"}
            timeline = self.quest_manager.timeline()
            x = 285
            spacing = min(92, 560 // max(1, len(timeline)))
            for item in timeline:
                self.draw_text(
                    screen, f"{states[item['state']]} {item['year']}", x, 634,
                    self.small_font, GREEN if item["state"] == "completed" else RED
                )
                x += spacing

    def wrap(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()

            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def draw_information(self, screen):
        panel_x = 770
        panel_y = 180

        pygame.draw.rect(
            screen, WHITE,
            (panel_x, panel_y, 290, 350),
            border_radius=12
        )

        pygame.draw.rect(
            screen, GRAY,
            (panel_x, panel_y, 290, 350),
            width=2,
            border_radius=12
        )

        self.draw_text(
            screen, "THÔNG TIN ĐỊA DANH",
            panel_x + 20, panel_y + 18,
            self.small_bold, RED
        )

        if self.selected_location is None:
            y = panel_y + 85

            for line in self.wrap(
                "Hãy bấm vào một địa điểm trên bản đồ để xem thông tin.",
                self.small_font, 250
            ):
                self.draw_text(screen, line, panel_x + 20, y, self.small_font)
                y += 24

            if self.message:
                y += 10
                for line in self.wrap(self.message, self.small_font, 250):
                    self.draw_text(screen, line, panel_x + 20, y, self.small_font, RED)
                    y += 24
            return

        location = self.selected_location
        status = self.status(location)

        display_name = location.get("display_name") or location.get("name", "")
        name_lines = self.wrap(display_name, self.small_bold, 250)
        name_y = panel_y + 58
        for line in name_lines[:2]:
            self.draw_text(screen, line, panel_x + 20, name_y, self.small_bold, GREEN)
            name_y += 21

        if "event_time" in location and location["event_time"]:
            self.draw_text(
                screen,
                f"Thời gian: {location['event_time']}",
                panel_x + 20, name_y + 2,
                self.small_bold, RED
            )

        self.draw_text(
            screen,
            f"Giai đoạn: {location['start']} - {location['end']}",
            panel_x + 20, name_y + 25,
            self.small_font
        )

        y = name_y + 51

        desc_lines = self.wrap(location.get("description", ""), self.small_font, 250)
        for line in desc_lines[:5]:
            self.draw_text(screen, line, panel_x + 20, y, self.small_font)
            y += 23

        status_text = {
            "done": ("Đã hoàn thành - ENTER: xem lại", COLOR_DONE),
            "open": ("Có thể khám phá - ENTER: điều tra", RED),
            "locked": ("Chưa mở khóa", COLOR_LOCKED),
        }[status]

        self.draw_text(
            screen, status_text[0],
            panel_x + 20, panel_y + 285,
            self.small_bold, status_text[1]
        )

        self.draw_text(
            screen, "D: Suy luận (cần đủ manh mối)",
            panel_x + 20, panel_y + 312,
            self.small_font, DARK
        )

    # ------------------------------------------------------------
    # SU KIEN
    # ------------------------------------------------------------
    def year_from_mouse(self, mouse_x):
        slider_x = 280
        slider_width = 560

        ratio = (mouse_x - slider_x) / slider_width
        ratio = max(0, min(1, ratio))

        return round(1914 + ratio * (1975 - 1914))

    # ------------------------------------------------------------
    # VECTOR ICONS GRAPHICS HELPERS
    # ------------------------------------------------------------
    def draw_vector_trophy(self, surface, cx, cy, size=16, color=(255, 215, 0)):
        """Vẽ biểu tượng Cúp Vàng vector sắc nét (không phụ thuộc font emoji)."""
        base_w, base_h = int(size * 0.9), max(3, int(size * 0.22))
        pygame.draw.rect(surface, color, (cx - base_w // 2, cy + int(size * 0.35), base_w, base_h), border_radius=2)
        stem_w, stem_h = max(2, int(size * 0.25)), int(size * 0.32)
        pygame.draw.rect(surface, color, (cx - stem_w // 2, cy + int(size * 0.1), stem_w, stem_h))
        top_w = int(size * 0.9)
        bot_w = int(size * 0.45)
        top_y = cy - int(size * 0.5)
        bot_y = cy + int(size * 0.12)
        cup_poly = [
            (cx - top_w // 2, top_y),
            (cx + top_w // 2, top_y),
            (cx + bot_w // 2, bot_y),
            (cx - bot_w // 2, bot_y),
        ]
        pygame.draw.polygon(surface, color, cup_poly)
        arc_r = max(4, int(size * 0.4))
        pygame.draw.arc(surface, color, (cx - top_w // 2 - arc_r // 2, top_y + 1, arc_r, arc_r), 1.57, 4.71, 2)
        pygame.draw.arc(surface, color, (cx + top_w // 2 - arc_r // 2, top_y + 1, arc_r, arc_r), 4.71, 1.57, 2)
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - top_w // 2, top_y - 1, top_w, 3), 1)

    def draw_vector_medal(self, surface, cx, cy, rank=1):
        """Vẽ huy chương vàng / bạc / đồng vector với dải ruy-băng."""
        pygame.draw.polygon(surface, (200, 35, 45), [(cx - 6, cy - 10), (cx - 2, cy - 1), (cx - 7, cy + 2)])
        pygame.draw.polygon(surface, (40, 85, 160), [(cx + 6, cy - 10), (cx + 2, cy - 1), (cx + 7, cy + 2)])
        if rank == 1:
            bg_col = (255, 210, 30)
            edge_col = (210, 160, 20)
            text_col = (110, 75, 5)
        elif rank == 2:
            bg_col = (215, 220, 225)
            edge_col = (165, 170, 180)
            text_col = (60, 65, 75)
        else:
            bg_col = (210, 135, 60)
            edge_col = (160, 95, 35)
            text_col = (255, 255, 255)
        pygame.draw.circle(surface, bg_col, (cx, cy), 10)
        pygame.draw.circle(surface, edge_col, (cx, cy), 10, 2)
        r_surf = pygame.font.SysFont("segoeui,arial", 11, bold=True).render(str(rank), True, text_col)
        surface.blit(r_surf, r_surf.get_rect(center=(cx, cy)))

    def draw_vector_backpack(self, surface, cx, cy, size=16, color=(255, 255, 255)):
        """Vẽ biểu tượng Balo / Túi đồ vector sắc nét."""
        bw = int(size * 0.85)
        bh = int(size * 0.85)
        pygame.draw.rect(surface, color, (cx - bw // 2, cy - bh // 2 + 2, bw, bh), border_radius=3)
        pygame.draw.rect(surface, (230, 230, 230), (cx - bw // 2, cy - bh // 2 + 2, bw, max(3, bh // 3)), border_radius=2)
        pocket_w = max(4, int(bw * 0.65))
        pocket_h = max(3, int(bh * 0.35))
        pygame.draw.rect(surface, (200, 205, 215), (cx - pocket_w // 2, cy + 1, pocket_w, pocket_h), border_radius=2)
        handle_w = max(4, int(bw * 0.5))
        handle_h = max(3, int(bh * 0.3))
        pygame.draw.arc(surface, color, (cx - handle_w // 2, cy - bh // 2 - handle_h // 2, handle_w, handle_h), 0, 3.14, 2)

    def draw_vector_scroll(self, surface, cx, cy, color=(255, 255, 255)):
        """Vẽ biểu tượng cuộn văn kiện / tài liệu."""
        pygame.draw.rect(surface, color, (cx - 5, cy - 6, 10, 12), border_radius=1)
        pygame.draw.line(surface, (100, 100, 100), (cx - 3, cy - 3), (cx + 3, cy - 3), 1)
        pygame.draw.line(surface, (100, 100, 100), (cx - 3, cy), (cx + 3, cy), 1)
        pygame.draw.line(surface, (100, 100, 100), (cx - 3, cy + 3), (cx + 1, cy + 3), 1)

    def draw_vector_relic(self, surface, cx, cy, color=(255, 255, 255)):
        """Vẽ biểu tượng bình cổ / hiện vật."""
        pygame.draw.ellipse(surface, color, (cx - 5, cy - 5, 10, 10))
        pygame.draw.rect(surface, color, (cx - 3, cy - 7, 6, 3))
        pygame.draw.rect(surface, color, (cx - 4, cy + 4, 8, 2))

    def draw_vector_chat(self, surface, cx, cy, color=(255, 255, 255)):
        """Vẽ biểu tượng bong bóng hội thoại / lời khai."""
        pygame.draw.rect(surface, color, (cx - 6, cy - 5, 12, 9), border_radius=2)
        pygame.draw.polygon(surface, color, [(cx - 2, cy + 4), (cx + 2, cy + 4), (cx - 4, cy + 7)])

    def load_leaderboard(self):
        """Tải dữ liệu Bảng vàng học giả từ MySQL XAMPP hoặc file cache API."""
        leaderboard = []

        # 1. Truy vấn trực tiếp từ MySQL (đầy đủ các tài khoản: hocsinh01, tea, 123,...)
        try:
            from data.db_queries import get_db_connection
            conn, _ = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT u.ma_nguoi_dung, u.ten_dang_nhap, u.ho_va_ten, 
                               COALESCE(t.diem_tri_thuc, 0) AS score,
                               COALESCE(t.nam_mo_khoa_cao_nhat, 1914) AS max_year
                        FROM nguoi_dung u
                        LEFT JOIN tien_do_choi t ON u.ma_nguoi_dung = t.ma_nguoi_dung
                        ORDER BY score DESC, u.ma_nguoi_dung ASC
                        LIMIT 10;
                    """)
                    rows = cur.fetchall()
                    for r in rows:
                        name = r.get("ho_va_ten") or r.get("ten_dang_nhap") or f"Học giả #{r.get('ma_nguoi_dung')}"
                        leaderboard.append({
                            "user_id": str(r.get("ma_nguoi_dung")),
                            "username": r.get("ten_dang_nhap", ""),
                            "user_name": name,
                            "score": int(r.get("score") or 0),
                            "max_year": int(r.get("max_year") or 1914)
                        })
                conn.close()
        except Exception:
            pass

        # 2. Nếu MySQL chưa bật hoặc lỗi kết nối, nạp từ file JSON cache
        if not leaderboard:
            import json
            import os
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "api_progress_db.json"
            )
            if os.path.exists(db_path):
                try:
                    with open(db_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        lb = data.get("leaderboard", [])
                        lb.sort(key=lambda x: x.get("score", 0), reverse=True)
                        leaderboard = lb[:10]
                except Exception:
                    pass

        # 3. Đảm bảo người chơi hiện tại (ví dụ 'Lee Tea' hoặc 'tea') luôn có mặt
        cur_name = getattr(self, "player_name", "") or ""
        if cur_name:
            found = False
            for item in leaderboard:
                if (item.get("user_name", "").strip().lower() == cur_name.strip().lower() or
                    item.get("username", "").strip().lower() == cur_name.strip().lower()):
                    item["score"] = max(item.get("score", 0), getattr(self, "score", 0))
                    found = True
                    break
            if not found:
                leaderboard.append({
                    "user_id": "current",
                    "username": cur_name,
                    "user_name": cur_name,
                    "score": getattr(self, "score", 0)
                })

        # Sắp xếp lại theo điểm giảm dần
        leaderboard.sort(key=lambda x: x.get("score", 0), reverse=True)
        return leaderboard[:10]

    def draw_leaderboard_modal(self, screen):
        """Hiển thị hộp thoại Bảng vàng Top học giả điểm cao (Leaderboard Popup)."""
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((15, 12, 10, 180))
        screen.blit(overlay, (0, 0))

        # Cửa sổ chính giữa
        box_w, box_h = 580, 500
        box_x = (width - box_w) // 2
        box_y = (height - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(screen, (253, 249, 238), box_rect, border_radius=12)
        pygame.draw.rect(screen, (195, 145, 30), box_rect, 3, border_radius=12)

        # Header bảng vàng
        header_rect = pygame.Rect(box_x, box_y, box_w, 55)
        pygame.draw.rect(screen, (175, 32, 42), header_rect, border_top_left_radius=12, border_top_right_radius=12)

        # Vẽ biểu tượng Cúp Vàng trên header
        self.draw_vector_trophy(screen, box_x + 35, box_y + 27, size=18, color=(255, 235, 120))
        t_title = self.small_bold.render("BẢNG VÀNG DANH DỰ HỌC GIẢ LỊCH SỬ VIỆT NAM", True, (255, 255, 255))
        screen.blit(t_title, (box_x + 60, box_y + 18))

        # Nút đóng [X]
        close_btn = pygame.Rect(box_x + box_w - 42, box_y + 12, 30, 30)
        pygame.draw.rect(screen, (190, 45, 50), close_btn, border_radius=6)
        x_surf = self.small_bold.render("✕", True, (255, 255, 255))
        screen.blit(x_surf, x_surf.get_rect(center=close_btn.center))

        # Danh sách top
        items = self.load_leaderboard()
        start_y = box_y + 68

        # Cột tiêu đề
        col_rank = self.small_bold.render("HẠNG", True, (115, 110, 100))
        col_name = self.small_bold.render("TÊN HỌC GIẢ", True, (115, 110, 100))
        col_score = self.small_bold.render("ĐIỂM SỐ", True, (115, 110, 100))
        screen.blit(col_rank, (box_x + 32, start_y))
        screen.blit(col_name, (box_x + 130, start_y))
        screen.blit(col_score, (box_x + 465, start_y))
        pygame.draw.line(screen, (215, 205, 185), (box_x + 20, start_y + 24), (box_x + box_w - 20, start_y + 24), 1)

        row_y = start_y + 32
        cur_name = getattr(self, "player_name", "").strip().lower()

        for i, item in enumerate(items, 1):
            is_me = (item.get("user_name", "").strip().lower() == cur_name or
                     item.get("username", "").strip().lower() == cur_name)

            if is_me:
                bg_col = (255, 244, 215)
                border_col = (195, 145, 30)
                border_w = 2
            elif i == 1:
                bg_col = (255, 248, 228)
                border_col = (230, 200, 140)
                border_w = 1
            elif i <= 3:
                bg_col = (255, 251, 242)
                border_col = (230, 220, 200)
                border_w = 1
            else:
                bg_col = (255, 255, 255)
                border_col = (230, 225, 215)
                border_w = 1

            row_rect = pygame.Rect(box_x + 20, row_y, box_w - 40, 36)
            pygame.draw.rect(screen, bg_col, row_rect, border_radius=6)
            pygame.draw.rect(screen, border_col, row_rect, border_w, border_radius=6)

            # Huy chương / Badge hạng
            cx_medal = box_x + 48
            cy_medal = row_y + 18
            if i == 1:
                self.draw_vector_medal(screen, cx_medal, cy_medal, rank=1)
            elif i == 2:
                self.draw_vector_medal(screen, cx_medal, cy_medal, rank=2)
            elif i == 3:
                self.draw_vector_medal(screen, cx_medal, cy_medal, rank=3)
            else:
                r_surf = self.small_bold.render(f"#{i}", True, (120, 115, 110))
                screen.blit(r_surf, r_surf.get_rect(center=(cx_medal, cy_medal)))

            # Tên học giả
            name_str = item.get("user_name", "Ẩn danh")[:24]
            name_col = (165, 35, 45) if is_me else (45, 40, 35)
            n_surf = self.small_bold.render(name_str, True, name_col)
            screen.blit(n_surf, (box_x + 115, row_y + 8))

            # Nhãn [BẠN] nếu là tài khoản người chơi hiện tại
            if is_me:
                tag_surf = pygame.font.SysFont("segoeui,arial", 11, bold=True).render("[BẠN]", True, (45, 125, 80))
                screen.blit(tag_surf, (box_x + 120 + n_surf.get_width() + 8, row_y + 10))

            # Điểm số
            sc_surf = self.small_bold.render(f"{item.get('score', 0)} đ", True, (175, 32, 42))
            screen.blit(sc_surf, (box_x + 465, row_y + 8))

            row_y += 40

        # Footer hướng dẫn
        hint_surf = self.small_font.render("Nhấn phím [L], [ESC] hoặc click [✕] để đóng Bảng vàng", True, (120, 115, 110))
        screen.blit(hint_surf, hint_surf.get_rect(center=(box_x + box_w // 2, box_y + box_h - 22)))

    def get_all_collected_clues_details(self):
        """Truy xuất danh sách chi tiết toàn bộ manh mối đã thu thập được."""
        collected_ids = set()
        if self.quest_manager and hasattr(self.quest_manager, "collected_clues"):
            for loc_name, ids in self.quest_manager.collected_clues.items():
                collected_ids.update(ids)

        results = []
        inv_data = getattr(self, "investigation_data", {}) or {}

        for loc in self.locations:
            loc_name = loc.get("name", "")
            disp_name = loc.get("display_name") or loc_name
            is_loc_completed = (loc_name in self.completed)

            loc_clues = inv_data.get(loc_name, {}).get("clues", [])
            for clue in loc_clues:
                cid = clue.get("id")
                if cid in collected_ids or is_loc_completed:
                    results.append({
                        "id": cid,
                        "title": clue.get("name") or clue.get("title", "Manh mối"),
                        "detail": clue.get("detail", "Nội dung chứng cứ lịch sử."),
                        "kind": clue.get("kind", "Văn kiện"),
                        "source": clue.get("source", "Hồ sơ Di tích Lịch sử Quốc gia"),
                        "location": disp_name,
                        "is_completed": is_loc_completed,
                    })

        # Fallback nếu địa điểm đã hoàn thành nhưng danh sách manh mối trống
        if not results and self.completed:
            for loc_name in self.completed:
                results.append({
                    "id": f"done_{loc_name}",
                    "title": f"Hồ sơ giải mã: {loc_name}",
                    "detail": f"Đã hoàn thành xuất sắc toàn bộ nhiệm vụ và điều tra tư liệu tại {loc_name}.",
                    "kind": "Văn kiện",
                    "source": "Ban Thẩm định Lịch sử",
                    "location": loc_name,
                    "is_completed": True,
                })
        return results

    def draw_inventory_modal(self, screen):
        """Hiển thị hộp thoại Túi đồ manh mối & Hiện vật đã thu thập (Inventory Modal)."""
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((15, 12, 10, 190))
        screen.blit(overlay, (0, 0))

        box_w, box_h = 780, 520
        box_x = (width - box_w) // 2
        box_y = (height - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(screen, (253, 249, 238), box_rect, border_radius=12)
        pygame.draw.rect(screen, (195, 145, 30), box_rect, 3, border_radius=12)

        # Header Túi đồ
        header_rect = pygame.Rect(box_x, box_y, box_w, 52)
        pygame.draw.rect(screen, (40, 95, 150), header_rect, border_top_left_radius=12, border_top_right_radius=12)
        self.draw_vector_backpack(screen, box_x + 35, box_y + 26, size=18, color=(255, 255, 255))
        t_title = self.small_bold.render("TÚI ĐỒ HỌC GIẢ — BỘ SƯU TẬP MANH MỐI & HIỆN VẬT", True, (255, 255, 255))
        screen.blit(t_title, (box_x + 58, box_y + 16))

        # Nút đóng [X]
        close_btn = pygame.Rect(box_x + box_w - 42, box_y + 10, 32, 32)
        pygame.draw.rect(screen, (180, 40, 45), close_btn, border_radius=6)
        x_txt = self.small_bold.render("✕", True, (255, 255, 255))
        screen.blit(x_txt, x_txt.get_rect(center=close_btn.center))

        # Danh sách manh mối
        clues = self.get_all_collected_clues_details()
        items_per_page = 4
        total_pages = max(1, (len(clues) + items_per_page - 1) // items_per_page)
        self.inventory_page = max(0, min(self.inventory_page, total_pages - 1))

        # Thanh trạng thái phụ
        sub_bar = pygame.Rect(box_x, box_y + 52, box_w, 32)
        pygame.draw.rect(screen, (240, 234, 218), sub_bar)
        pygame.draw.line(screen, (215, 205, 185), (box_x, box_y + 84), (box_x + box_w, box_y + 84), 1)
        sub_txt = self.small_font.render(f"Tổng số manh mối đã thu thập: {len(clues)} tư liệu  |  Phân loại: Lời khai, Văn kiện, Hiện vật", True, (75, 70, 65))
        screen.blit(sub_txt, (box_x + 25, box_y + 60))

        if not clues:
            empty_msg1 = self.small_bold.render("Túi đồ của bạn hiện đang trống.", True, (175, 35, 45))
            empty_msg2 = self.small_font.render("Hãy chọn một địa danh đang mở khóa trên bản đồ và nhấn ENTER để tiến hành điều tra!", True, (90, 85, 80))
            screen.blit(empty_msg1, empty_msg1.get_rect(center=(box_x + box_w // 2, box_y + 200)))
            screen.blit(empty_msg2, empty_msg2.get_rect(center=(box_x + box_w // 2, box_y + 235)))
        else:
            page_clues = clues[self.inventory_page * items_per_page : (self.inventory_page + 1) * items_per_page]
            start_item_y = box_y + 95

            for idx, c in enumerate(page_clues):
                item_y = start_item_y + idx * 88
                item_rect = pygame.Rect(box_x + 22, item_y, box_w - 44, 80)
                pygame.draw.rect(screen, (255, 255, 255), item_rect, border_radius=8)
                pygame.draw.rect(screen, (222, 214, 198), item_rect, 1, border_radius=8)

                # Badge loại manh mối
                kind_raw = str(c.get("kind", "Văn kiện")).lower()
                if "văn" in kind_raw or "kiện" in kind_raw:
                    badge_color = (40, 95, 150)
                    badge_label = "VĂN KIỆN"
                elif "hiện" in kind_raw or "vật" in kind_raw:
                    badge_color = (195, 145, 30)
                    badge_label = "HIỆN VẬT"
                elif "lời" in kind_raw or "khai" in kind_raw:
                    badge_color = (130, 55, 140)
                    badge_label = "LỜI KHAI"
                else:
                    badge_color = (45, 125, 80)
                    badge_label = "TƯ LIỆU"

                badge_rect = pygame.Rect(box_x + 32, item_y + 8, 92, 20)
                pygame.draw.rect(screen, badge_color, badge_rect, border_radius=4)
                if "văn" in kind_raw or "kiện" in kind_raw:
                    self.draw_vector_scroll(screen, badge_rect.left + 10, badge_rect.centery, color=(255, 255, 255))
                elif "hiện" in kind_raw or "vật" in kind_raw:
                    self.draw_vector_relic(screen, badge_rect.left + 10, badge_rect.centery, color=(255, 255, 255))
                elif "lời" in kind_raw or "khai" in kind_raw:
                    self.draw_vector_chat(screen, badge_rect.left + 10, badge_rect.centery, color=(255, 255, 255))
                else:
                    self.draw_vector_scroll(screen, badge_rect.left + 10, badge_rect.centery, color=(255, 255, 255))
                badge_surf = pygame.font.SysFont("segoeui,arial", 10, bold=True).render(badge_label, True, (255, 255, 255))
                screen.blit(badge_surf, (badge_rect.left + 22, badge_rect.centery - badge_surf.get_height() // 2))

                # Tiêu đề manh mối
                t_surf = self.small_bold.render(c.get("title", "Manh mối"), True, (45, 40, 35))
                screen.blit(t_surf, (box_x + 134, item_y + 8))

                # Địa danh thu thập
                loc_txt = f"📍 {c.get('location', '')}"
                loc_surf = self.small_font.render(loc_txt, True, (120, 115, 110))
                screen.blit(loc_surf, (box_x + box_w - 240, item_y + 8))

                # Nội dung chi tiết
                detail_str = c.get("detail", "")
                if len(detail_str) > 85:
                    detail_str = detail_str[:85] + "..."
                d_surf = self.small_font.render(detail_str, True, (55, 50, 45))
                screen.blit(d_surf, (box_x + 32, item_y + 32))

                # Nguồn sử liệu
                src_str = f"📚 Nguồn: {c.get('source', 'Sử liệu chính thống')}"
                if len(src_str) > 90:
                    src_str = src_str[:90] + "..."
                s_surf = self.small_font.render(src_str, True, (40, 95, 150))
                screen.blit(s_surf, (box_x + 32, item_y + 54))

        # Footer phân trang & hướng dẫn
        footer_y = box_y + box_h - 48
        pygame.draw.line(screen, (220, 212, 195), (box_x + 20, footer_y), (box_x + box_w - 20, footer_y), 1)

        # Nút chuyển trang
        prev_rect = pygame.Rect(box_x + 30, footer_y + 8, 115, 30)
        next_rect = pygame.Rect(box_x + box_w - 145, footer_y + 8, 115, 30)
        pygame.draw.rect(screen, (240, 235, 222), prev_rect, border_radius=6)
        pygame.draw.rect(screen, (215, 205, 185), prev_rect, 1, border_radius=6)
        pygame.draw.rect(screen, (240, 235, 222), next_rect, border_radius=6)
        pygame.draw.rect(screen, (215, 205, 185), next_rect, 1, border_radius=6)

        prev_txt = self.small_font.render("◀ Trang trước", True, (60, 55, 50))
        next_txt = self.small_font.render("Trang sau ▶", True, (60, 55, 50))
        screen.blit(prev_txt, prev_txt.get_rect(center=prev_rect.center))
        screen.blit(next_txt, next_txt.get_rect(center=next_rect.center))

        page_str = f"Trang {self.inventory_page + 1} / {total_pages}  (Phím Lên/Xuống hoặc cuộn chuột)"
        p_surf = self.small_font.render(page_str, True, (110, 105, 100))
        screen.blit(p_surf, p_surf.get_rect(center=(box_x + box_w // 2, footer_y + 22)))

    def handle_event(self, event):
        # 1. Đang mở hộp thoại Túi đồ
        if self.show_inventory:
            clues = self.get_all_collected_clues_details()
            total_pages = max(1, (len(clues) + 3) // 4)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_t, pygame.K_i):
                    self.show_inventory = False
                    return
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    self.inventory_page = max(0, self.inventory_page - 1)
                    return
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    self.inventory_page = min(total_pages - 1, self.inventory_page + 1)
                    return

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.inventory_page = max(0, self.inventory_page - 1)
                elif event.y < 0:
                    self.inventory_page = min(total_pages - 1, self.inventory_page + 1)
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                width, height = pygame.display.get_surface().get_size()
                box_w, box_h = 780, 520
                box_x = (width - box_w) // 2
                box_y = (height - box_h) // 2

                # Nút [X] đóng
                close_btn = pygame.Rect(box_x + box_w - 42, box_y + 10, 32, 32)
                if close_btn.collidepoint((mx, my)):
                    self.show_inventory = False
                    return

                # Nút chuyển trang
                footer_y = box_y + box_h - 48
                prev_rect = pygame.Rect(box_x + 30, footer_y + 8, 115, 30)
                next_rect = pygame.Rect(box_x + box_w - 145, footer_y + 8, 115, 30)
                if prev_rect.collidepoint((mx, my)):
                    self.inventory_page = max(0, self.inventory_page - 1)
                    return
                elif next_rect.collidepoint((mx, my)):
                    self.inventory_page = min(total_pages - 1, self.inventory_page + 1)
                    return

                # Click ra ngoài hộp thoại -> đóng
                box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
                if not box_rect.collidepoint((mx, my)):
                    self.show_inventory = False
                return

        # 2. Đang mở hộp thoại Bảng vàng
        if self.show_leaderboard:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.show_leaderboard = False
                return

        # 3. Phím tắt mở Bảng vàng hoặc Túi đồ
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                self.show_leaderboard = not self.show_leaderboard
                self.show_inventory = False
                return
            elif event.key in (pygame.K_t, pygame.K_i):
                self.show_inventory = not self.show_inventory
                self.show_leaderboard = False
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Click nút Bảng vàng trên thanh công cụ
            if self.leaderboard_btn.collidepoint((mouse_x, mouse_y)):
                self.show_leaderboard = not self.show_leaderboard
                self.show_inventory = False
                return

            # Click nút Túi đồ trên thanh công cụ
            if self.inventory_btn.collidepoint((mouse_x, mouse_y)):
                self.show_inventory = not self.show_inventory
                self.show_leaderboard = False
                return

            # Bam vao thanh thoi gian
            if 265 <= mouse_x <= 855 and abs(mouse_y - 605) <= 20:
                self.dragging = True
                self.selected_year = self.year_from_mouse(mouse_x)
                self.selected_location = None
                self.message = ""

            # Bam vao dia diem (kiem tra ca cham tron va khung chu ten dia danh)
            for location in self.locations:
                distance_x = mouse_x - location["x"]
                distance_y = mouse_y - location["y"]
                hit_pin = (distance_x ** 2 + distance_y ** 2 <= 20 ** 2)
                hit_label = bool(location.get("label_rect") and location["label_rect"].collidepoint(mouse_x, mouse_y))

                if hit_pin or hit_label:
                    if self.status(location) == "locked":
                        self.selected_location = None
                        self.message = "Địa điểm chưa mở khóa. Hãy hoàn thành các giai đoạn trước."
                    else:
                        self.selected_location = location
                        self.message = ""

                        # Dua thanh thoi gian ve dung giai doan cua dia diem
                        if not self.in_year(location):
                            self.selected_year = location["start"]
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.selected_year = self.year_from_mouse(event.pos[0])
            self.selected_location = None

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def draw(self, screen, dt=1 / 60):
        self.animation_time += min(max(dt, 0.0), 0.05)
        screen.fill(BACKGROUND)
        width, height = screen.get_size()

        # =========================================================
        # 1. THANH CÔNG CỤ NẰM NGANG TRÊN CÙNG (TOP TOOL BAR)
        # =========================================================
        top_bar_rect = pygame.Rect(0, 0, width, 44)
        pygame.draw.rect(screen, (242, 235, 218), top_bar_rect)
        pygame.draw.line(screen, (212, 202, 180), (0, 44), (width, 44), 2)

        # Nhãn nhận diện bên trái thanh công cụ
        tool_label = self.small_bold.render("🏛️ SỬ HỌC TOÀN KHOA — BẢN ĐỒ TIẾN TRÌNH", True, (165, 35, 45))
        screen.blit(tool_label, (25, 12))

        # Cập nhật tọa độ 2 nút nằm ngay ngắn trên thanh công cụ
        self.leaderboard_btn = pygame.Rect(width - 340, 6, 155, 32)
        self.inventory_btn = pygame.Rect(width - 175, 6, 155, 32)

        # Nút Bảng Vàng (L)
        pygame.draw.rect(screen, (195, 145, 30), self.leaderboard_btn, border_radius=6)
        self.draw_vector_trophy(screen, self.leaderboard_btn.left + 20, self.leaderboard_btn.centery, size=15, color=(255, 245, 160))
        btn_lb_txt = self.small_bold.render("BẢNG VÀNG (L)", True, (255, 255, 255))
        screen.blit(btn_lb_txt, (self.leaderboard_btn.left + 35, self.leaderboard_btn.centery - btn_lb_txt.get_height() // 2))

        # Nút Túi Đồ (T)
        pygame.draw.rect(screen, (40, 95, 150), self.inventory_btn, border_radius=6)
        self.draw_vector_backpack(screen, self.inventory_btn.left + 20, self.inventory_btn.centery, size=15, color=(255, 255, 255))
        btn_inv_txt = self.small_bold.render("TÚI ĐỒ (T)", True, (255, 255, 255))
        screen.blit(btn_inv_txt, (self.inventory_btn.left + 35, self.inventory_btn.centery - btn_inv_txt.get_height() // 2))

        # =========================================================
        # 2. TIÊU ĐỀ CHÍNH NẰM DƯỚI THANH CÔNG CỤ (HOÀN TOÀN KHÔNG BỊ CHE)
        # =========================================================
        title = self.title_font.render("HÀNH TRÌNH LỊCH SỬ VIỆT NAM (1914 - 1975)", True, RED)
        screen.blit(title, (width // 2 - title.get_width() // 2, 56))

        # Hiển thị trạng thái kết nối Cơ sở dữ liệu (MySQL / Offline Cache)
        if self.db_status:
            status_color = GREEN if "Connected" in self.db_status else (160, 130, 40)
            self.draw_text(screen, f"[{self.db_status}]", 40, 110, self.small_bold, status_color)

        # Hiển thị thông tin người chơi & Điểm số từ bảng tien_do_choi
        if self.player_name:
            player_info_str = f"Người chơi: {self.player_name}  |  Điểm: {self.score}"
            self.draw_text(screen, player_info_str, 720, 110, self.small_bold, BLUE)

        self.draw_map_panel(screen)
        self.draw_information(screen)
        self.draw_timeline(screen)

        # =========================================================
        # 3. HIỂN THỊ CÁC MODAL DIALOGS
        # =========================================================
        if self.show_leaderboard:
            self.draw_leaderboard_modal(screen)

        if self.show_inventory:
            self.draw_inventory_modal(screen)
