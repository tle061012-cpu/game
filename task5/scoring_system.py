"""
================================================================================
TASK 5: SCORING SYSTEM (ĐỘNG CƠ TÍNH ĐIỂM, XẾP HẠNG VÀ DANH HIỆU HỌC GIẢ)
================================================================================
"""

from typing import Dict, Any


class ScoringEngine:
    """Hệ thống đánh giá điểm tri thức và xếp loại học giả lịch sử."""

    def __init__(self, initial_score: int = 0):
        self.total_score = initial_score
        self.review_rewards: Dict[str, int] = {}

    def calculate_rank(self, score: int) -> str:
        """Xếp hạng học giả theo thang điểm S, A, B, C, D."""
        if score >= 500:
            return "S"
        elif score >= 350:
            return "A"
        elif score >= 200:
            return "B"
        elif score >= 100:
            return "C"
        return "D"

    def get_rank_title(self, score: int) -> str:
        """Danh hiệu học thuật tương ứng với mức điểm."""
        rank = self.calculate_rank(score)
        titles = {
            "S": "Sử Gia Lỗi Lạc (Hạng S)",
            "A": "Bác Học Lịch Sử (Hạng A)",
            "B": "Nhà Nghiên Cứu Lịch Sử (Hạng B)",
            "C": "Học Giả Khám Phá (Hạng C)",
            "D": "Tập Sự Sử Học (Hạng D)",
        }
        return titles.get(rank, "Tập Sự Sử Học")

    def record_review_reward(self, question_id: str, points: int = 15) -> int:
        """Cộng điểm khi ôn tập thành công một câu hỏi trước đó từng làm sai."""
        if question_id not in self.review_rewards:
            self.review_rewards[question_id] = points
            self.total_score += points
            return points
        return 0

    def export_summary(self) -> Dict[str, Any]:
        """Xuất báo cáo tổng kết điểm và thứ hạng của người chơi."""
        return {
            "total_score": self.total_score,
            "rank": self.calculate_rank(self.total_score),
            "rank_title": self.get_rank_title(self.total_score),
            "review_bonus_points": sum(self.review_rewards.values()),
        }

    def export_certificate(self, player_name: str = "Học giả Lịch Sử", output_path: str = None) -> str:
        """Xuất Bằng Chứng Nhận vinh danh học giả thành file ảnh nghệ thuật (PNG)."""
        import os
        import datetime
        import pygame

        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        width, height = 1000, 680
        cert = pygame.Surface((width, height))

        # 1. Nền giấy cổ điển
        BG_COLOR = (253, 249, 238)
        GOLD = (195, 145, 30)
        RED = (175, 32, 42)
        DARK = (45, 40, 35)
        MUTED = (115, 110, 100)
        cert.fill(BG_COLOR)

        # 2. Khung viền kép hoa văn
        pygame.draw.rect(cert, GOLD, pygame.Rect(20, 20, width - 40, height - 40), 4, border_radius=12)
        pygame.draw.rect(cert, RED, pygame.Rect(32, 32, width - 64, height - 64), 2, border_radius=8)

        # Góc trang trí
        corner_len = 30
        for cx, cy in [(32, 32), (width - 32, 32), (32, height - 32), (width - 32, height - 32)]:
            pygame.draw.circle(cert, GOLD, (cx, cy), 8)
            pygame.draw.circle(cert, RED, (cx, cy), 4)

        # 3. Phông chữ
        font_large = pygame.font.SysFont("segoeui,arial,timesnewroman", 32, bold=True)
        font_sub = pygame.font.SysFont("segoeui,arial,timesnewroman", 16, bold=True)
        font_name = pygame.font.SysFont("segoeui,arial,timesnewroman", 36, bold=True)
        font_body = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        font_rank = pygame.font.SysFont("segoeui,arial,timesnewroman", 24, bold=True)
        font_small = pygame.font.SysFont("segoeui,arial,timesnewroman", 14, italic=True)

        # 4. Quốc hiệu
        t_vn = font_sub.render("DỰ ÁN GIÁO DỤC LỊCH SỬ VIỆT NAM — NHÓM 11", True, DARK)
        cert.blit(t_vn, t_vn.get_rect(center=(width // 2, 65)))
        line_w = 260
        pygame.draw.line(cert, GOLD, (width // 2 - line_w // 2, 85), (width // 2 + line_w // 2, 85), 2)

        # 5. Tiêu đề Chứng chỉ
        title = font_large.render("CHỨNG NHẬN VINH DANH HỌC GIẢ LỊCH SỬ", True, RED)
        cert.blit(title, title.get_rect(center=(width // 2, 135)))

        sub = font_body.render("Chứng nhận thành tích khám phá và giải mã các mốc son lịch sử dân tộc", True, MUTED)
        cert.blit(sub, sub.get_rect(center=(width // 2, 180)))

        # 6. Tên người chơi
        cert_for = font_body.render("Trân trọng trao tặng Học giả:", True, DARK)
        cert.blit(cert_for, cert_for.get_rect(center=(width // 2, 235)))

        name_surf = font_name.render(player_name.upper(), True, RED)
        cert.blit(name_surf, name_surf.get_rect(center=(width // 2, 280)))

        # Đường gạch chân tên học giả
        name_w = name_surf.get_width() + 60
        pygame.draw.line(cert, GOLD, (width // 2 - name_w // 2, 310), (width // 2 + name_w // 2, 310), 3)

        # 7. Danh hiệu & Điểm số
        summary = self.export_summary()
        rank_text = f"Đạt Danh Hiệu: {summary['rank_title']}"
        rank_surf = font_rank.render(rank_text, True, GOLD)
        cert.blit(rank_surf, rank_surf.get_rect(center=(width // 2, 350)))

        score_desc = f"Tổng điểm tri thức tích lũy: {summary['total_score']} Điểm  |  Hạng: {summary['rank']}"
        score_surf = font_body.render(score_desc, True, DARK)
        cert.blit(score_surf, score_surf.get_rect(center=(width // 2, 395)))

        desc = font_body.render("Đã hoàn thành xuất sắc các nhiệm vụ điều tra thực địa, giải mã chuỗi thời gian", True, DARK)
        cert.blit(desc, desc.get_rect(center=(width // 2, 440)))
        desc2 = font_body.render("và củng cố vững chắc tri thức lịch sử hào hùng của Tổ quốc Việt Nam.", True, DARK)
        cert.blit(desc2, desc2.get_rect(center=(width // 2, 470)))

        # 8. Con dấu mô phỏng & Ngày ký
        today_str = datetime.date.today().strftime("Ngày %d tháng %m năm %Y")
        date_surf = font_small.render(f"Hà Nội, {today_str}", True, MUTED)
        cert.blit(date_surf, (width - 320, 530))

        sign_title = font_sub.render("HỘI ĐỒNG THẨM ĐỊNH LỊCH SỬ", True, DARK)
        cert.blit(sign_title, (width - 335, 555))

        # Dấu tròn đỏ
        seal_center = (width - 240, 615)
        pygame.draw.circle(cert, RED, seal_center, 36, 3)
        pygame.draw.circle(cert, RED, seal_center, 30, 1)
        seal_txt = pygame.font.SysFont("segoeui,arial", 11, bold=True).render("ĐÃ KIỂM CHỨNG", True, RED)
        cert.blit(seal_txt, seal_txt.get_rect(center=seal_center))

        # 9. Lưu file ra đĩa
        if not output_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_path = os.path.join(base_dir, "data", "chung_nhan_hoc_gia.png")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pygame.image.save(cert, output_path)
        return output_path


