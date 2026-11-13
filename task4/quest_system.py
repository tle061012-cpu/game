"""Reusable quest, clue inventory, timeline board and quiz components.

These classes are UI-light on purpose: a Scene Manager can own them and pass
Pygame events/draw surfaces without coupling quest rules to a particular scene.
Run ``python -m task4.quest_system`` from the project directory for the demo.
"""

from dataclasses import dataclass, asdict
from enum import Enum
import json
import math
import struct
import pygame

VIETNAMESE_FONT_FAMILY = "segoeui,arial,timesnewroman,tahoma"


class QuestState(str, Enum):
    LOCKED = "LOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    DEDUCTION_PHASE = "DEDUCTION_PHASE"
    COMPLETED = "COMPLETED"


class QuestStateMachine:
    """Validates progression; UI actions cannot skip required quest phases."""

    def __init__(self, required_clues):
        self.required_clues = set(required_clues)
        self.collected_clues = set()
        self.state = QuestState.LOCKED
        self.timeline_verified = False
        self.quiz_completed = False

    def start(self):
        if self.state == QuestState.LOCKED:
            self.state = QuestState.IN_PROGRESS
            return True
        return self.state != QuestState.COMPLETED

    def collect_clue(self, clue_id):
        if self.state != QuestState.IN_PROGRESS or clue_id not in self.required_clues:
            return False
        self.collected_clues.add(clue_id)
        if self.required_clues.issubset(self.collected_clues):
            self.state = QuestState.DEDUCTION_PHASE
        return True

    def complete_timeline(self, correct):
        if self.state != QuestState.DEDUCTION_PHASE:
            return False
        self.timeline_verified = bool(correct)
        return self.timeline_verified

    def complete(self):
        if (
            self.state != QuestState.DEDUCTION_PHASE
            or not self.timeline_verified
            or not self.quiz_completed
        ):
            return False
        self.state = QuestState.COMPLETED
        return True

    def mark_quiz_completed(self):
        """Allow quest completion only after the post-timeline quiz is done."""
        if self.state != QuestState.DEDUCTION_PHASE or not self.timeline_verified:
            return False
        self.quiz_completed = True
        return True


CLUE_TYPES = {"lời khai", "văn kiện", "hiện vật"}


@dataclass(frozen=True)
class Clue:
    """Historical clue. A non-empty source citation is mandatory."""

    id: str
    title: str
    kind: str
    detail: str
    source: str
    timeline_stage: int

    def __post_init__(self):
        if not self.id.strip() or not self.title.strip() or not self.detail.strip():
            raise ValueError("Clue cần có id, tiêu đề và nội dung chi tiết.")
        if self.kind not in CLUE_TYPES:
            raise ValueError(f"Loại clue phải thuộc: {sorted(CLUE_TYPES)}")
        if not self.source.strip():
            raise ValueError("Mỗi clue bắt buộc phải có nguồn trích dẫn lịch sử.")
        if self.timeline_stage not in range(4):
            raise ValueError("timeline_stage phải là 0, 1, 2 hoặc 3.")


