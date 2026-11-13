
import sys
import argparse
import os
import threading
import queue
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import pygame

from scenes.login_scene import LoginScene
from scenes.map_scene import MapScene
from scenes.investigation_scene import InvestigationScene
from scenes.deduction_scene import DeductionScene
from scenes.quit_scene import QuitScene
from scenes.review_scene import ReviewScene
from task4 import Clue, ClueInventory, DeductionTimelineBoard, QuizSystem, TimelineScene, QuestStateMachine
from task5 import ScoringEngine, ReviewManager

try:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, SCREEN_TITLE
    WIDTH = SCREEN_WIDTH
    HEIGHT = SCREEN_HEIGHT
except ImportError:
    WIDTH = 1080
    HEIGHT = 720
    TARGET_FPS = 60
    SCREEN_TITLE = "Hành Trình Lịch Sử Việt Nam"

try:
    from services.logger import setup_logger
    logger = setup_logger("GameDirector")
except ImportError:
    import logging
    logger = logging.getLogger("GameDirector")


def parse_window_size():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--width", type=int, default=WIDTH, help="Cửa sổ rộng (px)")
    parser.add_argument("--height", type=int, default=HEIGHT, help="Cửa sổ cao (px)")
    args, _ = parser.parse_known_args()
    return max(800, args.width), max(600, args.height)


def key_is(event, letter):
    """Kiem tra phim vua nhan co phai chu `letter` khong.

    Nhan theo CA ma phim (event.key) LAN ky tu go ra (event.unicode),
    nen van dung khi bat Caps Lock hoac Shift.
    """
    if event.key == getattr(pygame, "K_" + letter):
        return True

    typed = getattr(event, "unicode", "")
    return bool(typed) and typed.lower() == letter


