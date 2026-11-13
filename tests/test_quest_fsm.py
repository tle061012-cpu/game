"""Unit Test Suite cho Task 4: Quest FSM, Inventory, Timeline Deduction & Quiz.

Kiểm thử toàn diện 7 khía cạnh then chốt:
1. Vòng đời chuyển trạng thái FSM (LOCKED -> IN_PROGRESS -> DEDUCTION -> COMPLETED).
2. Cơ chế chống gian lận (Anti-cheat & Anti-skip).
3. Xác minh bàn suy luận Timeline với ô trống và ô sai thứ tự.
4. Thao tác di chuyển, hoán đổi (swap), gỡ thẻ (remove) và đặt lại (reset) trên bàn chơi.
5. Tính bất biến (Immutability) và xác thực dữ liệu của Thẻ manh mối (Clue).
6. Quy chuẩn hệ thống Quiz ôn tập (30 điểm/câu, thứ tự tuần tự, nguồn sử liệu).
7. Tính toàn vẹn của bộ dữ liệu Timeline cho cả 4 mốc lịch sử lớn (Pác Bó, Ba Đình, Điện Biên Phủ, Dinh Độc Lập).
"""

import os
import sys
import unittest

# Đảm bảo đường dẫn import tương thích môi trường
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"

from task4.quest_system import (
    Clue,
    ClueInventory,
    DeductionTimelineBoard,
    QuestState,
    QuestStateMachine,
    QuizSystem,
)
from task4.timeline_data import TIMELINE_QUEST_CONFIGS