class ClueInventory:
    """Stores unique clues and renders a simple selectable inventory list."""

    def __init__(self):
        self._clues = {}
        self.selected_id = None
        self.scroll = 0

    @property
    def clues(self):
        return list(self._clues.values())

    def add(self, clue):
        if not isinstance(clue, Clue):
            raise TypeError("Inventory chỉ nhận đối tượng Clue.")
        is_new = clue.id not in self._clues
        self._clues[clue.id] = clue
        return is_new

    def get(self, clue_id):
        return self._clues.get(clue_id)

    def draw(self, surface, rect, font=None, small_font=None, selected_id=None, placed_slots=None):
        """Draw inventory cards; returns clue card rectangles for drag logic."""
        if not pygame.font.get_init():
            pygame.font.init()
        font = font or pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 16, bold=True)
        small_font = small_font or pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 13)
        tag_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 11, bold=True)
        pygame.draw.rect(surface, (255, 252, 245), rect, border_radius=10)
        pygame.draw.rect(surface, (180, 185, 175), rect, 2, border_radius=10)
        surface.blit(font.render("TÚI ĐỒ - MẢNH GHÉP", True, (50, 45, 40)), (rect.x + 12, rect.y + 10))
        cards = {}
        y = rect.y + 42
        visible = self.clues[self.scroll:]
        placed_slots = placed_slots or {}
        for clue in visible:
            card = pygame.Rect(rect.x + 8, y, rect.w - 16, 52)
            if y + card.h > rect.bottom - 8:
                break
            is_selected = (clue.id == selected_id)
            is_placed = clue.id in placed_slots

            card_bg = (235, 247, 238) if is_placed else ((255, 248, 235) if is_selected else (255, 255, 255))
            pygame.draw.rect(surface, card_bg, card, border_radius=6)

            border_color = (235, 130, 20) if is_selected else ((45, 125, 80) if is_placed else (210, 205, 195))
            border_width = 2 if (is_selected or is_placed) else 1
            pygame.draw.rect(surface, border_color, card, border_width, border_radius=6)

            surface.blit(font.render(clue.title[:30], True, (50, 45, 40)), (card.x + 8, card.y + 5))
            surface.blit(small_font.render(f"{clue.kind} · Nguồn: {clue.source[:28]}", True, (90, 105, 95)), (card.x + 8, card.y + 28))

            if is_placed:
                slot_idx = placed_slots[clue.id]
                badge = tag_font.render(f"Đã đặt [Ô {slot_idx + 1}]", True, (45, 125, 80))
                badge_rect = badge.get_rect(right=card.right - 8, top=card.y + 6)
                surface.blit(badge, badge_rect)

            cards[clue.id] = card
            y += 58
        return cards

    def handle_event(self, event, rect, card_rects):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(max(0, len(self._clues) - 1), self.scroll - event.y))
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and rect.collidepoint(event.pos):
            self.selected_id = next((clue_id for clue_id, card in card_rects.items() if card.collidepoint(event.pos)), None)


class Task4SoundFX:
    """Procedural audio feedback for Task 4.

    Generates click, snap, success chime, and error tones without external file dependencies.
    Gracefully silences if audio device or mixer is unavailable.
    """
    _sounds = {}

    @classmethod
    def _create_tone(cls, frequency, duration=0.1, sample_rate=44100, volume=0.25):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
            init_freq, _, init_channels = pygame.mixer.get_init()
            total_samples = int(init_freq * duration)
            buf = bytearray()
            max_amp = int(32767 * volume)
            for i in range(total_samples):
                decay = 1.0 - (i / total_samples)
                sample = int(math.sin(2 * math.pi * frequency * i / init_freq) * max_amp * decay)
                sample_bytes = struct.pack("<h", sample)
                if init_channels == 2:
                    buf.extend(sample_bytes * 2)
                else:
                    buf.extend(sample_bytes)
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    @classmethod
    def get(cls, name):
        if name not in cls._sounds:
            try:
                if name == "snap":
                    cls._sounds[name] = cls._create_tone(880, duration=0.07, volume=0.18)
                elif name == "remove":
                    cls._sounds[name] = cls._create_tone(440, duration=0.08, volume=0.15)
                elif name == "success":
                    cls._sounds[name] = cls._create_tone(1174, duration=0.25, volume=0.25)
                elif name == "error":
                    cls._sounds[name] = cls._create_tone(220, duration=0.18, volume=0.2)
            except Exception:
                cls._sounds[name] = None
        return cls._sounds.get(name)

    @classmethod
    def play(cls, name):
        try:
            snd = cls.get(name)
            if snd:
                snd.play()
        except Exception:
            pass


TIMELINE_STAGES = (
    "Bối cảnh / Nguyên nhân",
    "Chủ trương / Hành động",
    "Diễn biến đỉnh điểm",
    "Kết quả / Ý nghĩa",
)