class Game:
    def __init__(self):
        # =====================================
        # 1. KHOI TAO GAME
        # =====================================
        # A stale dummy driver (used by headless tests) creates no visible window.
        if os.environ.get("SDL_VIDEODRIVER", "").lower() == "dummy":
            os.environ.pop("SDL_VIDEODRIVER", None)
        pygame.init()

        self.window_size = parse_window_size()
        self.fullscreen = False
        self.display = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        # Keep a fixed logical canvas so existing scene coordinates/layout remain valid.
        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()
        pygame.display.set_caption("Game Lịch Sử Việt Nam")
        self.clock = pygame.time.Clock()
        self.delta_time = 0.0
        self.elapsed_time = 0.0
        self.transition_alpha = 255.0
        self.transition_speed = 850.0
        self.previous_scene = "login"
        self.hint_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.notice_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 18, bold=True)

        # =============================================================
        # 2. GỌI TẦNG DỊCH VỤ / SQL ĐỂ ĐỔ DỮ LIỆU VÀO GAME
        # =============================================================
        from services.game_data_service import game_data_service
        self.game_data = {
            "locations": game_data_service.locations,
            "investigation_data": game_data_service.investigation_data,
            "questions": game_data_service.questions,
            "is_connected": False,
            "status_message": "Đang tải dữ liệu CSDL...",
        }
        self._data_queue = queue.Queue()
        self._data_loader = threading.Thread(
            target=self._load_game_data, args=(game_data_service,), daemon=True
        )
        self._data_loader.start()

        # =============================================================
        # 3. KHỞI TẠO CÁC MÀN HÌNH (GIAO DIỆN NHẬN DỮ LIỆU ĐÃ MAP)
        # =============================================================
        self.login_scene = LoginScene()
        self.map_scene = MapScene(
            locations=self.game_data["locations"],
            db_status=self.game_data["status_message"]
        )
        self.map_scene.investigation_data = self.game_data.get("investigation_data", {})
        self.investigation_scene = InvestigationScene(
            investigation_data=self.game_data["investigation_data"]
        )
        self.deduction_scene = DeductionScene(
            questions=self.game_data["questions"]
        )
        self.quit_scene = QuitScene()
        self.task4_scene = None

        # Khởi tạo Hệ thống Tính điểm & Ôn tập tư liệu (Task 5)
        self.scoring_engine = ScoringEngine()
        self.review_manager = ReviewManager()
        self.review_scene = ReviewScene(
            review_manager=self.review_manager,
            scoring_engine=self.scoring_engine
        )

        # Quản lý phiên đăng nhập và tiến độ người chơi
        self.current_user = None
        self.score = 0
        self.last_score_delta = 0
        self.completed = set()
        self.map_scene.completed = self.completed
        from task4 import QuestManager
        self.quest_manager = QuestManager(self.game_data["locations"], self.completed)
        self.map_scene.quest_manager = self.quest_manager

        # Khởi đầu tại màn hình Đăng nhập
        self.scene = "login"
        self.scene_before_quit = "login"
        self.running = True

        self.notice = ""
        self.notice_until = 0

    def _load_game_data(self, service):
        """Load SQL data off the Pygame thread so the window remains responsive."""
        try:
            self._data_queue.put((True, service.load_game_data()))
        except Exception as error:
            self._data_queue.put((False, error))

    def _apply_loaded_game_data(self, data):
        self.game_data = data
        self.map_scene.locations = data["locations"]
        self.map_scene.db_status = data["status_message"]
        self.map_scene.investigation_data = data["investigation_data"]
        self.investigation_scene.investigation_data = data["investigation_data"]
        self.deduction_scene.questions = data["questions"]
        from task4 import QuestManager
        self.quest_manager = QuestManager(data["locations"], self.completed)
        self.map_scene.quest_manager = self.quest_manager

    def apply_user_session(self, user, progress):
        """Thiết lập thông tin người chơi và nạp tiến trình lưu từ CSDL."""
        self.current_user = user
        self.score = progress.get("score", 0)
        self.completed = progress.get("completed", set())
        self.map_scene.completed = self.completed
        self.quest_manager = self.quest_manager.__class__(
            self.game_data["locations"], self.completed, progress.get("task4", {})
        )
        self.map_scene.quest_manager = self.quest_manager
        self.restore_task4_progress()

        display_name = user.get("ho_va_ten") or user.get("ten_dang_nhap")
        self.map_scene.player_name = display_name
        self.map_scene.score = self.score

        max_year = progress.get("max_year", 1914)
        if 1914 <= max_year <= 1975:
            self.map_scene.selected_year = max_year

        self.scene = "map"
        self.notify(f"Đăng nhập thành công! Chào {display_name}")

    # =================================================================
    # CAC LENH DIEU HUONG (moi phim chi goi mot ham o day)
    # =================================================================
    def notify(self, text):
        self.notice = text
        self.notice_until = pygame.time.get_ticks() + 2800

    def open_quit(self):
        """Phim Q: mo man hinh xac nhan thoat tu BAT KY man hinh nao."""
        if self.scene != "quit":
            self.scene_before_quit = self.scene
            self.scene = "quit"

    def open_investigation(self):
        """Phim Enter tren ban do: vao man hinh dieu tra."""
        location = self.map_scene.selected_location

        if location is None:
            self.notify("Hãy chọn một địa điểm trên bản đồ")
            return

        if self.map_scene.status(location) == "locked":
            self.notify("Địa điểm chưa mở khóa")
            return

        self.investigation_scene.set_location(location)
        self.quest_manager.start(location)
        self.investigation_scene.collected_clues.update(
            self.quest_manager.collected_clues.get(location["name"], set())
        )
        self.scene = "investigation"

    def open_deduction(self):
        """Phim D: sang man hinh suy luan (tu ban do hoac man hinh dieu tra)."""
        if self.scene not in ("map", "investigation"):
            return

        location = self.map_scene.selected_location

        if location is None:
            self.notify("Hãy chọn một địa điểm trên bản đồ trước")
            return

        if self.scene == "investigation":
            location = self.investigation_scene.location
            if location is None:
                return

        if self.map_scene.status(location) == "locked":
            self.notify("Địa điểm chưa mở khóa")
            return

        already_done = location["name"] in self.completed

        if not already_done:
            if not self.investigation_scene.is_complete(location):
                self.notify("Cần thu thập đủ manh mối trước (ENTER để điều tra, bấm vào manh mối)")
                return
            self.quest_manager.clues_complete(location)

        from task4 import TIMELINE_QUEST_CONFIGS
        if location["name"] in TIMELINE_QUEST_CONFIGS and not already_done:
            self.open_timeline_deduction(location)
            return

        self.deduction_scene.score = self.score
        self.deduction_scene.last_score_delta = 0
        self.deduction_scene.set_location(location)
        self.quest_manager.clues_complete(location)
        self.scene = "deduction"

    def open_pac_bo_timeline(self, location):
        """Backward-compatible wrapper for Pác Bó timeline."""
        self.open_timeline_deduction(location)

    def open_timeline_deduction(self, location):
        """Enter Task 4's generalized 4-stage cause-effect timeline/quiz scene."""
        loc_name = location["name"]
        data = self.investigation_scene.investigation_data.get(loc_name, {})
        field_clues = data.get("clues", [])
        if field_clues and not all(c["id"] in self.investigation_scene.collected_clues for c in field_clues):
            self.notify(f"Hãy thu thập đủ manh mối {location.get('display_name', loc_name)} trước khi mở bàn suy luận.")
            return

        from task4 import TIMELINE_QUEST_CONFIGS
        config = TIMELINE_QUEST_CONFIGS.get(loc_name)
        if not config:
            self.deduction_scene.score = self.score
            self.deduction_scene.last_score_delta = 0
            self.deduction_scene.set_location(location)
            self.quest_manager.clues_complete(location)
            self.scene = "deduction"
            return

        self.current_timeline_location = location
        self.current_timeline_config = config
        self.quest_manager.start(location)
        self.quest_manager.clues_complete(location)

        clues = config["clues"]
        self.task4_machine = QuestStateMachine(clue.id for clue in clues)
        self.task4_machine.start()
        self.task4_inventory = ClueInventory()
        for clue in clues:
            self.task4_inventory.add(clue)
            self.task4_machine.collect_clue(clue.id)
        self.task4_board = DeductionTimelineBoard(self.task4_inventory, self.task4_machine)
        self.task4_scene = TimelineScene(self.task4_inventory, self.task4_board)
        self.task4_scene.score = self.score
        self.deduction_scene.score = self.score
        self.deduction_scene.set_location(location)
        self.task4_questions = QuizSystem(config["questions"])
        self.task4_quiz_index = 0
        self.task4_feedback = "Kéo từng mảnh vào đúng ô, sau đó nhấn Enter để xác thực."
        self.scene = "task4_timeline"

    def go_back(self):
        """Phim ESC: quay lai man hinh truoc."""
        if self.scene == "quit":
            self.scene = self.scene_before_quit
        elif self.scene == "review":
            self.scene = "map"
        elif self.scene == "deduction":
            self.scene = "investigation"
        elif self.scene in ("task4_timeline", "task4_quiz"):
            self.scene = "investigation"
        elif self.scene == "investigation":
            self.scene = "map"
        elif self.scene == "map":
            self.open_quit()

    def handle_quit_result(self, result):
        if result == "quit":
            self.running = False
        elif result == "back":
            self.scene = self.scene_before_quit

    def handle_deduction_result(self, result):
        if result == "completed":
            location = self.deduction_scene.location
            if location and location["name"] not in self.completed:
                self.quest_manager.record_quiz_answer(location, self.deduction_scene.last_answer_correct)
                self.save_task4_progress(location)
                self.deduction_scene.last_answer_recorded = self.deduction_scene.last_answer_correct
                if not self.quest_manager.complete(location):
                    self.notify("Chưa đủ điều kiện hoàn thành quest. Hãy kiểm tra manh mối và quiz.")
                    return
                self.completed.add(location["name"])
                self.score += 30
                self.last_score_delta = 30
                self.deduction_scene.score = self.score
                self.deduction_scene.last_score_delta = 30
                self.map_scene.score = self.score
                self.map_scene.completed = self.completed
                self.quest_manager._refresh_unlocks()
                self.save_task4_progress(location)

            # Tìm địa điểm tiếp theo vừa được mở khóa
            next_loc = None
            if location and location.get("name") == "Ba Dinh":
                next_loc = next((l for l in self.game_data["locations"] if l["name"] == "Dien Bien Phu"), None)
            if not next_loc:
                for loc in self.game_data["locations"]:
                    if loc["name"] not in self.completed and self.map_scene.status(loc) != "locked":
                        next_loc = loc
                        break

            if next_loc:
                self.map_scene.selected_location = next_loc
                self.map_scene.selected_year = next_loc.get("start", self.map_scene.selected_year)
                next_name = next_loc.get("display_name", next_loc["name"])
                self.notify(f"Hoàn thành! +30 điểm | Đã mở khóa: {next_name}!")
            else:
                self.notify(f"Hoàn thành xuất sắc! +30 điểm | Tổng điểm: {self.score}")

            # Đồng bộ tiến độ và điểm số vào bảng `tien_do_choi` trong MySQL
            user_id = self.current_user.get("ma_nguoi_dung", 0) if self.current_user else 0
            if user_id > 0:
                try:
                    from services.game_data_service import game_data_service
                    loc_id = next_loc.get("id", location.get("id", 1)) if next_loc else location.get("id", 1)
                    year = max(location.get("end", 1914), next_loc.get("start", 1914) if next_loc else 1914)
                    game_data_service.sync_user_progress(
                        user_id=user_id,
                        current_loc_id=loc_id,
                        max_year=year,
                        score=self.score,
                        completed_set=self.completed
                    )
                except Exception as e:
                    print(f"Lỗi khi lưu tiến trình: {e}")
        elif result == "correct_question":
            location = self.deduction_scene.location
            if location and location["name"] not in self.completed:
                self.score += 30
                self.last_score_delta = 30
                self.deduction_scene.score = self.score
                self.deduction_scene.last_score_delta = 30
                self.map_scene.score = self.score
                self.notify(f"Chính xác! +30 điểm | Điểm hiện tại: {self.score}")
        elif result is None and self.deduction_scene.last_answer_correct is not None:
            # Ghi nhận câu trả lời sai vào Hệ thống Ôn tập Task 5
            if self.deduction_scene.last_answer_correct is False:
                loc = self.deduction_scene.location
                if loc:
                    q_idx = min(self.deduction_scene.question_index, len(self.deduction_scene.questions) - 1)
                    curr_q = self.deduction_scene.questions[q_idx]
                    self.review_manager.record_mistake(
                        question_id=f"deduct_{loc['name']}_{q_idx}",
                        location_name=loc.get("display_name", loc["name"]),
                        question_text=curr_q["question"],
                        options=curr_q["options"],
                        correct_index=curr_q["answer"],
                        user_choice=-1,
                        explanation=curr_q.get("explanation", "Kiểm chứng tư liệu lịch sử."),
                        source_title="Đại cương Lịch sử Việt Nam (Tập 2)",
                        source_author="Viện Sử học / Bộ GD&ĐT",
                        source_publisher="NXB Giáo dục",
                        source_citation=loc.get("event_time", "Giai đoạn 1914 - 1954")
                    )
            self.quest_manager.record_quiz_answer(
                self.deduction_scene.location,
                self.deduction_scene.last_answer_correct,
            )
            self.save_task4_progress(self.deduction_scene.location)
            self.deduction_scene.last_answer_recorded = self.deduction_scene.last_answer_correct
        elif result == "map":
            self.scene = "map"
            if not self.map_scene.selected_location or self.map_scene.selected_location["name"] in self.completed:
                for loc in self.game_data["locations"]:
                    if loc["name"] not in self.completed and self.map_scene.status(loc) != "locked":
                        self.map_scene.selected_location = loc
                        self.map_scene.selected_year = loc.get("start", self.map_scene.selected_year)
                        break

    def handle_task4_quiz_answer(self, option_index):
        """Apply one answer and finish/save the integrated timeline quest."""
        if self.scene != "task4_quiz" or self.task4_quiz_index >= 3:
            return
        result = self.task4_questions.answer(self.task4_quiz_index, option_index)
        location = getattr(self, "current_timeline_location", None) or self.deduction_scene.location or self.investigation_scene.location
        if not location:
            location = next((loc for loc in self.game_data["locations"] if loc["name"] == "Pac Bo"), {"id": 4, "name": "Pac Bo", "end": 1945})

        already_done = location["name"] in self.completed
        if not already_done and result["correct"]:
            self.last_score_delta = result["points"]
            self.score += result["points"]
        else:
            self.last_score_delta = 0

        self.map_scene.score = self.score
        self.deduction_scene.score = self.score
        if hasattr(self, "task4_scene"):
            self.task4_scene.score = self.score

        # Đồng bộ điểm ngay vào MySQL nếu người dùng đã đăng nhập và trả lời đúng lần đầu
        user_id = self.current_user.get("ma_nguoi_dung", 0) if self.current_user else 0
        if user_id > 0 and result["correct"] and not already_done:
            try:
                from services.game_data_service import game_data_service
                game_data_service.sync_user_progress(
                    user_id=user_id,
                    current_loc_id=location.get("id", 4),
                    max_year=max(self.current_user.get("max_year", 1914), location.get("end", 1945)),
                    score=self.score,
                    completed_set=self.completed
                )
            except Exception as e:
                pass

        # Nếu trả lời sai, tự động thêm vào phòng ôn tập Task 5
        if not result["correct"]:
            q_data = self.task4_questions.questions[self.task4_quiz_index]
            self.review_manager.record_mistake(
                question_id=q_data.get("id", f"{location['name']}_q_{self.task4_quiz_index}"),
                location_name=location.get("display_name", location["name"]),
                question_text=q_data["question"],
                options=q_data["options"],
                correct_index=q_data["answer"],
                user_choice=option_index,
                explanation=result["explanation"],
                source_title=q_data.get("source", "Tài liệu Lịch sử chuẩn"),
                source_author="Viện Sử học / NXB Chính trị Quốc gia",
                source_publisher="NXB Chính trị Quốc gia Sự thật",
                source_citation=result.get("source", location.get("name", ""))
            )
        self.task4_feedback = (
            ("Chính xác! " if result["correct"] else "Chưa đúng. ")
            + result["explanation"] + " Nguồn: " + result["source"]
        )
        self.task4_quiz_index += 1
        if self.task4_quiz_index == 3:
            self.task4_machine.mark_quiz_completed()
            self.task4_machine.complete()
            self.quest_manager.clues_complete(location)
            self.quest_manager.record_quiz_answer(location, True)
            self.quest_manager.complete(location)
            self.completed.add(location["name"])
            self.map_scene.completed = self.completed
            self.quest_manager._refresh_unlocks()
            self.save_task4_progress(location)

            loc_label = getattr(self, "current_timeline_config", {}).get("event_label", location["name"]) if hasattr(self, "current_timeline_config") else location["name"]

            # Tìm địa điểm tiếp theo vừa được mở khóa (đặc biệt: Ba Đình sẽ mở thẳng Lòng chảo Điện Biên Phủ)
            next_loc = None
            if location.get("name") == "Ba Dinh":
                next_loc = next((l for l in self.game_data["locations"] if l["name"] == "Dien Bien Phu"), None)
            if not next_loc:
                for loc in self.game_data["locations"]:
                    if loc["name"] not in self.completed and self.map_scene.status(loc) != "locked":
                        next_loc = loc
                        break

            if next_loc:
                self.map_scene.selected_location = next_loc
                self.map_scene.selected_year = next_loc.get("start", self.map_scene.selected_year)
                next_name = next_loc.get("display_name", next_loc["name"])
                self.notify(f"Hoàn thành {loc_label}! +{self.task4_questions.score} điểm | Đã mở khóa: {next_name}!")
                self.task4_feedback += f" | Đã mở khóa {next_name}!"
            else:
                self.notify(f"Quest {loc_label} hoàn thành! +{self.task4_questions.score} điểm tri thức.")
                self.task4_feedback += f" | Quest {loc_label} hoàn thành!"

            user_id = self.current_user.get("ma_nguoi_dung", 0) if self.current_user else 0
            if user_id > 0:
                try:
                    from services.game_data_service import game_data_service
                    target_loc = next_loc or location
                    loc_id = target_loc.get("id", location.get("id", 4))
                    year = max(location.get("end", 1945), target_loc.get("start", 1954), target_loc.get("end", 1954))
                    curr_max = self.current_user.get("max_year", 1914)
                    new_max_year = max(curr_max, year, 1954 if location.get("name") == "Ba Dinh" else 1945)
                    self.current_user["max_year"] = new_max_year
                    self.current_user["current_loc_id"] = loc_id
                    game_data_service.sync_user_progress(
                        user_id=user_id,
                        current_loc_id=loc_id,
                        max_year=new_max_year,
                        score=self.score,
                        completed_set=self.completed
                    )
                    print(f"[MySQL] Đã lưu hoàn thành {location['name']} và mở khóa {target_loc['name']} (năm {new_max_year})!")
                except Exception as e:
                    print(f"Lỗi lưu hoàn thành {location['name']} vào MySQL: {e}")

    def task4_save_payload(self):
        """Return Task 4 progress in the schema expected by a future FastAPI API."""
        from task4 import build_save_json
        quest_id = getattr(self, "current_timeline_config", {}).get("quest_id", "pac_bo_1941") if hasattr(self, "current_timeline_config") else "pac_bo_1941"
        return json.loads(build_save_json(
            quest_id, self.task4_machine, self.task4_inventory, self.task4_questions
        ))

    def draw_task4_quiz(self):
        """Render the three-question review phase within the current scene manager."""
        self.screen.fill((245, 239, 220))
        font = pygame.font.SysFont("segoeui,arial,timesnewroman", 25, bold=True)
        score_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 22, bold=True)
        bonus_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16, bold=True)
        body = pygame.font.SysFont("segoeui,arial,timesnewroman", 19)

        title_text = getattr(self, "current_timeline_config", {}).get("title", "ÔN TẬP SỬ LIỆU - PÁC BÓ 1941") if hasattr(self, "current_timeline_config") else "ÔN TẬP SỬ LIỆU - PÁC BÓ 1941"
        title = font.render(title_text, True, (180, 35, 45))
        self.screen.blit(title, (55, 40))

        # Khung hiển thị ĐIỂM SỐ đang có (cộng dồn sau mỗi câu đúng)
        score_box = pygame.Rect(780, 32, 215, 46)
        pygame.draw.rect(self.screen, (255, 255, 255), score_box, border_radius=10)
        pygame.draw.rect(self.screen, (45, 125, 80), score_box, 2, border_radius=10)
        score_text = score_font.render(f"Điểm : {self.score}", True, (45, 125, 80))
        self.screen.blit(score_text, score_text.get_rect(center=score_box.center))

        if getattr(self, "last_score_delta", 0) > 0 and self.task4_quiz_index > 0:
            plus_badge = bonus_font.render(f"+{self.last_score_delta}", True, (35, 155, 70))
            self.screen.blit(plus_badge, (score_box.right + 10, score_box.y + 12))

        loc_label = getattr(self, "current_timeline_config", {}).get("event_label", "Địa điểm") if hasattr(self, "current_timeline_config") else "Pác Bó"

        if self.task4_quiz_index < 3:
            question = self.task4_questions.questions[self.task4_quiz_index]
            self.screen.blit(body.render(f"Câu {self.task4_quiz_index + 1}/3 · +30 điểm/câu đúng", True, (50, 45, 40)), (60, 105))
            self.screen.blit(body.render(question["question"], True, (50, 45, 40)), (60, 155))
            for index, option in enumerate(question["options"]):
                rect = pygame.Rect(90, 220 + index * 72, 900, 54)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=8)
                pygame.draw.rect(self.screen, (210, 205, 195), rect, 2, border_radius=8)
                self.screen.blit(body.render(f"{chr(65 + index)}. {option}", True, (50, 45, 40)), (rect.x + 18, rect.y + 14))
        else:
            self.screen.blit(font.render(f"Quest {loc_label} Hoàn Thành! Đã Mở Khóa Vùng Tiếp Theo", True, (45, 125, 80)), (60, 140))
            self.screen.blit(body.render(f"Điểm bài quiz: {self.task4_questions.score}/90 điểm", True, (50, 45, 40)), (60, 195))
            self.screen.blit(body.render(f"Tổng điểm toàn game hiện có: {self.score} điểm", True, (180, 35, 45)), (60, 235))

            # Nút bấm Về bản đồ
            map_btn = pygame.Rect(60, 280, 320, 48)
            pygame.draw.rect(self.screen, (45, 125, 80), map_btn, border_radius=8)
            btn_txt = font.render("VỀ BẢN ĐỒ (ENTER)", True, (255, 255, 255))
            self.screen.blit(btn_txt, btn_txt.get_rect(center=map_btn.center))

        if self.task4_feedback:
            # Tự động chia dòng giải thích rõ ràng
            words = self.task4_feedback.split()
            lines = []
            cur = ""
            for w in words:
                cand = (cur + " " + w).strip()
                if body.size(cand)[0] < 960:
                    cur = cand
                else:
                    if cur:
                        lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            y_fb = 535
            for fl in lines[:3]:
                fb_color = (45, 125, 80) if "Chính xác" in self.task4_feedback else (180, 35, 45)
                self.screen.blit(body.render(fl, True, fb_color), (60, y_fb))
                y_fb += 26

    # =================================================================
    # XU LY SU KIEN
    # =================================================================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.window_size = self.display.get_size()
            else:
                self.window_size = parse_window_size()
                self.display = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            return

        if self.transition_alpha > 100:
            return
        if event.type == pygame.VIDEORESIZE:
            self.window_size = (max(800, event.w), max(600, event.h))
            if not self.fullscreen:
                self.display = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            return
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            scale = min(self.window_size[0] / WIDTH, self.window_size[1] / HEIGHT)
            offset_x = (self.window_size[0] - WIDTH * scale) / 2
            offset_y = (self.window_size[1] - HEIGHT * scale) / 2
            logical_pos = (
                max(0, min(WIDTH - 1, int((event.pos[0] - offset_x) / scale))),
                max(0, min(HEIGHT - 1, int((event.pos[1] - offset_y) / scale))),
            )
            event = pygame.event.Event(event.type, {**event.dict, "pos": logical_pos})
        # Dong game bang nut X
        if event.type == pygame.QUIT:
            self.running = False
            return

        # ---------------- MÀN HÌNH ĐĂNG NHẬP ----------------
        if self.scene == "login":
            result = self.login_scene.handle_event(event)
            if result and result.get("action") == "login_success":
                self.apply_user_session(result["user"], result["progress"])
            return

        # ---------------- MÀN HÌNH ÔN TẬP (TASK 5) ----------------
        if self.scene == "review":
            res = self.review_scene.handle_event(event)
            if res == "map":
                self.scene = "map"
            return

        # ---------------- HỘP XÁC NHẬN THOÁT ----------------
        if self.scene == "quit":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.handle_quit_result(self.quit_scene.handle_event(event))
            return

        # ---------------- BÀN PHÍM (CÁC MÀN HÌNH CHƠI) ----------------
        if event.type == pygame.KEYDOWN:
            # Cac phim chung
            if key_is(event, "q"):
                self.open_quit()
                return

            if event.key == pygame.K_ESCAPE:
                self.go_back()
                return

            if self.scene == "task4_timeline":
                self.task4_scene.handle_event(event)
                if self.task4_board.verified:
                    self.scene = "task4_quiz"
                    self.task4_feedback = "Timeline đúng! Bắt đầu 3 câu hỏi ôn tập."
                return

            if self.scene == "task4_quiz":
                if self.task4_quiz_index >= 3 and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.scene = "map"
                    if not self.map_scene.selected_location or self.map_scene.selected_location["name"] in self.completed:
                        for loc in self.game_data["locations"]:
                            if loc["name"] not in self.completed and self.map_scene.status(loc) != "locked":
                                self.map_scene.selected_location = loc
                                self.map_scene.selected_year = loc.get("start", self.map_scene.selected_year)
                                break
                    return
                if pygame.K_1 <= event.key <= pygame.K_4 and self.task4_quiz_index < 3:
                    self.handle_task4_quiz_answer(event.key - pygame.K_1)
                return

            # Đăng xuất tài khoản khi bấm phím O
            if key_is(event, "o") and self.scene == "map":
                self.scene = "login"
                self.login_scene.switch_mode("login")
                return

            # Phím riêng cho Bản đồ (Bảng vàng L, Túi đồ T/I)
            if self.scene == "map":
                self.map_scene.handle_event(event)

            # Mở phòng Ôn tập sử liệu (Task 5)
            if key_is(event, "r") and self.scene == "map":
                self.review_scene.player_name = self.map_scene.player_name
                self.review_scene.scoring_engine.total_score = self.score
                self.scene = "review"
                return

            if key_is(event, "d"):
                self.open_deduction()
                return

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.scene == "map":
                self.open_investigation()
                return

            # Cac phim rieng theo tung man hinh
            if self.scene == "investigation":
                self.investigation_scene.handle_event(event)
                self.sync_task4_clues()
            elif self.scene == "deduction":
                self.handle_deduction_result(self.deduction_scene.handle_event(event))
            return

        # Du phong: TEXTINPUT
        if event.type == getattr(pygame, "TEXTINPUT", None):
            typed = event.text.lower()
            if typed == "q":
                self.open_quit()
            elif typed in ("d", "đ"):
                self.open_deduction()
            elif typed == "o" and self.scene == "map":
                self.scene = "login"
                self.login_scene.switch_mode("login")
            return

        # ---------------- CHUỘT ----------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scene == "map":
                self.map_scene.handle_event(event)
            elif self.scene == "investigation":
                self.investigation_scene.handle_event(event)
                self.sync_task4_clues()
            elif self.scene == "deduction":
                self.handle_deduction_result(self.deduction_scene.handle_event(event))
            elif self.scene == "task4_timeline":
                self.task4_scene.handle_event(event)
                if self.task4_board.verified:
                    self.scene = "task4_quiz"
                    self.task4_feedback = "Timeline đúng! Bắt đầu 3 câu hỏi ôn tập."
            elif self.scene == "task4_quiz":
                if self.task4_quiz_index >= 3:
                    self.scene = "map"
                    if not self.map_scene.selected_location or self.map_scene.selected_location["name"] in self.completed:
                        for loc in self.game_data["locations"]:
                            if loc["name"] not in self.completed and self.map_scene.status(loc) != "locked":
                                self.map_scene.selected_location = loc
                                self.map_scene.selected_year = loc.get("start", self.map_scene.selected_year)
                                break
                else:
                    for index in range(4):
                        option_rect = pygame.Rect(90, 220 + index * 72, 900, 54)
                        if option_rect.collidepoint(event.pos):
                            self.handle_task4_quiz_answer(index)
                            break

        elif event.type == pygame.MOUSEMOTION and self.scene == "task4_timeline":
            self.task4_scene.handle_event(event)

        elif event.type == pygame.MOUSEBUTTONUP and self.scene == "task4_timeline":
            self.task4_scene.handle_event(event)
            if self.task4_board.verified:
                self.scene = "task4_quiz"
                self.task4_feedback = "Timeline đúng! Bắt đầu 3 câu hỏi ôn tập."

        elif event.type == pygame.MOUSEMOTION:
            if self.scene == "map":
                self.map_scene.handle_event(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.scene == "map":
                self.map_scene.handle_event(event)

        elif event.type == getattr(pygame, "MOUSEWHEEL", 1027):
            if self.scene == "map":
                self.map_scene.handle_event(event)

    # =================================================================
    # VE GIAO DIEN
    # =================================================================
    def draw_hint(self, text, x, y):
        hint = self.hint_font.render(text, True, (50, 45, 40))
        self.screen.blit(hint, (x, y))

    def sync_task4_clues(self):
        """Keep collected clue IDs in Task 4 state in sync with the scene."""
        location = self.investigation_scene.location
        if not location:
            return
        data = self.investigation_scene.investigation_data.get(location["name"], {})
        required_ids = [clue["id"] for clue in data.get("clues", [])]
        previous_clues = set(self.quest_manager.collected_clues.get(location["name"], set()))
        before = set(self.quest_manager.collected_clues.get(location["name"], set()))
        for clue_id in self.investigation_scene.collected_clues:
            self.quest_manager.collect_clue(location, clue_id, required_ids)
        self.investigation_scene.collected_clues.update(
            self.quest_manager.collected_clues.get(location["name"], set())
        )
        if self.quest_manager.collected_clues.get(location["name"], set()) != previous_clues:
            self.save_task4_progress(location)
        newly_collected = self.quest_manager.collected_clues.get(location["name"], set()) - before
        if newly_collected:
            self.notify(f"Hoàn thành mục tiêu nhiệm vụ! Đã nhận {len(newly_collected)} manh mối.")
            if self.current_user:
                uid = self.current_user.get("ma_nguoi_dung")
                try:
                    from data.db_queries import add_clue_to_inventory
                    for cid in newly_collected:
                        add_clue_to_inventory(uid, cid)
                except Exception:
                    pass

    def restore_task4_progress(self):
        """Restore per-location clue collection and quiz attempts after login."""
        for location in self.game_data["locations"]:
            data = self.investigation_scene.investigation_data.get(location["name"], {})
            required_ids = [clue["id"] for clue in data.get("clues", [])]
            saved = self.quest_manager.export_location_progress(location)
            self.quest_manager.restore_location_progress(
                location, saved["clue_ids"], saved["quiz_attempts"], required_ids
            )

    def save_task4_progress(self, location):
        """Persist Task 4 state for signed-in users; guests remain local-only."""
        user_id = self.current_user.get("ma_nguoi_dung", 0) if self.current_user else 0
        if user_id <= 0 or not location:
            return
        progress = self.quest_manager.export_location_progress(location)
        from services.game_data_service import game_data_service
        success, message = game_data_service.sync_task4_progress(
            user_id,
            location.get("id", 0),
            progress["clue_ids"],
            progress["quiz_attempts"],
        )
        if not success:
            print(f"Không lưu được tiến trình Task 4: {message}")

    def draw(self):
        if self.scene == "login":
            self.login_scene.draw(self.screen)

        elif self.scene == "map":
            self.map_scene.draw(self.screen, self.delta_time)
            self.draw_hint("ENTER: Điều tra | D: Suy luận | T: Túi đồ | L: Bảng vàng | R: Ôn tập | Q: Thoát", 185, 678)

        elif self.scene == "review":
            self.review_scene.draw(self.screen)

        elif self.scene == "investigation":
            self.investigation_scene.draw(self.screen)
            self.draw_hint(
                "Chọn nhiệm vụ rồi đối chiếu bằng chứng: 1-3 | ESC: Đóng / quay lại | Q: Thoát",
                210, 678
            )

        elif self.scene == "deduction":
            self.deduction_scene.draw(self.screen)
            self.draw_hint("Kéo mảnh ghép vào ô | ENTER: xác thực | ESC: quay lại", 250, 675)

        elif self.scene == "task4_timeline":
            self.task4_scene.draw(self.screen)
            self.draw_hint("Kéo thả / Click: Đổi chỗ | Chuột phải / [×]: Gỡ ô | Nút 'Đặt lại': Xóa hết | ENTER: Kiểm tra | ESC: Bản đồ", 100, 680)

        elif self.scene == "task4_quiz":
            self.draw_task4_quiz()
            self.draw_hint("Chọn A-D bằng phím 1-4 hoặc chuột | ESC: quay lại", 300, 675)

        elif self.scene == "quit":
            self.quit_scene.draw(self.screen)

        # Thong bao ngan (hien vai giay)
        if self.notice and pygame.time.get_ticks() < self.notice_until:
            image = self.notice_font.render(self.notice, True, (255, 255, 255))
            box = image.get_rect(center=(WIDTH // 2, 120))
            box.inflate_ip(24, 14)
            pygame.draw.rect(self.screen, (180, 35, 45), box, border_radius=10)
            self.screen.blit(image, image.get_rect(center=box.center))

        if self.transition_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 18, 16, int(self.transition_alpha)))
            self.screen.blit(overlay, (0, 0))
            self.transition_alpha = max(
                0.0, self.transition_alpha - self.transition_speed * self.delta_time
            )

        # Preserve the scene's aspect ratio; letterbox instead of stretching text.
        scale = min(self.window_size[0] / WIDTH, self.window_size[1] / HEIGHT)
        scaled_size = (max(1, round(WIDTH * scale)), max(1, round(HEIGHT * scale)))
        scaled = pygame.transform.smoothscale(self.screen, scaled_size)
        self.display.fill((20, 18, 16))
        offset = ((self.window_size[0] - scaled_size[0]) // 2,
                  (self.window_size[1] - scaled_size[1]) // 2)
        self.display.blit(scaled, offset)
        pygame.display.flip()

    # =================================================================
    # VONG LAP CHINH
    # =================================================================
    def step(self):
        try:
            succeeded, result = self._data_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            if succeeded:
                self._apply_loaded_game_data(result)
            else:
                print(f"Không tải được dữ liệu CSDL: {result}")

        self.delta_time = min(self.clock.tick(60) / 1000.0, 0.05)
        self.elapsed_time += self.delta_time
        if self.scene != self.previous_scene:
            self.previous_scene = self.scene
            self.transition_alpha = 150.0

        for event in pygame.event.get():
            self.handle_event(event)

        self.draw()

    async def run_async(self):
        """Vòng lặp bất đồng bộ tương thích 100% với Pygbag (WebGL Web Browser)."""
        import asyncio
        while self.running:
            self.step()
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

    def run(self):
        while self.running:
            self.step()

        pygame.quit()
        sys.exit()


async def main():
    game = Game()
    await game.run_async()


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

