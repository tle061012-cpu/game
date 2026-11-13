"""
================================================================================
SCENES/BASE_SCENE.PY - LỚP CƠ SỞ VÀ QUẢN LÝ CẢNH THEO MẪU THIẾT KẾ STATE PATTERN
================================================================================
Cung cấp khung kiến trúc Hướng đối tượng (OOP) chuẩn cho toàn bộ các màn hình
trong game (Login, Map, Investigation, Deduction, Review, v.v.).
Loại bỏ tình trạng "God Class" và quản lý phân tán các màn hình.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pygame


class BaseScene(ABC):
    """Lớp cha trừu tượng cho mọi Cảnh (Scene) trong Game."""

    def __init__(self, name: str = "BaseScene"):
        self.name = name
        self.manager: Optional["SceneManager"] = None

    def on_enter(self, **kwargs):
        """Được gọi tự động khi người chơi bước vào Cảnh này."""
        pass

    def on_exit(self):
        """Được gọi tự động khi Cảnh này kết thúc và chuẩn bị đổi cảnh."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Xử lý sự kiện bàn phím, chuột riêng của Cảnh.
        
        Trả về một chuỗi lệnh điều hướng (nếu có), ví dụ: 'map', 'quit', 'deduction'.
        """
        pass

    def update(self, dt: float = 0.0):
        """Cập nhật logic thời gian, hoạt ảnh chuyển động theo Delta-Time (giây)."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Vẽ toàn bộ thành phần giao diện của Cảnh lên màn hình."""
        pass


class SceneManager:
    """Bộ điều phối cảnh (Scene Manager) theo mô hình State & Stack."""

    def __init__(self):
        self._scenes: Dict[str, BaseScene] = {}
        self._current_scene: Optional[BaseScene] = None
        self._scene_stack: list[BaseScene] = []

    def register(self, name: str, scene: BaseScene):
        """Đăng ký một Cảnh vào hệ thống."""
        scene.manager = self
        self._scenes[name] = scene

    @property
    def current(self) -> Optional[BaseScene]:
        return self._current_scene

    @property
    def current_name(self) -> str:
        return self._current_scene.name if self._current_scene else ""

    def change_scene(self, name: str, **kwargs):
        """Chuyển sang cảnh mới hoàn toàn."""
        if name not in self._scenes:
            raise KeyError(f"Cảnh '{name}' chưa được đăng ký trong SceneManager.")

        if self._current_scene:
            self._current_scene.on_exit()

        self._current_scene = self._scenes[name]
        self._current_scene.on_enter(**kwargs)

    def push_scene(self, name: str, **kwargs):
        """Đẩy cảnh mới lên đỉnh ngăn xếp (phù hợp cho bảng xác nhận, pop-up)."""
        if name not in self._scenes:
            raise KeyError(f"Cảnh '{name}' chưa được đăng ký.")

        if self._current_scene:
            self._scene_stack.append(self._current_scene)

        self._current_scene = self._scenes[name]
        self._current_scene.on_enter(**kwargs)

    def pop_scene(self):
        """Quay lại cảnh trước đó trong ngăn xếp."""
        if not self._scene_stack:
            return

        if self._current_scene:
            self._current_scene.on_exit()

        self._current_scene = self._scene_stack.pop()

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self._current_scene:
            return self._current_scene.handle_event(event)
        return None

    def update(self, dt: float = 0.0):
        if self._current_scene:
            self._current_scene.update(dt)

    def draw(self, screen: pygame.Surface):
        if self._current_scene:
            self._current_scene.draw(screen)