class DeductionTimelineBoard:
    """Four-slot drag/drop board with full swap, move, and remove capabilities."""

    def __init__(self, inventory, quest_machine):
        self.inventory = inventory
        self.quest_machine = quest_machine
        self.slots = [None] * 4
        self.dragging_id = None
        self.slot_rects = []
        self.remove_rects = []
        self.message = "Kéo mảnh ghép vào ô hoặc click chọn để đặt / đổi chỗ."
        self.verified = False
        self.shake_start = 0
        self.shake_until = 0

    def trigger_shake(self, duration_ms=350):
        try:
            now = pygame.time.get_ticks()
        except Exception:
            now = 0
        self.shake_start = now
        self.shake_until = now + duration_ms

    def place(self, clue_id, stage):
        """Đặt hoặc chuyển mảnh ghép vào ô; nếu ô đã có thì hoán đổi."""
        clue = self.inventory.get(clue_id)
        if clue is None or stage not in range(4):
            return False

        old_stage = next((i for i, cid in enumerate(self.slots) if cid == clue_id), None)
        target_clue = self.slots[stage]

        if old_stage is not None and old_stage != stage:
            # Hoán đổi giữa 2 ô
            self.slots[old_stage] = target_clue
            self.slots[stage] = clue_id
            if target_clue:
                self.message = f"Đã hoán đổi vị trí Ô {old_stage + 1} và Ô {stage + 1}."
            else:
                self.message = f"Đã chuyển mảnh ghép sang Ô {stage + 1}."
        else:
            if old_stage is not None and old_stage == stage:
                # Đang ở đúng ô này rồi
                pass
            else:
                # Đặt mới vào stage
                self.slots[stage] = clue_id
                self.message = f"Đã đặt vào Ô {stage + 1}. Kéo hoặc click để đổi chỗ bất cứ lúc nào."

        self.verified = False
        Task4SoundFX.play("snap")
        return True

    def swap(self, stage_a, stage_b):
        """Hoán đổi trực tiếp 2 ô timeline cho nhau."""
        if stage_a in range(4) and stage_b in range(4):
            if stage_a != stage_b:
                self.slots[stage_a], self.slots[stage_b] = self.slots[stage_b], self.slots[stage_a]
                self.verified = False
                self.message = f"Đã hoán đổi vị trí Ô {stage_a + 1} và Ô {stage_b + 1}."
                Task4SoundFX.play("snap")
                return True
        return False

    def remove(self, stage):
        """Gỡ mảnh ghép khỏi một ô timeline."""
        if stage in range(4) and self.slots[stage] is not None:
            removed = self.slots[stage]
            self.slots[stage] = None
            self.verified = False
            self.message = f"Đã gỡ mảnh ghép khỏi Ô {stage + 1}."
            Task4SoundFX.play("remove")
            return removed
        return None

    def reset(self):
        """Đặt lại toàn bộ 4 ô."""
        self.slots = [None] * 4
        self.verified = False
        self.message = "Đã đặt lại 4 ô. Bạn có thể sắp xếp lại từ đầu."
        Task4SoundFX.play("remove")

    def check(self):
        if any(clue_id is None for clue_id in self.slots):
            self.message = "Còn ô trống: hãy đặt đủ 4 mảnh ghép trước khi xác thực."
            self.trigger_shake()
            Task4SoundFX.play("error")
            return False
        correct = all(
            self.inventory.get(clue_id).timeline_stage == stage
            for stage, clue_id in enumerate(self.slots)
        )
        self.verified = self.quest_machine.complete_timeline(correct)
        if correct:
            self.message = "ĐÃ XÁC THỰC LỊCH SỬ! Nhấn Enter để tiếp tục."
            Task4SoundFX.play("success")
        else:
            self.message = "MÂU THUẪN LỊCH SỬ: thứ tự chưa đúng, hãy đổi lại vị trí các ô."
            self.trigger_shake()
            Task4SoundFX.play("error")
        return correct

    def draw(self, surface, rect, font=None, selected_stage=None, hover_stage=None):
        if not pygame.font.get_init():
            pygame.font.init()
        font = font or pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 15, bold=True)
        small_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 13)
        btn_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 13, bold=True)
        title_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 14, bold=True)

        now = 0
        try:
            now = pygame.time.get_ticks()
        except Exception:
            pass

        shake_x = 0
        if now < self.shake_until:
            shake_x = int(math.sin((now - self.shake_start) * 0.05) * 6)

        slot_rects = []
        remove_rects = []
        gap = 8
        width = (rect.w - gap * 3) // 4
        for stage, label in enumerate(TIMELINE_STAGES):
            slot = pygame.Rect(rect.x + stage * (width + gap) + shake_x, rect.y, width, rect.h)
            slot_rects.append(slot)
            clue = self.inventory.get(self.slots[stage]) if self.slots[stage] else None

            if self.verified:
                color = (225, 248, 230)
                pulse = int(math.sin(now * 0.007) * 20)
                border_color = (max(30, 45 + pulse), min(160, 125 + pulse), max(50, 80 + pulse))
                border_width = 3
            elif stage == selected_stage or stage == hover_stage:
                color = (255, 248, 232)
                pulse = int(math.sin(now * 0.008) * 25)
                border_color = (min(255, 235 + pulse), 130, 20)
                border_width = 3
            elif clue:
                color = (252, 252, 248)
                border_color = (130, 160, 140)
                border_width = 2
            else:
                color = (255, 252, 245)
                border_color = (195, 195, 185)
                border_width = 1

            pygame.draw.rect(surface, color, slot, border_radius=8)
            pygame.draw.rect(surface, border_color, slot, border_width, border_radius=8)

            heading = (
                ("1. Bối cảnh", "/ Nguyên nhân"),
                ("2. Chủ trương", "/ Hành động"),
                ("3. Diễn biến", "đỉnh điểm"),
                ("4. Kết quả", "/ Ý nghĩa"),
            )[stage]
            for line_index, line in enumerate(heading):
                surface.blit(font.render(line, True, (50, 45, 40)), (slot.x + 8, slot.y + 7 + line_index * 18))

            if clue:
                # Nút [×] ở góc trên bên phải
                x_rect = pygame.Rect(slot.right - 22, slot.y + 6, 16, 16)
                remove_rects.append(x_rect)
                pygame.draw.rect(surface, (235, 225, 220), x_rect, border_radius=4)
                x_text = btn_font.render("x", True, (180, 40, 40))
                surface.blit(x_text, x_text.get_rect(center=x_rect.center))

                # Hiển thị tên mảnh ghép tự động xuống dòng đẹp mắt
                words = clue.title.split()
                lines = []
                cur = ""
                for w in words:
                    cand = (cur + " " + w).strip()
                    if title_font.size(cand)[0] < width - 16:
                        cur = cand
                    else:
                        if cur:
                            lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                lines = lines[:3]

                for li, l_text in enumerate(lines):
                    surface.blit(title_font.render(l_text, True, (35, 95, 60)), (slot.x + 8, slot.y + 48 + li * 18))
            else:
                remove_rects.append(None)
                hint_empty = small_font.render("(Trống - Kéo/click để đặt)", True, (160, 155, 145))
                surface.blit(hint_empty, (slot.x + 8, slot.y + 55))

        if self.verified:
            stamp = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 24, bold=True).render("ĐÃ XÁC THỰC LỊCH SỬ", True, (45, 125, 80))
            surface.blit(stamp, stamp.get_rect(center=(rect.centerx + shake_x, rect.bottom + 24)))

        self.slot_rects = slot_rects
        self.remove_rects = remove_rects
        return slot_rects


