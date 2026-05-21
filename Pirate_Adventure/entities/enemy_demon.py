import os
import pygame


class EnemyDemon:

    def __init__(self, x, y):

        # Animation settings
        self.frame_width = 64
        self.frame_height = 64
        # base animation speed (frames per update increment)
        self.animation_speed = 0.12

        # per-state animation speeds (frames per update)
        # we'll set idle to 10 FPS assuming a 60 FPS main loop -> 10/60 = 0.1667
        self.animation_speeds = {
            "idle": 10.0 / 60.0,
            "attack": 0.12,
            "flying": 0.12,
            "hurt": 0.12,
            "death": 0.12,
        }

        self.frame_index = 0
        self.current_animation = []
        self.last_animation = None

        # Position
        self.image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # Load sheets (use outline versions)
        base = "assets/enemy_demon/with_outline/"
        # prefer individual idle frames if present (demon_idle-1..n)
        self.idle_sheet = None
        idle_seq = []
        for i in range(1, 9):
            path = os.path.join(base, f"demon_idle-{i}.png")
            if os.path.exists(path):
                try:
                    idle_seq.append(pygame.image.load(path).convert_alpha())
                except Exception:
                    continue
            else:
                break

        if not idle_seq:
            try:
                self.idle_sheet = pygame.image.load(base + "IDLE.png").convert_alpha()
            except Exception:
                self.idle_sheet = None
        else:
            # if we loaded separate images, store them in a list and will use directly
            self.idle_seq = idle_seq

        try:
            self.attack_sheet = pygame.image.load(base + "ATTACK.png").convert_alpha()
        except Exception:
            self.attack_sheet = None

        try:
            self.flying_sheet = pygame.image.load(base + "FLYING.png").convert_alpha()
        except Exception:
            self.flying_sheet = None

        try:
            self.hurt_sheet = pygame.image.load(base + "HURT.png").convert_alpha()
        except Exception:
            self.hurt_sheet = None

        try:
            self.death_sheet = pygame.image.load(base + "DEATH.png").convert_alpha()
        except Exception:
            self.death_sheet = None

        # Extract frames
        if hasattr(self, 'idle_seq') and self.idle_seq:
            # center/crop each image to frame size
            frames = []
            for surf in self.idle_seq:
                try:
                    cropped = self.crop_alpha(surf)
                except Exception:
                    cropped = surf
                target = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                x = (self.frame_width - cropped.get_width()) // 2
                y = (self.frame_height - cropped.get_height()) // 2
                target.blit(cropped, (x, y))
                frames.append(target)
            self.idle = frames
        else:
            self.idle = self.load_frames(self.idle_sheet)
        self.attack = self.load_frames(self.attack_sheet)
        self.flying = self.load_frames(self.flying_sheet)
        self.hurt = self.load_frames(self.hurt_sheet)
        self.death = self.load_frames(self.death_sheet)

        # Start state
        self.state = "idle"
        self.current_animation = self.idle if self.idle else [self.image]
        self.image = self.current_animation[0]

    def load_frames(self, sheet):
        if not sheet:
            return []

        frames = []
        sheet_w = sheet.get_width()
        cols = max(1, sheet_w // self.frame_width)

        for i in range(cols):
            frame = sheet.subsurface(
                pygame.Rect(
                    i * self.frame_width,
                    0,
                    self.frame_width,
                    self.frame_height,
                )
            ).copy()
            frames.append(frame)

        return frames

    def set_state(self, state):
        if state == self.state:
            return
        self.state = state
        mapping = {
            "idle": self.idle,
            "attack": self.attack,
            "flying": self.flying,
            "hurt": self.hurt,
            "death": self.death,
        }
        new_anim = mapping.get(state) or self.idle or [self.image]
        if new_anim:
            self.current_animation = new_anim
            self.frame_index = 0
            self.last_animation = None

    def animate(self):
        animation = self.current_animation

        if animation != self.last_animation:
            self.frame_index = 0
            self.last_animation = animation

        # choose per-state speed, fallback to default
        speed = self.animation_speeds.get(self.state, self.animation_speed)

        if len(animation) > 1:
            self.frame_index += speed
            if self.frame_index >= len(animation):
                # loop idle/flying/attack; on death stay on last frame
                if self.state == "death":
                    self.frame_index = len(animation) - 1
                else:
                    self.frame_index = 0

        else:
            self.frame_index = min(self.frame_index, len(animation) - 1)

        old_center = self.rect.center
        self.image = animation[int(self.frame_index)] if animation else self.image
        self.rect = self.image.get_rect(center=old_center)

    def update(self):
        # Placeholder AI could be added here; for now just animate
        self.animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
