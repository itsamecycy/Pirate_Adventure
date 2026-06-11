import os
import pygame


class BossNPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = []
        self.frame = 0.0
        self.frame_speed = 0.12
        self.rect = pygame.Rect(x, y, 64, 64)
        self.load_sprites()

    def load_sprites(self):
        folder = os.path.join("assets", "boss_npc")
        if not os.path.isdir(folder):
            return
        files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
        files = sorted(files)
        for fname in files:
            try:
                img = pygame.image.load(os.path.join(folder, fname)).convert_alpha()
                try:
                    img = pygame.transform.smoothscale(img, (140, 140))
                except Exception:
                    pass
                self.images.append(img)
            except Exception:
                continue
        if self.images:
            w, h = self.images[0].get_size()
            self.rect = pygame.Rect(self.x - w // 2, self.y - h // 2, w, h)

    def update(self):
        if not self.images:
            return
        self.frame += self.frame_speed
        if self.frame >= len(self.images):
            self.frame = 0.0

    def draw(self, screen):
        if not self.images:
            return
        idx = int(self.frame) % len(self.images)
        img = self.images[idx]
        screen.blit(img, self.rect.topleft)

    def interact(self, player, boss_area):
        # If player is not blessed yet, refuse challenge
        blessed = getattr(player, 'blessed', False)
        if not blessed:
            boss_area.dialog_text = "Boss: You are not ready. Seek blessings first."
            boss_area.dialog_timer = 4000
            return None

        # Start boss battle
        try:
            from entities.enemy_boss import EnemyBoss
            from scenes.battle import BattleScene

            enemy = EnemyBoss(self.rect.centerx, self.rect.centery, boss_area.screen)
            battle = BattleScene(boss_area.screen, boss_area.player_name, player, enemy, boss_area)
            return ("switch_scene", battle)
        except Exception:
            boss_area.dialog_text = "Boss: I will not fight now."
            boss_area.dialog_timer = 3000
            return None
