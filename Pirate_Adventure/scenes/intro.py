import os
import pygame


class IntroScene:
    """Full-screen cinematic intro shown once when starting a new game."""

    LINES = [
        "",
        "The Golden Age of Pirates...",
        "",
        "The seas are lawless.",
        "Empires crumble. Thieves become kings.",
        "",
        "One name strikes fear across every ocean...",
        "",
        "BLACKBEARD.",
        "",
        "His fleet rules the waters,",
        "and none who challenge him return alive.",
        "",
        "But every tyrant's reign must end.",
        "",
        "Your journey begins now, Captain.",
    ]

    def __init__(self, screen, player_name, next_scene_factory=None):
        self.screen = screen
        self.player_name = player_name
        self.next_scene_factory = next_scene_factory
        self.screen_w, self.screen_h = self.screen.get_size()

        self.title_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 52)
        self.text_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 32)
        self.hint_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 22)

        # Boss image for the intro
        self.boss_image = None
        try:
            path = os.path.join("assets", "boss_npc", "boss_1.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # Scale to a reasonable display size
                scale = min(220 / img.get_width(), 280 / img.get_height(), 1.0)
                self.boss_image = pygame.transform.smoothscale(
                    img,
                    (int(img.get_width() * scale), int(img.get_height() * scale)),
                )
        except Exception:
            pass

        # Typewriter state
        self.current_line = 0
        self.char_index = 0
        self.displayed_lines = []  # list of fully-typed strings
        self.typing_line = ""
        self.char_timer = 0.0
        self.chars_per_second = 28
        self.line_pause = 0.0  # pause between lines
        self.line_pause_duration = 0.35

        # Fade-in
        self.fade_alpha = 255
        self.fade_speed = 4

        # Done state
        self.finished_typing = False
        self.done_timer = 0.0
        self.auto_advance_delay = 2.5  # seconds after last line before auto-advance

        self.start_ticks = pygame.time.get_ticks()

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                # If still typing, skip to fully displayed
                if not self.finished_typing:
                    self._skip_to_end()
                    return None
                # If already done, advance
                return self._advance()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.finished_typing:
                self._skip_to_end()
                return None
            return self._advance()
        return None

    def _skip_to_end(self):
        """Instantly show all remaining lines."""
        while self.current_line < len(self.LINES):
            self.displayed_lines.append(self.LINES[self.current_line])
            self.current_line += 1
        self.typing_line = ""
        self.finished_typing = True
        self.done_timer = 0.0

    def _advance(self):
        """Transition to the next scene."""
        if callable(self.next_scene_factory):
            try:
                next_scene = self.next_scene_factory()
                return ("switch_scene", next_scene)
            except Exception:
                pass
        return "intro_done"

    def update(self):
        dt = 1 / 60.0  # assume 60 FPS

        # fade in
        if self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)

        if self.finished_typing:
            self.done_timer += dt
            if self.done_timer >= self.auto_advance_delay:
                return self._advance()
            return None

        # pause between lines
        if self.line_pause > 0:
            self.line_pause -= dt
            return None

        # typewriter effect
        if self.current_line < len(self.LINES):
            line = self.LINES[self.current_line]
            if self.char_index < len(line):
                self.char_timer += dt
                chars_to_add = int(self.char_timer * self.chars_per_second)
                if chars_to_add > 0:
                    self.char_timer -= chars_to_add / self.chars_per_second
                    self.char_index = min(len(line), self.char_index + chars_to_add)
                    self.typing_line = line[: self.char_index]
            else:
                # Line complete
                self.displayed_lines.append(line)
                self.typing_line = ""
                self.char_index = 0
                self.char_timer = 0.0
                self.current_line += 1
                self.line_pause = self.line_pause_duration

                if self.current_line >= len(self.LINES):
                    self.finished_typing = True
                    self.done_timer = 0.0

        return None

    def draw(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        self.screen.fill((6, 6, 14))

        # Subtle vignette overlay
        vignette = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        for i in range(60):
            alpha = int(80 * (1 - i / 60))
            pygame.draw.rect(
                vignette,
                (0, 0, 0, alpha),
                (i, i, self.screen_w - 2 * i, self.screen_h - 2 * i),
                1,
            )
        self.screen.blit(vignette, (0, 0))

        # Boss image on the right side, semi-transparent
        if self.boss_image:
            boss_alpha = max(0, min(180, 180 - self.fade_alpha))
            boss_copy = self.boss_image.copy()
            boss_copy.set_alpha(boss_alpha)
            bx = self.screen_w - self.boss_image.get_width() - 80
            by = self.screen_h // 2 - self.boss_image.get_height() // 2
            self.screen.blit(boss_copy, (bx, by))

            # Boss name label under image
            if boss_alpha > 60:
                label = self.hint_font.render("Blackbeard", True, (200, 160, 80))
                label.set_alpha(boss_alpha)
                self.screen.blit(
                    label,
                    label.get_rect(
                        center=(
                            bx + self.boss_image.get_width() // 2,
                            by + self.boss_image.get_height() + 20,
                        )
                    ),
                )

        # Draw text on the left-center area
        text_x = 120
        text_max_x = self.screen_w - 320 if self.boss_image else self.screen_w - 120
        start_y = max(80, self.screen_h // 2 - len(self.LINES) * 18)

        y = start_y
        for i, line in enumerate(self.displayed_lines):
            if line == "":
                y += 14
                continue
            # Special styling for BLACKBEARD
            if line.strip() == "BLACKBEARD.":
                surf = self.title_font.render(line, True, (220, 170, 60))
                shadow = self.title_font.render(line, True, (80, 50, 10))
                self.screen.blit(shadow, (text_x + 2, y + 2))
                self.screen.blit(surf, (text_x, y))
                y += 50
            else:
                color = (220, 215, 200)
                surf = self.text_font.render(line, True, color)
                self.screen.blit(surf, (text_x, y))
                y += 36

        # Currently typing line
        if self.typing_line:
            line = self.typing_line
            if self.current_line < len(self.LINES) and self.LINES[self.current_line].strip() == "BLACKBEARD.":
                surf = self.title_font.render(line, True, (220, 170, 60))
                shadow = self.title_font.render(line, True, (80, 50, 10))
                self.screen.blit(shadow, (text_x + 2, y + 2))
                self.screen.blit(surf, (text_x, y))
            else:
                surf = self.text_font.render(line, True, (220, 215, 200))
                self.screen.blit(surf, (text_x, y))

        # Hint at bottom
        if self.finished_typing:
            hint = self.hint_font.render(
                "Press ENTER to begin your adventure...", True, (160, 160, 160)
            )
            # Blink effect
            ticks = pygame.time.get_ticks()
            if (ticks // 600) % 2 == 0:
                self.screen.blit(
                    hint, hint.get_rect(center=(self.screen_w // 2, self.screen_h - 50))
                )
        else:
            hint = self.hint_font.render(
                "Press ENTER to skip", True, (100, 100, 100)
            )
            self.screen.blit(
                hint, hint.get_rect(center=(self.screen_w // 2, self.screen_h - 50))
            )

        # Fade-in overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((self.screen_w, self.screen_h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surf, (0, 0))
