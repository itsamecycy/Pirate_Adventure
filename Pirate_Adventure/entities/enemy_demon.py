import pygame


class EnemyDemon:

    def __init__(self, x, y):

        # Animation settings
        self.frame_width = 64
        self.frame_height = 64
        self.animation_speed = 0.12

        self.frame_index = 0
        self.current_animation = []
        self.last_animation = None

        # Position
        self.image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # Load sheets (use outline versions)
        base = "assets/enemy_demon/with_outline/"
        try:
            self.idle_sheet = pygame.image.load(base + "IDLE.png").convert_alpha()
        except Exception:
            self.idle_sheet = None

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

        if len(animation) > 1:
            self.frame_index += self.animation_speed
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
