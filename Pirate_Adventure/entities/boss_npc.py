import os
import pygame


class BossNPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = []
        self.current_sprite = 0.0
        self.frame_speed = 0.12
        self.image = None
        self.rect = pygame.Rect(x, y, 64, 64)
        self.load_sprites()

    def load_sprites(self):
        folder = os.path.join("assets", "boss_npc")
        for i in range(1, 7):
            path = os.path.join(folder, f"boss_{i}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (100, 100))
                self.sprite.append(img)
            except Exception:
                continue

        if self.sprite:
            self.image = self.sprite[int(self.current_sprite)]
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, speed=None):
        if not self.sprite:
            return

        if speed is None:
            speed = self.frame_speed

        self.current_sprite += speed
        if self.current_sprite >= len(self.sprite):
            self.current_sprite = 0.0

        self.image = self.sprite[int(self.current_sprite)]

    def draw(self, screen):
        if not self.image:
            return
        screen.blit(self.image, self.rect.topleft)

    def interact(self, player, boss_area):
        blessed = getattr(player, 'blessed', False)
        if not blessed:
            boss_area.dialog_text = "Boss: You are not ready. Seek blessings first."
            boss_area.dialog_timer = 4000
            return None

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