class TestQuestFSMAndTimeline(unittest.TestCase):
    def setUp(self):
        """Khởi tạo bộ dữ liệu mẫu chuẩn cho từng test case."""
        self.sample_clues = [
            Clue("clue_stage0", "Sự kiện Bối cảnh", "lời khai", "Chi tiết bối cảnh", "Nguồn 1", 0),
            Clue("clue_stage1", "Sự kiện Chủ trương", "văn kiện", "Chi tiết chủ trương", "Nguồn 2", 1),
            Clue("clue_stage2", "Sự kiện Diễn biến", "hiện vật", "Chi tiết diễn biến", "Nguồn 3", 2),
            Clue("clue_stage3", "Sự kiện Kết quả", "văn kiện", "Chi tiết kết quả", "Nguồn 4", 3),
        ]
        self.required_ids = [c.id for c in self.sample_clues]
        self.machine = QuestStateMachine(self.required_ids)
        self.inventory = ClueInventory()
        for c in self.sample_clues:
            self.inventory.add(c)
        self.board = DeductionTimelineBoard(self.inventory, self.machine)

    def test_fsm_normal_lifecycle(self):
        """1. Kiểm tra vòng đời chuẩn của Quest FSM."""
        # Ban đầu: LOCKED
        self.assertEqual(self.machine.state, QuestState.LOCKED)
        self.assertFalse(self.machine.timeline_verified)
        self.assertFalse(self.machine.quiz_completed)

        # Bắt đầu quest -> IN_PROGRESS
        self.assertTrue(self.machine.start())
        self.assertEqual(self.machine.state, QuestState.IN_PROGRESS)

        # Thu thập dần manh mối
        self.assertTrue(self.machine.collect_clue("clue_stage0"))
        self.assertEqual(self.machine.state, QuestState.IN_PROGRESS)

        self.assertTrue(self.machine.collect_clue("clue_stage1"))
        self.assertTrue(self.machine.collect_clue("clue_stage2"))
        self.assertEqual(self.machine.state, QuestState.IN_PROGRESS)

        # Thu thập đủ manh mối -> Tự động chuyển DEDUCTION_PHASE
        self.assertTrue(self.machine.collect_clue("clue_stage3"))
        self.assertEqual(self.machine.state, QuestState.DEDUCTION_PHASE)

        # Xác thực timeline đúng
        self.assertTrue(self.machine.complete_timeline(True))
        self.assertTrue(self.machine.timeline_verified)

        # Hoàn thành Quiz
        self.assertTrue(self.machine.mark_quiz_completed())
        self.assertTrue(self.machine.quiz_completed)

        # Hoàn thành toàn bộ Quest -> COMPLETED
        self.assertTrue(self.machine.complete())
        self.assertEqual(self.machine.state, QuestState.COMPLETED)

    def test_anti_cheat_state_skipping(self):
        """2. Cơ chế chống nhảy cóc trạng thái (Anti-cheat/Anti-skip)."""
        # Không thể nhặt manh mối khi chưa start (đang LOCKED)
        self.assertFalse(self.machine.collect_clue("clue_stage0"))

        # Không thể hoàn thành khi đang LOCKED
        self.assertFalse(self.machine.complete())

        # Start quest
        self.machine.start()
        # Không thể hoàn thành khi đang IN_PROGRESS
        self.assertFalse(self.machine.complete())

        # Nhặt manh mối không thuộc danh sách yêu cầu
        self.assertFalse(self.machine.collect_clue("fake_clue_id"))

        # Thu thập đủ manh mối để sang DEDUCTION_PHASE
        for cid in self.required_ids:
            self.machine.collect_clue(cid)
        self.assertEqual(self.machine.state, QuestState.DEDUCTION_PHASE)

        # Chưa xác thực timeline -> Không thể đánh dấu quiz xong hay complete
        self.assertFalse(self.machine.mark_quiz_completed())
        self.assertFalse(self.machine.complete())

        # Timeline sai -> Vẫn không thể hoàn thành
        self.machine.complete_timeline(False)
        self.assertFalse(self.machine.complete())

        # Timeline đúng nhưng chưa làm Quiz -> Vẫn không thể hoàn thành
        self.machine.complete_timeline(True)
        self.assertFalse(self.machine.complete())

    def test_board_verification_empty_or_wrong_slots(self):
        """3. Bàn suy luận Timeline kiểm tra ô trống và ô sai thứ tự."""
        # 1. Bàn chưa xếp thẻ nào (toàn bộ ô trống)
        self.assertFalse(self.board.check())
        self.assertIn("Còn ô trống", self.board.message)
        self.assertFalse(self.board.verified)

        # 2. Xếp thiếu (chỉ có 2 ô)
        self.board.place("clue_stage0", 0)
        self.board.place("clue_stage1", 1)
        self.assertFalse(self.board.check())
        self.assertIn("Còn ô trống", self.board.message)

        # 3. Xếp đủ 4 ô nhưng SAI thứ tự logic nhân - quả
        self.board.place("clue_stage3", 2)
        self.board.place("clue_stage2", 3)
        self.assertFalse(self.board.check())
        self.assertIn("MÂU THUẪN LỊCH SỬ", self.board.message)
        self.assertFalse(self.board.verified)

        # 4. Xếp ĐÚNG thứ tự 4 giai đoạn nhân - quả: 0 -> 1 -> 2 -> 3
        self.board.place("clue_stage0", 0)
        self.board.place("clue_stage1", 1)
        self.board.place("clue_stage2", 2)
        self.board.place("clue_stage3", 3)

        # Cho FSM sang DEDUCTION_PHASE trước khi check
        self.machine.start()
        for cid in self.required_ids:
            self.machine.collect_clue(cid)

        self.assertTrue(self.board.check())
        self.assertTrue(self.board.verified)
        self.assertIn("ĐÃ XÁC THỰC LỊCH SỬ", self.board.message)

    def test_board_swap_remove_reset(self):
        """4. Kiểm tra các tương tác: đổi chỗ (swap), gỡ (remove), đặt lại (reset)."""
        # Đặt vào ô 0 và ô 1
        self.board.place("clue_stage0", 0)
        self.board.place("clue_stage1", 1)
        self.assertEqual(self.board.slots[0], "clue_stage0")
        self.assertEqual(self.board.slots[1], "clue_stage1")

        # Hoán đổi ô 0 và ô 1
        self.assertTrue(self.board.swap(0, 1))
        self.assertEqual(self.board.slots[0], "clue_stage1")
        self.assertEqual(self.board.slots[1], "clue_stage0")

        # Gỡ mảnh ghép khỏi ô 0
        removed = self.board.remove(0)
        self.assertEqual(removed, "clue_stage1")
        self.assertIsNone(self.board.slots[0])

        # Đặt lại toàn bộ
        self.board.place("clue_stage2", 2)
        self.board.reset()
        self.assertEqual(self.board.slots, [None, None, None, None])
        self.assertFalse(self.board.verified)

    def test_clue_immutability(self):
        """5. Tính bất biến (frozen=True) và tính hợp lệ của Clue."""
        clue = self.sample_clues[0]

        # Kiểm tra tính bất biến: gán lại trường phải ném ra Exception
        with self.assertRaises((Exception, AttributeError)):
            clue.title = "Tiêu đề bị sửa trái phép"

        with self.assertRaises((Exception, AttributeError)):
            clue.timeline_stage = 3

        # Kiểm tra validate khi khởi tạo Clue không hợp lệ
        with self.assertRaises(ValueError):
            Clue("", "Tiêu đề", "lời khai", "Chi tiết", "Nguồn", 0)  # ID rỗng

        with self.assertRaises(ValueError):
            Clue("c1", "Tiêu đề", "lời khai", "Chi tiết", "", 0)  # Thiếu nguồn

        with self.assertRaises(ValueError):
            Clue("c1", "Tiêu đề", "lời khai", "Chi tiết", "Nguồn", 5)  # Stage ngoài 0..3

    def test_quiz_system(self):
        """6. Hệ thống Quiz: thứ tự tuần tự và chuẩn +30 điểm/câu."""
        questions = [
            {"id": "q1", "question": "Câu 1?", "options": ["A", "B", "C", "D"], "answer": 1, "explanation": "G1", "source": "N1"},
            {"id": "q2", "question": "Câu 2?", "options": ["A", "B", "C", "D"], "answer": 2, "explanation": "G2", "source": "N2"},
            {"id": "q3", "question": "Câu 3?", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "G3", "source": "N3"},
        ]
        quiz = QuizSystem(questions)

        # Trả lời sai thứ tự (nhảy cóc sang câu 2) -> ném ValueError
        with self.assertRaises(ValueError):
            quiz.answer(1, 0)

        # Trả lời đúng câu 1 -> nhận đúng +30 điểm
        res1 = quiz.answer(0, 1)
        self.assertTrue(res1["correct"])
        self.assertEqual(res1["points"], 30)
        self.assertEqual(quiz.score, 30)

        # Trả lời sai câu 2 -> nhận 0 điểm
        res2 = quiz.answer(1, 0)
        self.assertFalse(res2["correct"])
        self.assertEqual(res2["points"], 0)
        self.assertEqual(quiz.score, 30)

        # Trả lời đúng câu 3 -> nhận +30 điểm, tổng 60 điểm
        res3 = quiz.answer(2, 0)
        self.assertTrue(res3["correct"])
        self.assertEqual(res3["points"], 30)
        self.assertEqual(quiz.score, 60)

    def test_all_timeline_locations_dataset(self):
        """7. Kiểm tra tính toàn vẹn của cả 4 địa điểm Timeline trong TIMELINE_QUEST_CONFIGS."""
        expected_locations = ["Pac Bo", "Ba Dinh", "Dien Bien Phu", "Dinh Doc Lap"]

        for loc_name in expected_locations:
            self.assertIn(loc_name, TIMELINE_QUEST_CONFIGS, f"Thiếu cấu hình timeline cho {loc_name}")
            config = TIMELINE_QUEST_CONFIGS[loc_name]

            # Kiểm tra 4 manh mối tương ứng đúng 4 giai đoạn 0, 1, 2, 3
            clues = config["clues"]
            self.assertEqual(len(clues), 4, f"{loc_name} phải có đúng 4 thẻ manh mối")
            stages = [c.timeline_stage for c in clues]
            self.assertEqual(stages, [0, 1, 2, 3], f"{loc_name} các giai đoạn phải là [0, 1, 2, 3]")

            for c in clues:
                self.assertTrue(len(c.title) > 0)
                self.assertTrue(len(c.source) > 0, f"Clue {c.id} của {loc_name} thiếu nguồn trích dẫn")

            # Kiểm tra 3 câu hỏi trắc nghiệm
            questions = config["questions"]
            self.assertEqual(len(questions), 3, f"{loc_name} phải có đúng 3 câu hỏi trắc nghiệm")
            for q in questions:
                self.assertEqual(len(q["options"]), 4, f"Câu hỏi {q.get('id')} phải có đúng 4 lựa chọn")
                self.assertIn(q["answer"], range(4), f"Đáp án câu {q.get('id')} phải trong 0..3")
                self.assertTrue(len(q["explanation"]) > 0)
                self.assertTrue(len(q["source"]) > 0)


if __name__ == "__main__":
    unittest.main()

