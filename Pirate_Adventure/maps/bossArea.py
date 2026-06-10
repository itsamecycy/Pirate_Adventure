import os
import pygame


class BossArea:
    def __init__(self, screen, player_name, player_entity, return_scene):
        self.screen = screen
        self.screen_w, self.screen_h = self.screen.get_size()
        self.player_name = player_name
        self.player = player_entity
        self.return_scene = return_scene

        self.background = self.load_background()

        # position the player at the bottom center of the boss area
        self.player.rect.midbottom = (self.screen_w // 2, self.screen_h - 40)

    def load_background(self):
        path = os.path.join("assets", "maps", "boss_area.png")
        try:
            image = pygame.image.load(path).convert()
            return pygame.transform.smoothscale(image, (self.screen_w, self.screen_h))
        except Exception:
            return None

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "pause"
        return None

    def update(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        self.player.update()

        self.player.rect.x = max(0, min(self.player.rect.x, self.screen_w - self.player.rect.width))
        self.player.rect.y = max(0, min(self.player.rect.y, self.screen_h - self.player.rect.height))

        exit_width = 240
        exit_rect = pygame.Rect(
            (self.screen_w - exit_width) // 2,
            self.screen_h - 40,
            exit_width,
            40,
        )

        if self.player.rect.bottom >= self.screen_h - 2 and exit_rect.collidepoint(self.player.rect.centerx, self.player.rect.bottom - 1):
            self.return_scene.player.rect.midtop = (self.screen_w // 2, 40)
            return ("switch_scene", self.return_scene)

        return None

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((18, 10, 14))

        self.screen.blit(self.player.image, self.player.rect)

        title_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 40)
        text = title_font.render("Boss Area", True, (230, 190, 130))
        self.screen.blit(text, text.get_rect(center=(self.screen_w // 2, 50)))

        hint_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 22)
        hint = hint_font.render("Move to the bottom center to return", True, (210, 210, 210))
        self.screen.blit(hint, hint.get_rect(center=(self.screen_w // 2, self.screen_h - 20)))
