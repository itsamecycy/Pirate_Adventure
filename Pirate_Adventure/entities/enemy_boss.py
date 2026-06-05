import os
import pygame


class EnemyBoss:

    def __init__(self, x, y):

        self.frame_width = 64
        self.frame_height = 64

        self.animation_speed = 0.10
        self.frame_index = 0
        self.current_animation = []
        self.last_animation = None

        # Boss stats
        self.max_hp = 200
        self.hp = 200

        self.max_mp = 9999
        self.mp = 9999

        self.attack_power = (18, 30)

        self.image = pygame.Surface(
            (self.frame_width, self.frame_height),
            pygame.SRCALPHA
        )

        self.rect = self.image.get_rect(center=(x, y))

        # Load idle frames
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
            pygame.Rect(
                minx,
                miny,
                maxx - minx + 1,
                maxy - miny + 1
            )
        ).copy()

    def animate(self):

        if self.current_animation != self.last_animation:
            self.frame_index = 0
            self.last_animation = self.current_animation

        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0

        old_center = self.rect.center

        self.image = self.current_animation[
            int(self.frame_index)
        ]

        self.rect = self.image.get_rect(
            center=old_center
        )

    def update(self):
        self.animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)