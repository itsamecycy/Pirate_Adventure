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
        # event dialog queue for centered warnings
        self.event_dialog_queue = []
        self.event_dialog = None
        # pending encounter and encounter animation state
        self.pending_encounter = None
        self.encounter_anim = None

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

        # event dialog queue handling
        if self.event_dialog is None and self.event_dialog_queue:
            item = self.event_dialog_queue.pop(0)
            self.event_dialog = {
                'text': item.get('text'),
                'duration': item.get('duration', 3000),
                'fade_duration': item.get('fade_duration', 500),
                'delay': item.get('delay', 0),
                'timer': item.get('duration', 3000) if item.get('delay', 0) == 0 else 0,
            }

        if self.event_dialog is not None:
            if self.event_dialog['delay'] > 0:
                self.event_dialog['delay'] = max(0, self.event_dialog['delay'] - 16)
                if self.event_dialog['delay'] == 0:
                    self.event_dialog['timer'] = self.event_dialog['duration']
            elif self.event_dialog['timer'] > 0:
                self.event_dialog['timer'] = max(0, self.event_dialog['timer'] - 16)
                if self.event_dialog['timer'] == 0:
                    self.event_dialog = None

        # update encounter animation if present
        if self.encounter_anim is not None:
            self.encounter_anim['timer'] = self.encounter_anim.get('timer', 0) + 16
            if self.encounter_anim['timer'] >= self.encounter_anim.get('duration', 1200):
                # start battle now
                enemy = self.encounter_anim.get('enemy')
                from scenes.battle import BattleScene
                target_scene = getattr(self, 'return_scene', self)
                if hasattr(target_scene, 'return_scene'):
                    target_scene = getattr(target_scene, 'return_scene', target_scene)
                battle = BattleScene(self.screen, self.player_name, self.player, enemy, target_scene, boss_npc=getattr(self, 'boss', None))
                # clear anim state
                self.encounter_anim = None
                self.pending_encounter = None
                return ("switch_scene", battle)

        return None

    def start_encounter(self, enemy, duration=1200, fade_in=300, hold=600, fade_out=300):
        # begin boss encounter animation and delay battle creation
        self.pending_encounter = enemy
        self.encounter_anim = {
            'enemy': enemy,
            'timer': 0,
            'duration': duration,
            'fade_in': fade_in,
            'hold': hold,
            'fade_out': fade_out,
        }

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

        # draw centered event dialog (large warning) if present and delay elapsed
        if getattr(self, 'event_dialog', None) and self.event_dialog.get('delay', 0) == 0:
            font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 44)
            text = self.event_dialog['text']
            txt = font.render(text, True, (255, 230, 160)).convert_alpha()
            alpha = 255
            if self.event_dialog['duration'] > 0:
                fade = self.event_dialog.get('fade_duration', 500)
                elapsed = self.event_dialog['duration'] - self.event_dialog['timer']
                if fade > 0 and elapsed < fade:
                    alpha = int(255 * elapsed / fade)
                elif fade > 0 and self.event_dialog['timer'] < fade:
                    alpha = int(255 * self.event_dialog['timer'] / fade)
            alpha = max(0, min(255, alpha))
            txt.set_alpha(alpha)
            # shadow
            shadow = font.render(text, True, (18, 14, 12)).convert_alpha()
            shadow.set_alpha(max(0, alpha - 120))
            cx, cy = self.screen_w // 2, self.screen_h // 2
            shadow_rect = shadow.get_rect(center=(cx + 6, cy + 6))
            txt_rect = txt.get_rect(center=(cx, cy))
            # backdrop with reduced opacity, no border
            backdrop = pygame.Surface((txt_rect.width + 40, txt_rect.height + 24), pygame.SRCALPHA)
            backdrop.fill((6, 6, 12, min(150, alpha)))
            back_rect = backdrop.get_rect(center=(cx, cy))
            self.screen.blit(backdrop, back_rect.topleft)
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(txt, txt_rect)

        # draw encounter animation overlay if present
        if self.encounter_anim is not None:
            anim = self.encounter_anim
            t = anim.get('timer', 0)
            fi = anim.get('fade_in', 300)
            hold = anim.get('hold', 600)
            fo = anim.get('fade_out', 300)
            total = anim.get('duration', fi + hold + fo)
            if t < fi:
                alpha = int(255 * (t / max(1, fi)))
            elif t < fi + hold:
                alpha = 255
            else:
                alpha = int(255 * max(0, (total - t) / max(1, fo)))
            alpha = max(0, min(255, alpha))

            overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            overlay.fill((6, 6, 12, int(180 * (alpha / 255))))
            self.screen.blit(overlay, (0, 0))

            enemy = anim.get('enemy')
            name = getattr(enemy.__class__, '__name__', 'Boss')
            try:
                img = getattr(enemy, 'image', None)
                if img:
                    scale = min(self.screen_w * 0.5 / img.get_width(), self.screen_h * 0.5 / img.get_height(), 1.4)
                    scaled = pygame.transform.smoothscale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    rect = scaled.get_rect(center=(self.screen_w // 2, self.screen_h // 2 - 30))
                    tmp = scaled.copy().convert_alpha()
                    tmp.set_alpha(alpha)
                    self.screen.blit(tmp, rect)
            except Exception:
                pass

            try:
                font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 48)
                txt = font.render(f"A wild {name} appears!", True, (255, 230, 160))
                txt.set_alpha(alpha)
                self.screen.blit(txt, txt.get_rect(center=(self.screen_w // 2, self.screen_h // 2 + 120)))
            except Exception:
                pass