class TimelineScene:
    """Scene Manager scene shell integrating inventory and timeline drag/drop with swap/replace support."""

    def __init__(self, inventory, board):
        self.inventory = inventory
        self.board = board
        self.inventory_rect = pygame.Rect(30, 80, 330, 500)
        self.board_rect = pygame.Rect(380, 160, 670, 155)
        self.card_rects = {}
        self.slot_rects = []
        self.remove_rects = []
        self.dragging_id = None
        self.drag_source_stage = None
        self.selected_clue_id = None
        self.selected_slot_stage = None
        self.score = 0
        self.mouse_pos = (0, 0)
        self.reset_btn_rect = pygame.Rect(785, 115, 130, 34)
        self.check_btn_rect = pygame.Rect(925, 115, 125, 34)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = event.pos

            # Chuột phải (button 3): Click vào ô nào gỡ ngay mảnh ghép ở ô đó
            if event.button == 3:
                for stage, s_rect in enumerate(self.slot_rects):
                    if s_rect.collidepoint(event.pos):
                        self.board.remove(stage)
                        self.selected_clue_id = None
                        self.selected_slot_stage = None
                        return
                return

            if event.button == 1:
                # 1. Bấm nút "Đặt lại các ô"
                if self.reset_btn_rect.collidepoint(event.pos):
                    self.board.reset()
                    self.selected_clue_id = None
                    self.selected_slot_stage = None
                    return

                # 2. Bấm nút "Kiểm tra timeline"
                if self.check_btn_rect.collidepoint(event.pos):
                    self.board.check()
                    return

                # 3. Bấm nút [×] gỡ bỏ trên các ô
                for stage, x_rect in enumerate(self.remove_rects):
                    if x_rect and x_rect.collidepoint(event.pos):
                        self.board.remove(stage)
                        self.selected_clue_id = None
                        self.selected_slot_stage = None
                        return

                # 4. Bấm vào một trong các ô Timeline
                for stage, s_rect in enumerate(self.slot_rects):
                    if s_rect.collidepoint(event.pos):
                        # Nếu người chơi ĐÃ chọn 1 mảnh ghép trước đó (Click-to-place / Click-to-swap mode)
                        if self.selected_clue_id is not None:
                            if self.selected_slot_stage is not None and self.selected_slot_stage != stage:
                                # Đang chọn từ ô khác -> Hoán đổi 2 ô
                                self.board.swap(self.selected_slot_stage, stage)
                            else:
                                # Đang chọn từ túi đồ hoặc cùng ô
                                self.board.place(self.selected_clue_id, stage)
                            self.selected_clue_id = None
                            self.selected_slot_stage = None
                            return

                        # Nếu chưa chọn gì trước đó: Bắt đầu kéo thả hoặc chọn ô này
                        if self.board.slots[stage] is not None:
                            self.dragging_id = self.board.slots[stage]
                            self.drag_source_stage = stage
                            self.selected_clue_id = self.board.slots[stage]
                            self.selected_slot_stage = stage
                        return

                # 5. Bấm vào mảnh ghép trong Túi đồ
                for clue_id, c_rect in self.card_rects.items():
                    if c_rect.collidepoint(event.pos):
                        self.dragging_id = clue_id
                        self.drag_source_stage = next((s for s, cid in enumerate(self.board.slots) if cid == clue_id), None)
                        self.selected_clue_id = clue_id
                        self.selected_slot_stage = self.drag_source_stage
                        return

                # Click ra ngoài vùng tương tác -> bỏ chọn
                self.selected_clue_id = None
                self.selected_slot_stage = None

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_pos = event.pos
            if self.dragging_id:
                # Kiểm tra xem thả chuột vào ô nào
                target_stage = next((i for i, r in enumerate(self.slot_rects) if r.collidepoint(event.pos)), None)

                if target_stage is not None:
                    if self.drag_source_stage is not None:
                        # Kéo từ 1 ô sang 1 ô: Hoán đổi nếu khác nhau
                        if self.drag_source_stage != target_stage:
                            self.board.swap(self.drag_source_stage, target_stage)
                            self.selected_clue_id = None
                            self.selected_slot_stage = None
                    else:
                        # Kéo từ túi đồ vào target_stage
                        self.board.place(self.dragging_id, target_stage)
                        self.selected_clue_id = None
                        self.selected_slot_stage = None
                else:
                    # Thả chuột RA NGOÀI các ô (ví dụ kéo ra túi đồ hoặc khoảng trống)
                    # Nếu mảnh ghép đang kéo vốn nằm ở một ô -> Gỡ bỏ mảnh ghép khỏi ô đó!
                    if self.drag_source_stage is not None:
                        src_rect = self.slot_rects[self.drag_source_stage]
                        if not src_rect.collidepoint(event.pos):
                            self.board.remove(self.drag_source_stage)
                            self.selected_clue_id = None
                            self.selected_slot_stage = None

                self.dragging_id = None
                self.drag_source_stage = None

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.board.check()
            elif event.key in (pygame.K_BACKSPACE, pygame.K_c, pygame.K_r, pygame.K_DELETE):
                self.board.reset()
                self.selected_clue_id = None
                self.selected_slot_stage = None
            elif pygame.K_1 <= event.key <= pygame.K_4 and self.selected_clue_id:
                target_stage = event.key - pygame.K_1
                if self.selected_slot_stage is not None and self.selected_slot_stage != target_stage:
                    self.board.swap(self.selected_slot_stage, target_stage)
                else:
                    self.board.place(self.selected_clue_id, target_stage)
                self.selected_clue_id = None
                self.selected_slot_stage = None

    def draw(self, surface):
        if not pygame.font.get_init():
            pygame.font.init()
        surface.fill((245, 239, 220))

        # 1. Bảng túi đồ bên trái
        placed_slots = {cid: idx for idx, cid in enumerate(self.board.slots) if cid is not None}
        self.card_rects = self.inventory.draw(
            surface, self.inventory_rect,
            selected_id=self.selected_clue_id,
            placed_slots=placed_slots
        )

        # 2. Tiêu đề và nút bấm công cụ phía trên bên phải
        title_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 20, bold=True)
        btn_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 14, bold=True)

        surface.blit(title_font.render("BÀN SUY LUẬN & GHÉP NỐI SỰ KIỆN", True, (180, 35, 45)), (380, 120))

        # Khung hiển thị Điểm số hiện tại
        score_box = pygame.Rect(645, 115, 125, 34)
        pygame.draw.rect(surface, (255, 255, 255), score_box, border_radius=6)
        pygame.draw.rect(surface, (45, 125, 80), score_box, 1, border_radius=6)
        sc_text = btn_font.render(f"Điểm : {getattr(self, 'score', 0)}", True, (45, 125, 80))
        surface.blit(sc_text, sc_text.get_rect(center=score_box.center))

        # Nút Đặt lại
        reset_hover = self.reset_btn_rect.collidepoint(self.mouse_pos)
        pygame.draw.rect(surface, (230, 220, 210) if reset_hover else (240, 235, 225), self.reset_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (180, 170, 160), self.reset_btn_rect, 1, border_radius=6)
        reset_label = btn_font.render("Đặt lại các ô", True, (80, 70, 60))
        surface.blit(reset_label, reset_label.get_rect(center=self.reset_btn_rect.center))

        # Nút Kiểm tra
        check_hover = self.check_btn_rect.collidepoint(self.mouse_pos)
        check_color = (205, 45, 55) if check_hover else (180, 35, 45)
        pygame.draw.rect(surface, check_color, self.check_btn_rect, border_radius=6)
        check_label = btn_font.render("Kiểm tra (Enter)", True, (255, 255, 255))
        surface.blit(check_label, check_label.get_rect(center=self.check_btn_rect.center))

        # 3. 4 Ô timeline
        hover_stage = next((i for i, r in enumerate(self.slot_rects) if r.collidepoint(self.mouse_pos)), None)
        self.slot_rects = self.board.draw(
            surface, self.board_rect,
            selected_stage=self.selected_slot_stage,
            hover_stage=hover_stage
        )
        self.remove_rects = self.board.remove_rects

        # 4. Dòng thông điệp trạng thái & gợi ý
        msg_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 17, bold=True)
        hint_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 14)

        msg_color = (45, 125, 80) if self.board.verified else (180, 35, 45)
        surface.blit(msg_font.render(self.board.message, True, msg_color), (380, 335))

        hint_text = "• Kéo thả hoặc click để ĐỔI CHỖ các ô  |  • Chuột phải hoặc bấm nút [×] để GỠ BỎ"
        hint_text_2 = "• Nút 'Đặt lại các ô' hoặc phím C / Backspace để xếp lại từ đầu  |  • Enter để kiểm tra"
        surface.blit(hint_font.render(hint_text, True, (60, 55, 50)), (380, 370))
        surface.blit(hint_font.render(hint_text_2, True, (90, 85, 80)), (380, 395))

        # 5. Nếu đang kéo thả: Vẽ thẻ bài bay theo con trỏ chuột (Visual dragging)
        if self.dragging_id:
            drag_clue = self.inventory.get(self.dragging_id)
            if drag_clue:
                mx, my = self.mouse_pos
                preview_rect = pygame.Rect(mx - 80, my - 25, 160, 50)
                shadow_rect = preview_rect.copy()
                shadow_rect.x += 4
                shadow_rect.y += 4
                pygame.draw.rect(surface, (180, 175, 165), shadow_rect, border_radius=6)
                pygame.draw.rect(surface, (255, 252, 240), preview_rect, border_radius=6)
                pygame.draw.rect(surface, (235, 130, 20), preview_rect, 2, border_radius=6)
                p_font = pygame.font.SysFont(VIETNAMESE_FONT_FAMILY, 13, bold=True)
                surface.blit(p_font.render(drag_clue.title[:18], True, (50, 45, 40)), (preview_rect.x + 8, preview_rect.y + 8))
                if len(drag_clue.title) > 18:
                    surface.blit(p_font.render(drag_clue.title[18:36], True, (50, 45, 40)), (preview_rect.x + 8, preview_rect.y + 26))


