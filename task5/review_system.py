"""
================================================================================
TASK 5: REVIEW SYSTEM (HỆ THỐNG ÔN TẬP VÀ KIỂM CHỨNG TƯ LIỆU SỬ HỌC)
================================================================================
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    MASTERED = "MASTERED"


class ReviewQuestion:
    """Mô hình dữ liệu cho một câu hỏi cần ôn tập và tra cứu tư liệu."""

    def __init__(
        self,
        question_id: str,
        location_name: str,
        question_text: str,
        options: List[str],
        correct_index: int,
        user_choice: int,
        explanation: str,
        source_title: str = "Tư liệu Lịch sử Việt Nam",
        source_author: str = "Nhiều tác giả",
        source_publisher: str = "NXB Giáo dục",
        source_citation: str = "Tài liệu chính thống",
        status: ReviewStatus = ReviewStatus.PENDING,
        retry_count: int = 0,
    ):
        self.id = question_id
        self.location_name = location_name
        self.question = question_text
        self.options = options
        self.correct_index = correct_index
        self.user_choice = user_choice
        self.explanation = explanation
        self.source_title = source_title
        self.source_author = source_author
        self.source_publisher = source_publisher
        self.source_citation = source_citation
        self.status = status if isinstance(status, ReviewStatus) else ReviewStatus(status)
        self.retry_count = retry_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "location_name": self.location_name,
            "question": self.question,
            "options": self.options,
            "correct_index": self.correct_index,
            "user_choice": self.user_choice,
            "explanation": self.explanation,
            "source_title": self.source_title,
            "source_author": self.source_author,
            "source_publisher": self.source_publisher,
            "source_citation": self.source_citation,
            "status": self.status.value,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewQuestion":
        return cls(
            question_id=data.get("id", ""),
            location_name=data.get("location_name", ""),
            question_text=data.get("question", ""),
            options=data.get("options", []),
            correct_index=data.get("correct_index", 0),
            user_choice=data.get("user_choice", 0),
            explanation=data.get("explanation", ""),
            source_title=data.get("source_title", "Tư liệu Lịch sử Việt Nam"),
            source_author=data.get("source_author", "Nhiều tác giả"),
            source_publisher=data.get("source_publisher", "NXB Giáo dục"),
            source_citation=data.get("source_citation", "Tài liệu chính thống"),
            status=ReviewStatus(data.get("status", "PENDING")),
            retry_count=data.get("retry_count", 0),
        )


class RetryResult:
    def __init__(self, is_correct: bool, message: str = ""):
        self.is_correct = is_correct
        self.message = message


class ReviewManager:
    """Quản lý các câu hỏi ôn tập và tiến trình lưu trữ."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (
            Path(__file__).resolve().parent.parent / "data" / "review_progress.json"
        )
        self.questions: Dict[str, ReviewQuestion] = {}
        self.load_progress()

    def record_mistake(
        self,
        question_id: str,
        location_name: str,
        question_text: str,
        options: List[str],
        correct_index: int,
        user_choice: int,
        explanation: str,
        source_title: str = "Tư liệu Lịch sử Việt Nam",
        source_author: str = "Nhiều tác giả",
        source_publisher: str = "NXB Giáo dục",
        source_citation: str = "Tài liệu chính thống",
    ):
        if question_id in self.questions:
            q = self.questions[question_id]
            q.user_choice = user_choice
            q.retry_count += 1
            q.status = ReviewStatus.PENDING
        else:
            q = ReviewQuestion(
                question_id=question_id,
                location_name=location_name,
                question_text=question_text,
                options=options,
                correct_index=correct_index,
                user_choice=user_choice,
                explanation=explanation,
                source_title=source_title,
                source_author=source_author,
                source_publisher=source_publisher,
                source_citation=source_citation,
                status=ReviewStatus.PENDING,
                retry_count=1,
            )
            self.questions[question_id] = q
        self.save_progress()

    def get_pending_questions(self) -> List[ReviewQuestion]:
        return [q for q in self.questions.values() if q.status == ReviewStatus.PENDING]

    def get_mastered_questions(self) -> List[ReviewQuestion]:
        return [q for q in self.questions.values() if q.status == ReviewStatus.MASTERED]

    def retry_answer(self, question_id: str, choice_index: int) -> RetryResult:
        if question_id not in self.questions:
            return RetryResult(False, "Không tìm thấy câu hỏi")

        q = self.questions[question_id]
        q.user_choice = choice_index
        q.retry_count += 1

        if choice_index == q.correct_index:
            q.status = ReviewStatus.MASTERED
            self.save_progress()
            return RetryResult(True, "Chính xác!")
        else:
            self.save_progress()
            return RetryResult(False, "Chưa chính xác")

    def load_progress(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for qid, qdata in data.items():
                        self.questions[qid] = ReviewQuestion.from_dict(qdata)
            except Exception:
                pass

    def save_progress(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                data = {qid: q.to_dict() for qid, q in self.questions.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

