import os
import pygame
from entities.boss import BossNPC


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

        # place boss NPC near the upper center
        boss_x = self.screen_w // 2
        boss_y = int(self.screen_h * 0.3)
        self.boss = BossNPC(boss_x, boss_y)

        # transient dialog display
        self.dialog_text = None
        self.dialog_timer = 0

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
            if event.key == pygame.K_e:
                # interact with boss if colliding
                try:
                    if hasattr(self, 'boss') and self.player.rect.colliderect(self.boss.rect):
                        res = self.boss.interact(self.player, self)
                        if res:
                            return res
                except Exception:
                    pass
        # mouse click interaction
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                if hasattr(self, 'boss') and self.boss.rect.collidepoint(event.pos):
                    res = self.boss.interact(self.player, self)
                    if res:
                        return res
            except Exception:
                pass
        return None

    def update(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        self.player.update()

        try:
            if hasattr(self, 'boss'):
                self.boss.update()
        except Exception:
            pass

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

        # dialog timer
        if getattr(self, 'dialog_timer', 0) > 0:
            self.dialog_timer -= 16
            if self.dialog_timer <= 0:
                self.dialog_text = None
                self.dialog_timer = 0

        return None

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((18, 10, 14))

        self.screen.blit(self.player.image, self.player.rect)

        try:
            if hasattr(self, 'boss'):
                self.boss.draw(self.screen)
        except Exception:
            pass

        title_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 40)
        text = title_font.render("Boss Area", True, (230, 190, 130))
        self.screen.blit(text, text.get_rect(center=(self.screen_w // 2, 50)))

        hint_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 22)
        hint = hint_font.render("Move to the bottom center to return", True, (210, 210, 210))
        self.screen.blit(hint, hint.get_rect(center=(self.screen_w // 2, self.screen_h - 20)))

        # draw dialog text if present
        if getattr(self, 'dialog_text', None):
            font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 30)
            text = getattr(self, 'dialog_text', '')
            txt = font.render(text, True, (240, 240, 240))
            rect = txt.get_rect(center=(self.screen_w // 2, 80))
            panel_w = min(self.screen_w - 120, rect.width + 40)
            panel_h = rect.height + 24
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((6, 6, 12, 220))
            pygame.draw.rect(panel, (120, 140, 170, 220), panel.get_rect(), 2)
            panel_x = (self.screen_w - panel_w) // 2
            panel_y = rect.y - 12
            self.screen.blit(panel, (panel_x, panel_y))
            txt_rect = txt.get_rect(center=(panel_x + panel_w // 2, panel_y + panel_h // 2))
            self.screen.blit(txt, txt_rect)
