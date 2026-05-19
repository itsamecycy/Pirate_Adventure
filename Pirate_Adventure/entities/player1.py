import pygame


class Player:

    def __init__(self, x, y):

        # STATS
        self.speed = 4
        self.run_speed = 7

        # ANIMATION SETTINGS
        self.frame_width = 64
        self.frame_height = 64
        self.animation_speed = 0.15

        self.frame_index = 0

        self.moving = False
        self.running = False
        self.direction = "down"

        # IMPORTANT: store last animation to avoid reset flicker
        self.last_animation = None

        
        # LOAD SHEETS
        self.idle_front_sheet = pygame.image.load(
            "assets/player1/IDLE/idle_down.png"
        ).convert_alpha()

        self.idle_back_sheet = pygame.image.load(
            "assets/player1/IDLE/idle_up.png"
        ).convert_alpha()

        self.idle_left_sheet = pygame.image.load(
            "assets/player1/IDLE/idle_left.png"
        ).convert_alpha()

        self.idle_right_sheet = pygame.image.load(
            "assets/player1/IDLE/idle_right.png"
        ).convert_alpha()

        self.run_front_sheet = pygame.image.load(
            "assets/player1/RUN/run_down.png"
        ).convert_alpha()

        self.run_back_sheet = pygame.image.load(
            "assets/player1/RUN/run_up.png"
        ).convert_alpha()

        self.run_left_sheet = pygame.image.load(
            "assets/player1/RUN/run_left.png"
        ).convert_alpha()

        self.run_right_sheet = pygame.image.load(
            "assets/player1/RUN/run_right.png"
        ).convert_alpha()

        # FRAME EXTRACTION
        self.idle_front = self.load_frames(self.idle_front_sheet)
        self.idle_back = self.load_frames(self.idle_back_sheet)
        self.idle_left = self.load_frames(self.idle_left_sheet)
        self.idle_right = self.load_frames(self.idle_right_sheet)

        self.run_front = self.load_frames(self.run_front_sheet)
        self.run_back = self.load_frames(self.run_back_sheet)
        self.run_left = self.load_frames(self.run_left_sheet)
        self.run_right = self.load_frames(self.run_right_sheet)

        # START STATE
        self.current_animation = self.idle_front
        self.image = self.current_animation[0]

        self.rect = self.image.get_rect(center=(x, y))

    # SAFE FRAME LOADER
    def load_frames(self, sheet):

        frames = []

        for i in range(8):

            frame = sheet.subsurface(
                pygame.Rect(
                    i * self.frame_width,
                    0,
                    self.frame_width,
                    self.frame_height
                )
            ).copy()

            frames.append(frame)

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

        if self.running:

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

    # ANIMATION (FIXED NO FLICKER)
    def animate(self):

        animation = self.get_animation()

        # 🔥 ONLY RESET FRAME IF ANIMATION CHANGED
        if animation != self.last_animation:
            self.frame_index = 0
            self.last_animation = animation

        self.current_animation = animation

        if self.moving:
            self.frame_index += self.animation_speed

            if self.frame_index >= len(animation):
                self.frame_index = 0

        else:
            # keep idle frame stable (NO constant reset flicker)
            self.frame_index = min(self.frame_index, len(animation) - 1)

        old_center = self.rect.center
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

    # UPDATE
    def update(self):

        self.movement()
        self.animate()