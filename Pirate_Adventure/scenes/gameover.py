import pygame


class GameOver:

    def __init__(self, screen, next_scene=None):
        self.screen = screen
        self.screen_w, self.screen_h = self.screen.get_size()
        self.next_scene = next_scene

        self.title_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            80
        )
        self.text_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            40
        )

        self.blink_timer = 0
        self.show_prompt = True

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_scene is not None:
                return ("switch_scene", self.next_scene)
            return "back_to_menu"
        return None

    def update(self):
        self.blink_timer += 1
        if self.blink_timer >= 60:
            self.blink_timer = 0
            self.show_prompt = not self.show_prompt
        return None

    def draw(self):
        self.screen.fill((78, 42, 58))
        self.screen_w, self.screen_h = self.screen.get_size()

        for y in range(0, self.screen_h, 80):
            pygame.draw.rect(self.screen, (110, 60, 70), (0, y, self.screen_w, 20))
            pygame.draw.rect(self.screen, (140, 80, 70), (0, y + 40, self.screen_w, 15))

        title = self.title_font.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(
            title,
            title.get_rect(center=(self.screen_w // 2, 130))
        )

        if self.show_prompt:
            prompt = self.text_font.render(
                "Press any button to continue",
                True,
                (255, 255, 255)
            )
            self.screen.blit(
                prompt,
                prompt.get_rect(center=(self.screen_w // 2, 450))
            )