class QuizSystem:
    """Three multiple-choice questions, +30 knowledge points per correct answer."""

    def __init__(self, questions):
        if not questions:
            raise ValueError("Quiz phải có ít nhất một câu hỏi.")
        for question in questions:
            if len(question.get("options", [])) != 4 or question.get("answer") not in range(4):
                raise ValueError("Mỗi câu hỏi cần 4 lựa chọn và answer từ 0 đến 3.")
            if not question.get("explanation") or not question.get("source"):
                raise ValueError("Câu hỏi cần giải thích và nguồn sử liệu.")
        self.questions = questions
        self.answers = []
        self.score = 0

    def answer(self, question_index, option_index):
        if question_index != len(self.answers):
            raise ValueError("Trả lời lần lượt từng câu, không bỏ qua câu.")
        question = self.questions[question_index]
        correct = option_index == question["answer"]
        points = 30 if correct else 0
        self.score += points
        self.answers.append({
            "question_id": question.get("id", f"q{question_index + 1}"),
            "selected_option": option_index,
            "correct": correct,
            "points": points,
            "explanation": question["explanation"],
            "source": question["source"],
        })
        return self.answers[-1]


def build_save_json(quest_id, state_machine, inventory, quiz=None):
    """Produce a stable UTF-8 JSON payload suitable for a FastAPI save endpoint."""
    payload = {
        "schema_version": 1,
        "quest_id": quest_id,
        "state": state_machine.state.value,
        "collected_clue_ids": sorted(state_machine.collected_clues),
        "inventory": [asdict(clue) for clue in inventory.clues],
        "timeline_verified": state_machine.timeline_verified,
        "quiz_completed": state_machine.quiz_completed,
        "quiz": {
            "score": quiz.score if quiz else 0,
            "answers": quiz.answers if quiz else [],
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def demo_pac_bo():
    """Run a complete deterministic Pác Bó 1941 quest without opening a window."""
    clues = [
        Clue("pacbo_testimony", "Lời khai người dẫn đường", "lời khai",
             "Nguyễn Ái Quốc trở về Cao Bằng ngày 28/01/1941 qua mốc 108.",
             "Hồ Chí Minh: Biên niên tiểu sử, tập 3", 0),
        Clue("pacbo_resolution", "Nghị quyết Hội nghị Trung ương 8", "văn kiện",
             "Hội nghị Trung ương 8 họp tháng 5/1941, đặt giải phóng dân tộc lên hàng đầu.",
             "Văn kiện Đảng Toàn tập, tập 7 (1940–1945)", 1),
        Clue("pacbo_typewriter", "Máy chữ tại hang Pác Bó", "hiện vật",
             "Hiện vật gắn với nơi làm việc và hoạt động cách mạng ở Pác Bó.",
             "Khu di tích quốc gia đặc biệt Pác Bó, hồ sơ trưng bày", 2),
        Clue("pacbo_independence", "Mặt trận Việt Minh ra đời", "văn kiện",
             "Hội nghị quyết định thành lập Mặt trận Việt Minh ngày 19/5/1941.",
             "Văn kiện Đảng Toàn tập, tập 7 (1940–1945)", 3),
    ]
    machine = QuestStateMachine(clue.id for clue in clues)
    inventory = ClueInventory()
    assert machine.start()
    for clue in clues:
        inventory.add(clue)
        assert machine.collect_clue(clue.id)
    board = DeductionTimelineBoard(inventory, machine)
    for stage, clue in enumerate(clues):
        board.place(clue.id, stage)
    assert board.check()

    questions = [
        {"id": "pacbo_q1", "question": "Nguyễn Ái Quốc trở về nước năm nào?", "options": ["1930", "1941", "1945", "1954"], "answer": 1,
         "explanation": "Nguyễn Ái Quốc trở về Pác Bó ngày 28/01/1941.", "source": "Hồ Chí Minh: Biên niên tiểu sử, tập 3"},
        {"id": "pacbo_q2", "question": "Hội nghị Trung ương 8 họp vào tháng nào?", "options": ["1/1941", "3/1941", "5/1941", "8/1941"], "answer": 2,
         "explanation": "Hội nghị Trung ương 8 diễn ra từ ngày 10 đến 19/5/1941.", "source": "Văn kiện Đảng Toàn tập, tập 7"},
        {"id": "pacbo_q3", "question": "Mặt trận Việt Minh thành lập ngày nào?", "options": ["19/5/1941", "2/9/1945", "3/2/1930", "7/5/1954"], "answer": 0,
         "explanation": "Mặt trận Việt Minh thành lập ngày 19/5/1941.", "source": "Văn kiện Đảng Toàn tập, tập 7"},
    ]
    quiz = QuizSystem(questions)
    for index, question in enumerate(questions):
        quiz.answer(index, question["answer"])
    assert machine.mark_quiz_completed()
    assert machine.complete()
    return build_save_json("pac_bo_1941", machine, inventory, quiz)


if __name__ == "__main__":
    print(demo_pac_bo())
