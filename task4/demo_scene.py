"""Standalone Task 4 demo: Pác Bó 1941 with one quiz question.

Run from the project root with ``python -m task4.demo_scene``. This deliberately
does not instantiate the main game, login scene, database or earlier quests.
"""

import json
import os
import sys
import pygame

# Support both ``python -m task4.demo_scene`` from the project root and
# ``python demo_scene.py`` when the current directory is the task4 folder.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from task4.quest_system import (
    Clue, ClueInventory, DeductionTimelineBoard, QuestStateMachine,
    QuizSystem, TimelineScene, build_save_json,
)


WIDTH, HEIGHT = 1100, 700
OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "task4_demo_result.json"))


def make_demo():
    """Build a small, self-contained Pác Bó quest and its one-question quiz."""
    clues = [
        Clue("demo_testimony", "Lời khai người dẫn đường", "lời khai",
             "Nguyễn Ái Quốc trở về Cao Bằng ngày 28/01/1941 qua mốc 108.",
             "Hồ Chí Minh: Biên niên tiểu sử, tập 3", 0),
        Clue("demo_resolution", "Nghị quyết Trung ương 8", "văn kiện",
             "Hội nghị tháng 5/1941 đặt giải phóng dân tộc lên hàng đầu.",
             "Văn kiện Đảng Toàn tập, tập 7 (1940–1945)", 1),
        Clue("demo_typewriter", "Máy chữ tại Pác Bó", "hiện vật",
             "Hiện vật gắn với hoạt động làm việc tại căn cứ Pác Bó.",
             "Khu di tích quốc gia đặc biệt Pác Bó, hồ sơ trưng bày", 2),
        Clue("demo_vietminh", "Thành lập Mặt trận Việt Minh", "văn kiện",
             "Mặt trận Việt Minh thành lập ngày 19/5/1941.",
             "Văn kiện Đảng Toàn tập, tập 7 (1940–1945)", 3),
    ]
    machine = QuestStateMachine(clue.id for clue in clues)
    inventory = ClueInventory()
    quiz = QuizSystem([{
        "id": "pacbo_demo_q1",
        "question": "Nguyễn Ái Quốc trở về Tổ quốc tại Pác Bó vào năm nào?",
        "options": ["1930", "1941", "1945", "1954"],
        "answer": 1,
        "explanation": "Nguyễn Ái Quốc trở về Pác Bó ngày 28/01/1941.",
        "source": "Hồ Chí Minh: Biên niên tiểu sử, tập 3",
    }])
    board = DeductionTimelineBoard(inventory, machine)
    return clues, machine, inventory, board, quiz


class Task4Demo:
    """Minimal Scene Manager dedicated to the Task 4 demonstration."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Task 4 Demo — Pác Bó 1941")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui,arial", 22)
        self.small_font = pygame.font.SysFont("segoeui,arial", 18)
        self.clues, self.machine, self.inventory, self.board, self.quiz = make_demo()
        self.timeline_scene = TimelineScene(self.inventory, self.board)
        self.scene = "intro"
        self.quiz_answered = False
        self.feedback = ""
        self.running = True

    def start_quest(self):
        self.machine.start()
        # Demo simulates the field investigation and awards three sample pieces.
        for clue in self.clues[:3]:
            self.inventory.add(clue)
            self.machine.collect_clue(clue.id)
        # The fourth sample summarizes the outcome and completes the timeline set.
        self.inventory.add(self.clues[3])
        self.machine.collect_clue(self.clues[3].id)
        self.scene = "timeline"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif self.scene == "intro" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_quest()
            elif self.scene == "timeline" and event.key == pygame.K_RETURN:
                if self.board.check():
                    self.scene = "quiz"
                    self.feedback = "Timeline chính xác. Hãy trả lời câu hỏi để hoàn thành quest."
            elif self.scene == "quiz" and not self.quiz_answered and pygame.K_1 <= event.key <= pygame.K_4:
                self.answer_quiz(event.key - pygame.K_1)
        elif self.scene == "timeline" and event.type in (
            pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION
        ):
            self.timeline_scene.handle_event(event)
        elif self.scene == "quiz" and event.type == pygame.MOUSEBUTTONDOWN and not self.quiz_answered:
            for index in range(4):
                option_rect = pygame.Rect(125, 270 + index * 75, 850, 55)
                if option_rect.collidepoint(event.pos):
                    self.answer_quiz(index)
                    break

    def answer_quiz(self, option_index):
        result = self.quiz.answer(0, option_index)
        self.feedback = (
            ("Chính xác! " if result["correct"] else "Chưa chính xác. ")
            + result["explanation"] + " Nguồn: " + result["source"]
        )
        if not result["correct"]:
            # Keep the single-question demo retryable; a wrong attempt cannot
            # finish the quest or lock the quiz answer slot.
            self.quiz.answers.pop()
            self.scene = "quiz"
            return

        self.quiz_answered = True
        self.machine.mark_quiz_completed()
        self.machine.complete()
        self.scene = "result"
        with open(OUTPUT_PATH, "w", encoding="utf-8") as save_file:
            json.dump(
                json.loads(build_save_json("pac_bo_1941_demo", self.machine, self.inventory, self.quiz)),
                save_file, ensure_ascii=False, indent=2,
            )

    def draw(self):
        if self.scene == "intro":
            self.screen.fill((245, 239, 220))
            self.screen.blit(self.font.render("TASK 4 DEMO — QUEST PÁC BÓ 1941", True, (180, 35, 45)), (55, 70))
            self.screen.blit(self.small_font.render("Demo độc lập: không cần đăng nhập hay hoàn thành task trước.", True, (50, 45, 40)), (55, 140))
            self.screen.blit(self.small_font.render("Nhấn ENTER để nhận quest và 4 mảnh ghép mẫu.", True, (45, 125, 80)), (55, 200))
        elif self.scene == "timeline":
            self.timeline_scene.draw(self.screen)
            self.screen.blit(self.small_font.render("Kéo đủ 4 mảnh ghép vào đúng thứ tự, rồi nhấn ENTER.", True, (50, 45, 40)), (385, 430))
        else:
            self.screen.fill((245, 239, 220))
            title = "ÔN TẬP SỬ LIỆU" if self.scene == "quiz" else "KẾT QUẢ DEMO"
            self.screen.blit(self.font.render(title, True, (180, 35, 45)), (55, 55))
            if self.scene == "quiz":
                question = self.quiz.questions[0]
                self.screen.blit(self.small_font.render(question["question"], True, (50, 45, 40)), (65, 150))
                for index, option in enumerate(question["options"]):
                    rect = pygame.Rect(125, 270 + index * 75, 850, 55)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=8)
                    self.screen.blit(self.small_font.render(f"{chr(65 + index)}. {option}", True, (50, 45, 40)), (rect.x + 18, rect.y + 16))
            else:
                self.screen.blit(self.small_font.render(f"Quest: {self.machine.state.value} · Điểm: {self.quiz.score}/30", True, (45, 125, 80)), (65, 130))
                self.screen.blit(self.small_font.render(f"JSON đã lưu: {OUTPUT_PATH}", True, (50, 45, 40)), (65, 175))
            if self.feedback:
                self.screen.blit(self.small_font.render(self.feedback[:110], True, (45, 105, 70)), (65, 540))
        pygame.display.flip()

    def step(self):
        """Process one event batch and render one frame (also useful in tests)."""
        for event in pygame.event.get():
            self.handle_event(event)
        self.draw()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.step()
        pygame.quit()


if __name__ == "__main__":
    Task4Demo().run()