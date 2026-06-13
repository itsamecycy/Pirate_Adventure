import os
import pygame
from systems.inventorysys import InventorySystem


class Player:
    def __init__(self, x, y):
        # STATS
        self.speed = 4
        self.run_speed = 7

        # FRAME / ANIMATION
        self.frame_width = 64
        self.frame_height = 64
        self.scale = 1.1
        self.image_width = int(self.frame_width * self.scale)
        self.image_height = int(self.frame_height * self.scale)
        self.animation_speed = 0.15
        self.frame_index = 0.0

        self.moving = False
        self.running = False
        self.direction = "down"
        self.last_animation = None

        # load idle sheets (horizontal strip of 8 frames expected)
        self.idle_front_sheet = pygame.image.load(os.path.join("assets", "player1", "IDLE", "idle_down.png")).convert_alpha()
        self.idle_back_sheet = pygame.image.load(os.path.join("assets", "player1", "IDLE", "idle_up.png")).convert_alpha()
        self.idle_left_sheet = pygame.image.load(os.path.join("assets", "player1", "IDLE", "idle_left.png")).convert_alpha()
        self.idle_right_sheet = pygame.image.load(os.path.join("assets", "player1", "IDLE", "idle_right.png")).convert_alpha()

        # directional run frames from separate files
        run_folder = os.path.join("assets", "player1", "RUN")
        self.run_front = self.load_run_frames(run_folder, "rundown")
        self.run_back = self.load_run_frames(run_folder, "runup")
        self.run_left = self.load_run_frames(run_folder, "runleft")
        self.run_right = self.load_run_frames(run_folder, "runright")

        # slice idle frames from sheets
        self.idle_front = self.load_frames(self.idle_front_sheet)
        self.idle_back = self.load_frames(self.idle_back_sheet)
        self.idle_left = self.load_frames(self.idle_left_sheet)
        self.idle_right = self.load_frames(self.idle_right_sheet)

        # fallbacks
        if not self.run_front:
            self.run_front = [pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)]
        if not self.run_back:
            self.run_back = [pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)]
        if not self.run_left:
            self.run_left = [pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)]
        if not self.run_right:
            self.run_right = [pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)]

        # player status / resources
        self.max_hp = 120
        self.hp = 120
        self.max_mp = 40
        self.mp = 40
        self.items = {
            "Potion": 2,
            "Pistol": 1,
            "Cutlass": 1,
        }
        self.skills = ["Fireball"]
        self.status_effects = ["Healthy"]
        self.equipped_weapons = {"gun": None, "sword": None}
        self.attack_power = (12, 20)
        # quest and blessing state
        self.enemy_demon_kills = 0
        self.quest_demon_kills = 0
        self.quest_active = False
        self.blessed = False
        self.quest_rewards_given = False
        self.storm_warning_shown = False
        self.inventory_system = InventorySystem(self)

        # start state
        self.current_animation = self.idle_front
        self.image = self.current_animation[0]
        self.rect = self.image.get_rect(center=(x, y))

    def load_frames(self, sheet):
        frames = []
        for i in range(8):
            rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            try:
                frame = sheet.subsurface(rect).copy()
                frame = pygame.transform.smoothscale(frame, (self.image_width, self.image_height))
            except Exception:
                frame = pygame.Surface((self.image_width, self.image_height), pygame.SRCALPHA)
            frames.append(frame)
        return frames

    def crop_alpha(self, surface):
        width, height = surface.get_size()
        minx, miny, maxx, maxy = width, height, 0, 0
        for x in range(width):
            for y in range(height):
                if surface.get_at((x, y)).a != 0:
                    minx = min(minx, x)
                    miny = min(miny, y)
                    maxx = max(maxx, x)
                    maxy = max(maxy, y)
        if maxx < minx or maxy < miny:
            return surface.copy()
        return surface.subsurface(pygame.Rect(minx, miny, maxx - minx + 1, maxy - miny + 1)).copy()

    def load_run_frames(self, folder, prefix, count=8):
        frames = []
        for i in range(1, count + 1):
            path = os.path.join(folder, f"{prefix}-{i}.png")
            if not os.path.exists(path):
                continue
            try:
                frame = pygame.image.load(path).convert_alpha()
                frame = self.crop_alpha(frame)
                # center cropped frame onto fixed-size surface
                target = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                x = (self.frame_width - frame.get_width()) // 2
                y = (self.frame_height - frame.get_height()) // 2
                target.blit(frame, (x, y))
                target = pygame.transform.smoothscale(target, (self.image_width, self.image_height))
                frames.append(target)
            except Exception:
                continue
        if not frames:
            frames = [pygame.Surface((self.image_width, self.image_height), pygame.SRCALPHA)]
        return frames

    # MOVEMENT
    def movement(self):
        keys = pygame.key.get_pressed()

        self.moving = False
        self.running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        speed = self.run_speed if self.running else self.speed

        if keys[pygame.K_a]:
            self.rect.x -= speed
            self.direction = "left"
            self.moving = True
        elif keys[pygame.K_d]:
            self.rect.x += speed
            self.direction = "right"
            self.moving = True
        elif keys[pygame.K_w]:
            self.rect.y -= speed
            self.direction = "up"
            self.moving = True
        elif keys[pygame.K_s]:
            self.rect.y += speed
            self.direction = "down"
            self.moving = True

    # GET CURRENT ANIMATION
    def get_animation(self):
        if self.moving:
            if self.direction == "left":
                return self.run_left
            elif self.direction == "right":
                return self.run_right
            elif self.direction == "up":
                return self.run_back
            else:
                return self.run_front
        else:
            if self.direction == "left":
                return self.idle_left
            elif self.direction == "right":
                return self.idle_right
            elif self.direction == "up":
                return self.idle_back
            else:
                return self.idle_front

    def equip_weapon(self, weapon_name):
        return self.inventory_system.equip_weapon(weapon_name)

    def unequip_weapon(self, weapon_name=None):
        return self.inventory_system.unequip_weapon(weapon_name)

    def get_equipped_weapons(self):
        return self.equipped_weapons

    # ANIMATION
    def animate(self):
        animation = self.get_animation()

        if animation != self.last_animation:
            self.frame_index = 0.0
            self.last_animation = animation

        if self.moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0.0
        else:
            self.frame_index = min(self.frame_index, len(animation) - 1)

        old_center = self.rect.center
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

    # UPDATE
    def update(self):
        self.movement()
        self.animate()
