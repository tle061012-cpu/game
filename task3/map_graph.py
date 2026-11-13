"""Task 3: Historical Location Graph - Cấu trúc đồ thị địa điểm & Điều kiện mở khóa."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional


class LocationStatus(str, Enum):
    LOCKED = "LOCKED"          # Đang khóa (chưa đủ điều kiện lịch sử)
    UNLOCKED = "UNLOCKED"      # Đã mở khóa (có thể điều tra)
    COMPLETED = "COMPLETED"    # Đã hoàn thành toàn bộ nhiệm vụ


@dataclass
class LocationNode:
    id: int
    key: str
    name: str
    year_period: str
    pos_x: int
    pos_y: int
    description: str
    prerequisites: List[int] = field(default_factory=list)  # Các ID địa điểm phải xong trước


class HistoricalLocationGraph:
    """Đồ thị có hướng (Directed Acyclic Graph) quản lý cây tiến trình lịch sử."""

    def __init__(self):
        self.nodes: Dict[int, LocationNode] = {}
        self.adj_list: Dict[int, List[int]] = {}
        self._init_vietnam_history_graph()

    def _init_vietnam_history_graph(self):
        """Khởi tạo 8 nút địa danh lịch sử nòng cốt từ năm 1911 đến 1954."""
        locations_data = [
            (1, "Ben Nha Rong", "Bến Nhà Rồng (Sài Gòn)", "1911 - 1920", 365, 500,
             "Nguyễn Tất Thành ra đi tìm đường cứu nước.", []),
            (2, "Hong Kong", "Hương Cảng (Hong Kong)", "1930", 525, 203,
             "Thành lập Đảng Cộng sản Việt Nam.", [1]),
            (3, "Vinh - Ben Thuy", "Vinh - Bến Thủy (Nghệ An)", "1930 - 1931", 336, 277,
             "Phong trào Xô viết Nghệ - Tĩnh anh dũng.", [2]),
            (4, "Pac Bo", "Hang Pác Bó (Cao Bằng)", "1941", 325, 180,
             "Lãnh tụ Nguyễn Ái Quốc về nước lãnh đạo cách mạng.", [3]),
            (5, "Tan Trao", "Tân Trào (Tuyên Quang)", "1945", 300, 201,
             "Đại hội Quốc dân Tân Trào phát lệnh Tổng khởi nghĩa.", [4]),
            (6, "Ba Dinh", "Quảng trường Ba Đình (Hà Nội)", "1945", 350, 224,
             "Bác Hồ đọc Tuyên ngôn Độc lập khai sinh nước VNDCCH.", [5]),
            (7, "Viet Bac", "Chiến khu Việt Bắc", "1947 - 1950", 329, 207,
             "Căn cứ địa kháng chiến toàn quốc chống thực dân Pháp.", [6]),
            (8, "Dien Bien Phu", "Điện Biên Phủ", "1954", 273, 217,
             "Chiến thắng Điện Biên Phủ 'Lừng lẫy năm châu, chấn động địa cầu'.", [7]),
            (9, "Dinh Doc Lap", "Dinh Độc Lập (Sài Gòn)", "1975", 380, 505,
             "Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam.", [8]),
        ]

        for loc_id, key, name, period, x, y, desc, prereqs in locations_data:
            node = LocationNode(
                id=loc_id,
                key=key,
                name=name,
                year_period=period,
                pos_x=x,
                pos_y=y,
                description=desc,
                prerequisites=prereqs,
            )
            self.nodes[loc_id] = node
            self.adj_list[loc_id] = []

        # Xây dựng danh sách kề (Edges)
        for loc_id, node in self.nodes.items():
            for p_id in node.prerequisites:
                if p_id in self.adj_list:
                    self.adj_list[p_id].append(loc_id)

    def get_status(self, node_id: int, completed_nodes: Set[int]) -> LocationStatus:
        """Kiểm tra trạng thái của một nút địa danh dựa trên các nút đã hoàn thành."""
        if node_id in completed_nodes:
            return LocationStatus.COMPLETED

        node = self.nodes.get(node_id)
        if not node:
            return LocationStatus.LOCKED

        # Nếu không có điều kiện tiên quyết -> Mở mặc định
        if not node.prerequisites:
            return LocationStatus.UNLOCKED

        # Mốc Điện Biên Phủ (8) mở khi hoàn thành Ba Đình (6) hoặc Việt Bắc (7)
        if node_id == 8:
            if 6 in completed_nodes or 7 in completed_nodes:
                return LocationStatus.UNLOCKED

        # Nếu tất cả các nút tiên quyết đều đã hoàn thành -> Mở khóa
        if all(p in completed_nodes for p in node.prerequisites):
            return LocationStatus.UNLOCKED

        return LocationStatus.LOCKED

    def get_next_available_locations(self, completed_nodes: Set[int]) -> List[LocationNode]:
        """Lấy danh sách các địa danh đang mở khóa nhưng chưa hoàn thành."""
        res = []
        for loc_id, node in self.nodes.items():
            if self.get_status(loc_id, completed_nodes) == LocationStatus.UNLOCKED:
                res.append(node)
        return res
