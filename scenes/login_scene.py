import pygame
from services.game_data_service import game_data_service

# Màu sắc giao diện (Đồng bộ với chủ đề trò chơi lịch sử)
BACKGROUND = (245, 239, 220)
CARD_BG = (255, 252, 245)
CARD_BORDER = (200, 185, 160)
RED = (180, 35, 45)
RED_HOVER = (205, 50, 60)
DARK = (50, 45, 40)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
GREEN_HOVER = (55, 145, 95)
GRAY = (180, 175, 165)
LIGHT_GRAY = (240, 238, 232)
BLUE = (50, 100, 170)
GOLD = (210, 150, 30)


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.is_password = is_password
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                return False
            else:
                # Chỉ nhận các ký tự hợp lệ
                if event.unicode and len(self.text) < 35:
                    # Cho phép chữ, số, dấu gạch dưới, khoảng trắng
                    if event.unicode.isprintable():
                        self.text += event.unicode
        return False

    def draw(self, screen, font, small_font):
        # Vẽ nền ô nhập
        bg_col = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, bg_col, self.rect, border_radius=6)

        # Viền ô nhập
        border_col = BLUE if self.active else CARD_BORDER
        border_width = 2 if self.active else 1
        pygame.draw.rect(screen, border_col, self.rect, border_width, border_radius=6)

        # Text hiển thị
        display_str = self.text
        if self.is_password and self.text:
            display_str = "*" * len(self.text)

        if display_str:
            surf = font.render(display_str, True, DARK)
            screen.blit(surf, (self.rect.x + 12, self.rect.y + (self.rect.h - surf.get_height()) // 2))
        elif self.placeholder and not self.active:
            surf = small_font.render(self.placeholder, True, GRAY)
            screen.blit(surf, (self.rect.x + 12, self.rect.y + (self.rect.h - surf.get_height()) // 2))


class LoginScene:
    """
    Màn hình Đăng nhập & Đăng ký tài khoản:
    - Cho phép đăng nhập bằng tài khoản trong bảng `nguoi_dung`.
    - Đăng ký người chơi mới và khởi tạo bản ghi trong bảng `tien_do_choi`.
    - Hỗ trợ chế độ chơi Khách (Guest) nếu không muốn đăng nhập.
    - Lưu & Tải điểm số, danh sách địa điểm đã hoàn thành của từng tài khoản.
    """

    def __init__(self):
        # Fonts (Hỗ trợ tiếng Việt UTF-8 chuẩn trên Windows)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 28, bold=True)
        self.sub_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 18)
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 15)
        self.bold_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 17, bold=True)

        self.mode = "login"  # "login" hoặc "register"
        self.message = ""
        self.message_color = RED

        # Card chứa Form ở trung tâm (1100 x 700)
        self.card_rect = pygame.Rect(310, 110, 480, 500)

        # Tabs chuyển chế độ
        self.tab_login_rect = pygame.Rect(340, 180, 200, 40)
        self.tab_register_rect = pygame.Rect(560, 180, 200, 40)

        # Input fields cho Đăng nhập
        self.input_login_user = InputBox(350, 260, 400, 42, "Nhập tên đăng nhập (vd: hocsinh01)")
        self.input_login_pass = InputBox(350, 335, 400, 42, "Nhập mật khẩu (vd: 123456)", is_password=True)

        # Input fields cho Đăng ký
        self.input_reg_user = InputBox(350, 240, 400, 40, "Tên đăng nhập mới (viết liền, không dấu)")
        self.input_reg_pass = InputBox(350, 305, 400, 40, "Mật khẩu bảo mật", is_password=True)
        self.input_reg_name = InputBox(350, 370, 400, 40, "Họ và tên người chơi (vd: Nguyễn Văn A)")

        # Focus mặc định
        self.input_login_user.active = True

        # Nút hành động
        self.btn_submit = pygame.Rect(350, 410, 400, 46)
        self.btn_guest = pygame.Rect(350, 470, 400, 40)

    def switch_mode(self, new_mode):
        self.mode = new_mode
        self.message = ""
        if self.mode == "login":
            self.input_login_user.active = True
            self.input_login_pass.active = False
            self.btn_submit.y = 410
        else:
            self.input_reg_user.active = True
            self.input_reg_pass.active = False
            self.input_reg_name.active = False
            self.btn_submit.y = 435

    def do_login(self):
        username = self.input_login_user.text.strip()
        password = self.input_login_pass.text.strip()

        if not username or not password:
            self.message = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            self.message_color = RED
            return None

        success, user, progress_or_msg = game_data_service.login(username, password)
        if success:
            self.message = f"Xin chào {user.get('ho_va_ten', username)}!"
            self.message_color = GREEN
            return {
                "action": "login_success",
                "user": user,
                "progress": progress_or_msg
            }
        else:
            self.message = progress_or_msg
            self.message_color = RED
            return None

    def do_register(self):
        username = self.input_reg_user.text.strip()
        password = self.input_reg_pass.text.strip()
        fullname = self.input_reg_name.text.strip()

        if not username or not password or not fullname:
            self.message = "Vui lòng điền đầy đủ tất cả các trường!"
            self.message_color = RED
            return None

        success, user, progress_or_msg = game_data_service.register(username, password, fullname)
        if success:
            self.message = "Đăng ký thành công! Đang vào trò chơi..."
            self.message_color = GREEN
            return {
                "action": "login_success",
                "user": user,
                "progress": progress_or_msg
            }
        else:
            self.message = progress_or_msg
            self.message_color = RED
            return None

    def do_guest(self):
        """Chế độ chơi Khách không cần mật khẩu."""
        guest_user = {
            "ma_nguoi_dung": 0,
            "ten_dang_nhap": "khach",
            "ho_va_ten": "Khách khám phá",
            "vai_tro": "guest"
        }
        guest_progress = {
            "score": 0,
            "current_loc_id": 1,
            "max_year": 1914,
            "completed": set()
        }
        return {
            "action": "login_success",
            "user": guest_user,
            "progress": guest_progress
        }

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Xử lý Click chuột
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Chuyển tab
            if self.tab_login_rect.collidepoint(mouse_pos) and self.mode != "login":
                self.switch_mode("login")
                return None
            elif self.tab_register_rect.collidepoint(mouse_pos) and self.mode != "register":
                self.switch_mode("register")
                return None

            # Bấm nút Thực hiện (Đăng nhập / Đăng ký)
            if self.btn_submit.collidepoint(mouse_pos):
                if self.mode == "login":
                    return self.do_login()
                else:
                    return self.do_register()

            # Bấm nút Chơi Khách
            if self.mode == "login" and self.btn_guest.collidepoint(mouse_pos):
                return self.do_guest()

            # Kích hoạt ô nhập
            if self.mode == "login":
                self.input_login_user.handle_event(event)
                self.input_login_pass.handle_event(event)
            else:
                self.input_reg_user.handle_event(event)
                self.input_reg_pass.handle_event(event)
                self.input_reg_name.handle_event(event)

        # Xử lý Bàn phím
        elif event.type == pygame.KEYDOWN:
            # Phím TAB: Chuyển qua lại giữa các ô nhập
            if event.key == pygame.K_TAB:
                if self.mode == "login":
                    if self.input_login_user.active:
                        self.input_login_user.active = False
                        self.input_login_pass.active = True
                    else:
                        self.input_login_user.active = True
                        self.input_login_pass.active = False
                else:
                    if self.input_reg_user.active:
                        self.input_reg_user.active = False
                        self.input_reg_pass.active = True
                    elif self.input_reg_pass.active:
                        self.input_reg_pass.active = False
                        self.input_reg_name.active = True
                    else:
                        self.input_reg_name.active = False
                        self.input_reg_user.active = True
                return None

            # Phím ENTER: Submit form
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.mode == "login":
                    return self.do_login()
                else:
                    return self.do_register()

            # Gõ phím vào các ô
            if self.mode == "login":
                self.input_login_user.handle_event(event)
                self.input_login_pass.handle_event(event)
            else:
                self.input_reg_user.handle_event(event)
                self.input_reg_pass.handle_event(event)
                self.input_reg_name.handle_event(event)

        return None

    def draw(self, screen):
        screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()

        # 1. TIÊU ĐỀ TRANG TRỌNG
        title = self.title_font.render("GAME LỊCH SỬ VIỆT NAM (1914 - 1954)", True, RED)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 35))

        subtitle = self.sub_font.render("Hệ Thống Xác Thực Người Chơi & Lưu Trữ Tiến Trình", True, DARK)
        screen.blit(subtitle, (screen.get_width() // 2 - subtitle.get_width() // 2, 75))

        # 2. KHUNG NỀN THẺ (CARD CONTAINER)
        pygame.draw.rect(screen, CARD_BG, self.card_rect, border_radius=12)
        pygame.draw.rect(screen, CARD_BORDER, self.card_rect, 2, border_radius=12)

        # 3. THANH TABS CHỌN CHẾ ĐỘ
        login_tab_col = RED if self.mode == "login" else LIGHT_GRAY
        login_text_col = WHITE if self.mode == "login" else DARK
        pygame.draw.rect(screen, login_tab_col, self.tab_login_rect, border_radius=8)
        txt = self.bold_font.render("ĐĂNG NHẬP", True, login_text_col)
        screen.blit(txt, (self.tab_login_rect.centerx - txt.get_width() // 2, self.tab_login_rect.centery - txt.get_height() // 2))

        reg_tab_col = RED if self.mode == "register" else LIGHT_GRAY
        reg_text_col = WHITE if self.mode == "register" else DARK
        pygame.draw.rect(screen, reg_tab_col, self.tab_register_rect, border_radius=8)
        txt = self.bold_font.render("ĐĂNG KÝ MỚI", True, reg_text_col)
        screen.blit(txt, (self.tab_register_rect.centerx - txt.get_width() // 2, self.tab_register_rect.centery - txt.get_height() // 2))

        # 4. VẼ NỘI DUNG FORM
        if self.mode == "login":
            # Nhãn
            lbl_u = self.small_font.render("Tên đăng nhập:", True, DARK)
            screen.blit(lbl_u, (350, 238))
            self.input_login_user.draw(screen, self.font, self.small_font)

            lbl_p = self.small_font.render("Mật khẩu:", True, DARK)
            screen.blit(lbl_p, (350, 313))
            self.input_login_pass.draw(screen, self.font, self.small_font)

            # Nút Đăng nhập
            btn_col = RED_HOVER if self.btn_submit.collidepoint(mouse_pos) else RED
            pygame.draw.rect(screen, btn_col, self.btn_submit, border_radius=8)
            btn_txt = self.bold_font.render("VÀO TRÒ CHƠI", True, WHITE)
            screen.blit(btn_txt, (self.btn_submit.centerx - btn_txt.get_width() // 2, self.btn_submit.centery - btn_txt.get_height() // 2))

            # Nút Chơi Khách
            guest_col = (230, 225, 215) if self.btn_guest.collidepoint(mouse_pos) else LIGHT_GRAY
            pygame.draw.rect(screen, guest_col, self.btn_guest, border_radius=8)
            pygame.draw.rect(screen, CARD_BORDER, self.btn_guest, 1, border_radius=8)
            guest_txt = self.font.render("Chơi với tư cách Khách", True, DARK)
            screen.blit(guest_txt, (self.btn_guest.centerx - guest_txt.get_width() // 2, self.btn_guest.centery - guest_txt.get_height() // 2))

            # Gợi ý tài khoản mẫu từ CSDL
            hint = self.small_font.render("Tài khoản mẫu CSDL: hocsinh01 | Mật khẩu: 123456", True, (110, 105, 95))
            screen.blit(hint, (self.card_rect.centerx - hint.get_width() // 2, 535))

        else:
            # Form Đăng ký
            lbl_u = self.small_font.render("Tên tài khoản:", True, DARK)
            screen.blit(lbl_u, (350, 220))
            self.input_reg_user.draw(screen, self.font, self.small_font)

            lbl_p = self.small_font.render("Mật khẩu:", True, DARK)
            screen.blit(lbl_p, (350, 285))
            self.input_reg_pass.draw(screen, self.font, self.small_font)

            lbl_n = self.small_font.render("Họ và tên người chơi:", True, DARK)
            screen.blit(lbl_n, (350, 350))
            self.input_reg_name.draw(screen, self.font, self.small_font)

            # Nút Đăng ký
            btn_col = GREEN_HOVER if self.btn_submit.collidepoint(mouse_pos) else GREEN
            pygame.draw.rect(screen, btn_col, self.btn_submit, border_radius=8)
            btn_txt = self.bold_font.render("TẠO TÀI KHOẢN MỚI", True, WHITE)
            screen.blit(btn_txt, (self.btn_submit.centerx - btn_txt.get_width() // 2, self.btn_submit.centery - btn_txt.get_height() // 2))

        # 5. THÔNG BÁO LỖI / TRẠNG THÁI
        if self.message:
            msg_surf = self.bold_font.render(self.message, True, self.message_color)
            screen.blit(msg_surf, (self.card_rect.centerx - msg_surf.get_width() // 2, 565))

        # Hướng dẫn phím tắt dưới cùng
        nav_hint = self.small_font.render("Phím TAB: Chuyển ô nhập  |  Phím ENTER: Xác nhận  |  Phím Q: Thoát", True, DARK)
        screen.blit(nav_hint, (screen.get_width() // 2 - nav_hint.get_width() // 2, 640))
