"""Quest state and timeline progression for Task 4."""


class QuestManager:
    LOCKED = "locked"
    AVAILABLE = "available"
    INVESTIGATING = "investigating"
    QUIZ = "quiz"
    COMPLETED = "completed"

    def __init__(self, locations, completed=None, progress=None):
        self.locations = sorted(locations, key=lambda item: (item.get("start", 0), item.get("id", 0)))
        self.states = {location["name"]: self.LOCKED for location in self.locations}
        self.completed = set(completed or ())
        self.collected_clues = {location["name"]: set() for location in self.locations}
        self.quiz_attempts = {location["name"]: 0 for location in self.locations}
        self.quiz_passed = set()
        self.score = 0
        self.location_ids = {location["name"]: location.get("id") for location in self.locations}
        self._saved_progress = {
            int(location_id): saved
            for location_id, saved in (progress or {}).items()
        }
        for location in self.locations:
            name = location["name"]
            saved = self._saved_progress.get(self.location_ids[name], {})
            self.collected_clues[name].update(saved.get("clue_ids", set()))
            self.quiz_attempts[name] = int(saved.get("quiz_attempts", 0))
        self._refresh_unlocks()

    def _refresh_unlocks(self):
        previous_complete = True
        for location in self.locations:
            name = location["name"]
            if name in self.completed:
                self.states[name] = self.COMPLETED
            elif name == "Dien Bien Phu" and ("Ba Dinh" in self.completed or "Viet Bac" in self.completed):
                # Hoàn thành Ba Đình (hoặc Việt Bắc) là mở khóa ngay Lòng chảo Điện Biên Phủ
                if self._has_saved_clues(location):
                    self.states[name] = self.QUIZ
                else:
                    self.states[name] = self.AVAILABLE
            elif name in self.states and self._has_saved_clues(location):
                if previous_complete:
                    self.states[name] = self.QUIZ
                else:
                    self.states[name] = self.LOCKED
                previous_complete = False
            elif self.states.get(name) in (self.INVESTIGATING, self.QUIZ):
                previous_complete = False
            elif previous_complete:
                self.states[name] = self.AVAILABLE
                previous_complete = False
            else:
                self.states[name] = self.LOCKED

    def _has_saved_clues(self, location):
        saved = self._saved_progress.get(location.get("id"), {})
        return bool(saved.get("clue_ids"))

    def state(self, location):
        name = location if isinstance(location, str) else location.get("name")
        return self.states.get(name, self.LOCKED)

    def start(self, location):
        name = location if isinstance(location, str) else location["name"]
        if self.states.get(name) != self.QUIZ:
            self.states[name] = self.INVESTIGATING
        return True

    def clues_complete(self, location):
        name = location if isinstance(location, str) else location["name"]
        self.states[name] = self.QUIZ

    def collect_clue(self, location, clue_id, required_clue_ids):
        """Record a clue once and unlock the quiz when all required clues exist."""
        name = location["name"]
        if self.state(name) not in (self.INVESTIGATING, self.QUIZ):
            return False
        if clue_id not in required_clue_ids:
            return False
        self.collected_clues.setdefault(name, set()).add(clue_id)
        if set(required_clue_ids).issubset(self.collected_clues[name]):
            self.states[name] = self.QUIZ
        return True

    def clue_progress(self, location, required_clue_ids):
        name = location if isinstance(location, str) else location["name"]
        required = set(required_clue_ids)
        collected = self.collected_clues.get(name, set())
        return len(required & collected), len(required)

    def restore_location_progress(self, location, clue_ids=(), quiz_attempts=0, required_clue_ids=()):
        name = location["name"]
        valid_ids = set(required_clue_ids)
        self.collected_clues[name] = set(clue_ids) & valid_ids
        self.quiz_attempts[name] = max(0, int(quiz_attempts))
        if (
            valid_ids
            and valid_ids.issubset(self.collected_clues[name])
            and name not in self.completed
            and self.state(name) != self.LOCKED
        ):
            self.states[name] = self.QUIZ

    def export_location_progress(self, location):
        
            self.states[name] = self.QUIZ

    def export_location_progress(self, location):
        name = location["name"]
        return {
            "clue_ids": set(self.collected_clues.get(name, set())),
            "quiz_attempts": self.quiz_attempts.get(name, 0),
        }

    def record_quiz_answer(self, location, correct):
        """Track quiz attempts; return points awarded for a correct answer."""
        name = location["name"]
        if self.state(name) != self.QUIZ:
            return 0
        self.quiz_attempts[name] = self.quiz_attempts.get(name, 0) + 1
        if correct:
            self.quiz_passed.add(name)
        return 100 if correct else 0

    def complete(self, location):
        name = location if isinstance(location, str) else location["name"]
        if self.state(name) != self.QUIZ or name not in self.quiz_passed:
            return False
        self.completed.add(name)
        self._refresh_unlocks()
        return True

    def timeline(self):
        return [
            {
                "name": location["name"],
                "year": location.get("start"),
                "state": self.state(location),
                "clues": len(self.collected_clues.get(location["name"], set())),
                "attempts": self.quiz_attempts.get(location["name"], 0),
            }
            for location in self.locations
        ]
