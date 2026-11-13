
import pygame


class QuitScene:
    """Man hinh xac nhan thoat game.

    handle_event tra ve:
      "quit" -> thoat game
      "back" -> quay lai man hinh truoc khi bam Q
    """

    def __init__(self):
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 36, bold=True)
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 22)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)

        self.background = (245, 239, 220)
        self.red = (180, 35, 45)
        self.dark = (50, 45, 40)
        self.white = (255, 255, 255)
        self.green = (45, 125, 80)

        self.yes_button = pygame.Rect(350, 350, 170, 60)
        self.no_button = pygame.Rect(580, 350, 170, 60)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_y):
                return "quit"
            elif event.key in (pygame.K_ESCAPE, pygame.K_n):
                return "back"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.yes_button.collidepoint(event.pos):
                return "quit"

            if self.no_button.collidepoint(event.pos):
                return "back"

        return None

    def draw(self, screen):
        screen.fill(self.background)

        title = self.title_font.render("THOÁT GAME", True, self.red)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 200))

        message = self.font.render(
            "Bạn có chắc chắn muốn thoát game không?",
            True,
            self.dark
        )
        screen.blit(message, (screen.get_width() // 2 - message.get_width() // 2, 270))

        pygame.draw.rect(screen, self.red, self.yes_button, border_radius=10)
        pygame.draw.rect(screen, self.green, self.no_button, border_radius=10)

        yes_text = self.font.render("CÓ", True, self.white)
        no_text = self.font.render("KHÔNG", True, self.white)

        screen.blit(yes_text, (self.yes_button.centerx - yes_text.get_width() // 2, self.yes_button.centery - yes_text.get_height() // 2))
        screen.blit(no_text, (self.no_button.centerx - no_text.get_width() // 2, self.no_button.centery - no_text.get_height() // 2))

        hint = self.small_font.render(
            "Enter / Y: Thoát  |  ESC / N: Ở lại",
            True,
            self.dark
        )
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, 460))
