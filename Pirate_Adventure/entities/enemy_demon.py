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

        # Load sheets using outline assets when available, otherwise fallback to without_outline.
        base_dir = os.path.join("assets", "enemy_demon")
        self.base = os.path.join(base_dir, "with_outline")
        self.alt_base = os.path.join(base_dir, "without_outline")
        if not os.path.isdir(self.base):
            self.base = self.alt_base

        def load_sheet(filename):
            for folder in (self.base, self.alt_base):
                path = os.path.join(folder, filename)
                if not os.path.exists(path):
                    continue
                try:
                    return pygame.image.load(path).convert_alpha()
                except Exception:
                    continue
            return None

        # prefer individual idle frames if present (demon_idle-1..n)
        self.idle_sheet = None
        idle_seq = []
        for i in range(1, 9):
            path = os.path.join(self.base, f"demon_idle-{i}.png")
            if os.path.exists(path):
                try:
                    idle_seq.append(pygame.image.load(path).convert_alpha())
                except Exception:
                    continue
            else:
                break

        if not idle_seq:
            self.idle_sheet = load_sheet("IDLE.png")
        else:
            # if we loaded separate images, store them in a list and will use directly
            self.idle_seq = idle_seq

        self.attack_sheet = load_sheet("ATTACK.png")
        self.flying_sheet = load_sheet("FLYING.png")
        self.hurt_sheet = load_sheet("HURT.png")
        self.death_sheet = load_sheet("DEATH.png")

        # Extract raw frames from each animation group and normalize them to a stable centered size.
        raw_idle = self.extract_raw_frames(self.idle_sheet, getattr(self, 'idle_seq', None))
        raw_attack = self.extract_raw_frames(self.attack_sheet)
        raw_flying = self.extract_raw_frames(self.flying_sheet)
        raw_hurt = self.extract_raw_frames(self.hurt_sheet)
        raw_death = self.extract_raw_frames(self.death_sheet)

        all_frames = [*raw_idle, *raw_attack, *raw_flying, *raw_hurt, *raw_death]
        target_width = max((frame.get_width() for frame in all_frames), default=self.frame_width)
        target_height = max((frame.get_height() for frame in all_frames), default=self.frame_height)
        self.frame_width = target_width
        self.frame_height = target_height

        self.idle = [self.center_frame(frame, target_width, target_height) for frame in raw_idle]
        self.attack = [self.center_frame(frame, target_width, target_height) for frame in raw_attack]
        self.flying = [self.center_frame(frame, target_width, target_height) for frame in raw_flying]
        self.hurt = [self.center_frame(frame, target_width, target_height) for frame in raw_hurt]
        self.death = [self.center_frame(frame, target_width, target_height) for frame in raw_death]

        # Start state
        self.state = "idle"
        self.current_animation = self.idle if self.idle else [self.image]
        self.image = self.current_animation[0]
        self.rect = self.image.get_rect(center=self.rect.center)

    def extract_raw_frames(self, sheet, frame_list=None):
        frames = []
        if frame_list:
            for surf in frame_list:
                try:
                    frames.append(self.crop_alpha(surf))
                except Exception:
                    frames.append(pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA))
            return frames

        if sheet:
            return self.frames_from_sheet(sheet)

        return []

    def frames_from_sheet(self, sheet):
        rects = self.get_frame_rects(sheet)
        frames = []
        for rect in rects:
            try:
                frame = sheet.subsurface(rect).copy()
                frames.append(self.crop_alpha(frame))
            except Exception:
                continue
        return frames

    def get_frame_rects(self, sheet):
        w, h = sheet.get_size()
        is_transparent = [
            all(sheet.get_at((x, y)).a == 0 for y in range(h))
            for x in range(w)
        ]
        rects = []
        start = None
        for x, empty in enumerate(is_transparent):
            if not empty and start is None:
                start = x
            if empty and start is not None:
                rects.append(pygame.Rect(start, 0, x - start, h))
                start = None
        if start is not None:
            rects.append(pygame.Rect(start, 0, w - start, h))
        return rects

    def center_frame(self, frame, width, height):
        target = pygame.Surface((width, height), pygame.SRCALPHA)
        x = (width - frame.get_width()) // 2
        y = (height - frame.get_height()) // 2
        target.blit(frame, (x, y))
        return target

    def load_frames(self, sheet):
        return self.frames_from_sheet(sheet)

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

    def is_animation_finished(self):
        if not self.current_animation:
            return True
        return int(self.frame_index) >= len(self.current_animation) - 1

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
                if self.state in ("idle", "flying"):
                    self.frame_index = 0
                else:
                    self.frame_index = len(animation) - 1

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
