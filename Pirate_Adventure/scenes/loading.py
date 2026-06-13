import pygame


class LoadingScreen:

    def __init__(self, screen, player_name, next_scene_factory=None, duration=1800, intro_text=None, fade_duration=600):
        self.screen = screen
        self.player_name = player_name
        self.intro_text = intro_text
        self.fade_duration = max(0, int(fade_duration))
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

        if self.intro_text:
            intro_lines = []
            max_width = self.screen_w - 160
            current_line = ""
            for word in self.intro_text.split():
                if current_line:
                    test_line = f"{current_line} {word}"
                else:
                    test_line = word

                if self.small_font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    intro_lines.append(current_line)
                    current_line = word

            if current_line:
                intro_lines.append(current_line)

            line_y = self.screen_h // 2 - 130
            for line in intro_lines:
                intro_rendered = self.small_font.render(line, True, (235, 235, 235))
                self.screen.blit(
                    intro_rendered,
                    intro_rendered.get_rect(center=(self.screen_w // 2, line_y))
                )
                line_y += 36

        if self.fade_duration > 0:
            elapsed = pygame.time.get_ticks() - self.start_time
            fade_start = max(0, self.duration - self.fade_duration)
            if elapsed >= fade_start:
                fade_progress = min(1.0, (elapsed - fade_start) / self.fade_duration)
                alpha = int(255 * fade_progress)
                fade_surface = pygame.Surface((self.screen_w, self.screen_h))
                fade_surface.set_alpha(alpha)
                fade_surface.fill((0, 0, 0))
                self.screen.blit(fade_surface, (0, 0))
