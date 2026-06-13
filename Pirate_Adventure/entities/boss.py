import os
import pygame


class EnemyBoss:

    def __init__(self, x, y, screen=None):

        self.x = x
        self.y = y
        self.screen = screen

        self.speed = 2
        self.angle = 0

        self.frame_width = 64
        self.frame_height = 64

        self.animation_speed = 0.10
        self.frame_index = 0

        self.current_animation = []
        self.last_animation = None

        self.max_hp = 500
        self.hp = 500

        self.max_mp = 9999
        self.mp = 9999

        self.attack_power = (50, 70)

        self.damage = 50

        self.target = None
        self.target_distance = None
        self.last_shot_time = None

        self.image = pygame.Surface(
            (self.frame_width, self.frame_height),
            pygame.SRCALPHA
        )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.idle = []

        base = "assets/enemy_boss"

        for i in range(1, 6):
            path = os.path.join(base, f"Pirate5Idle-{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                cropped = self.crop_alpha(img)
                target = pygame.Surface(
                    (self.frame_width, self.frame_height),
                    pygame.SRCALPHA
                )
                xoff = (self.frame_width - cropped.get_width()) // 2
                yoff = (self.frame_height - cropped.get_height()) // 2
                target.blit(cropped, (xoff, yoff))
                self.idle.append(target)

        if not self.idle:
            self.idle.append(
                pygame.Surface(
                    (self.frame_width, self.frame_height),
                    pygame.SRCALPHA
                )
            )

        self.state = "idle"
        self.current_animation = self.idle
        self.image = self.current_animation[0]

    def crop_alpha(self, surface):
        width, height = surface.get_size()
        minx = width
        miny = height
        maxx = 0
        maxy = 0
        found = False
        for x in range(width):
            for y in range(height):
                if surface.get_at((x, y)).a > 0:
                    found = True
                    minx = min(minx, x)
                    miny = min(miny, y)
                    maxx = max(maxx, x)
                    maxy = max(maxy, y)
        if not found:
            return surface
        return surface.subsurface(
            pygame.Rect(minx, miny, maxx - minx + 1, maxy - miny + 1)
        ).copy()

    def animate(self):
        if self.current_animation != self.last_animation:
            self.frame_index = 0
            self.last_animation = self.current_animation
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0
        old_center = self.rect.center
        self.image = self.current_animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

    def update_ai(self, player):
        if player is None:
            return
        if self.target is None:
            self.target = player
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        self.target_distance = (dx * dx + dy * dy) ** 0.5
        if self.target_distance > 0:
            dx /= self.target_distance
            dy /= self.target_distance
            self.x += dx * self.speed
            self.y += dy * self.speed
        self.rect.center = (int(self.x), int(self.y))
        if dx != 0:
            try:
                self.angle = (-180 * (dy / dx)) / 3.141592653589793 + 90
            except ZeroDivisionError:
                pass
        now = pygame.time.get_ticks()
        if self.target_distance < 300 and (
            self.last_shot_time is None
            or now - self.last_shot_time > 2000
        ):
            self.shoot(self.target)
            self.last_shot_time = now

    def shoot(self, target):
        if target is None:
            return
        if not hasattr(target, "hp"):
            return
        target.hp -= self.damage
        if target.hp < 0:
            target.hp = 0

    def update(self, player=None):
        self.animate()
        if player is not None:
            self.update_ai(player)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


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
                    img = pygame.transform.scale(img, (140, 140))
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
        try:
            enemy = EnemyBoss(self.rect.centerx, self.rect.centery, boss_area.screen)

            has_golden = getattr(player, 'items', {}).get("Golden Pistol", 0) > 0
            has_falchion = getattr(player, 'items', {}).get("Falchion Sword", 0) > 0
            if not (has_golden and has_falchion):
                enemy.max_hp = 9999
                enemy.hp = 9999
                enemy.attack_power = (9999, 9999)
                enemy.damage = 9999
                boss_area.dialog_text = "Boss: You are outmatched without the Golden Pistol and Falchion Sword."
                boss_area.dialog_timer = 4000
            else:
                enemy.max_hp = 500
                enemy.hp = 500
                enemy.attack_power = (70, 90)
                enemy.damage = 70

            from scenes.battle import BattleScene
            # If the boss_area can handle encounter animations, ask it to start one
            try:
                if hasattr(boss_area, 'start_encounter'):
                    boss_area.start_encounter(enemy)
                    return None
            except Exception:
                pass
            target_scene = getattr(boss_area, 'return_scene', boss_area)
            if hasattr(target_scene, 'return_scene'):
                target_scene = getattr(target_scene, 'return_scene', target_scene)
            battle = BattleScene(boss_area.screen, boss_area.player_name, player, enemy, target_scene, boss_npc=self)
            return ("switch_scene", battle)
        except Exception:
            boss_area.dialog_text = "Boss: I will not fight now."
            boss_area.dialog_timer = 3000
            return None
