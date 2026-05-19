import pygame


class LoadingScreen:

    def __init__(self, screen, player_name, next_scene_factory=None, duration=1800):
        self.screen = screen
        self.player_name = player_name
        # optional callable returning the next scene instance
        self.next_scene_factory = next_scene_factory
        self.screen_w, self.screen_h = self.screen.get_size()

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            60
        )

        self.small_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            28
        )

        self.start_time = pygame.time.get_ticks()
        self.duration = duration

    # INPUT
    def handle_events(self, event):
        return None

    # UPDATE
    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time

        if elapsed >= self.duration:
            # if a factory was provided, create and switch to that scene
            if callable(self.next_scene_factory):
                try:
                    next_scene = self.next_scene_factory()
                    return ("switch_scene", next_scene)
                except Exception:
                    return "loading_done"
            return "loading_done"

        return None

    # DRAW
    def draw(self):
        self.screen.fill((8, 18, 40))

        self.screen_w, self.screen_h = self.screen.get_size()
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1.0, elapsed / self.duration)

        title = self.font.render(
            "Preparing adventure...",
            True,
            (143, 205, 217)
        )

        self.screen.blit(
            title,
            title.get_rect(center=(self.screen_w // 2, self.screen_h // 2 - 60))
        )

        player_text = self.small_font.render(
            f"Captain {self.player_name}",
            True,
            (205, 235, 255)
        )

        self.screen.blit(
            player_text,
            player_text.get_rect(center=(self.screen_w // 2, self.screen_h // 2 + 10))
        )

        bar_width = min(600, self.screen_w - 200)
        bar_height = 26
        bar_x = (self.screen_w - bar_width) // 2
        bar_y = self.screen_h // 2 + 80

        pygame.draw.rect(self.screen, (40, 55, 90), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            self.screen,
            (143, 205, 217),
            (bar_x, bar_y, int(bar_width * progress), bar_height)
        )

        percent_text = self.small_font.render(
            f"{int(progress * 100)}% loaded",
            True,
            (210, 230, 255)
        )

        self.screen.blit(
            percent_text,
            percent_text.get_rect(center=(self.screen_w // 2, bar_y + 45))
        )
