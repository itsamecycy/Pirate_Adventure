import pygame
from systems.settingsys import SettingsSystem


class Settings:

    def __init__(self, screen):
        self.screen = screen
        self.settings_system = SettingsSystem(self.screen)
        self.screen_w, self.screen_h = self.settings_system.screen.get_size()

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            50
        )

        self.small_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            36
        )

        self.back_text = self.small_font.render(
            "Back",
            True,
            (255, 255, 255)
        )

        self.back_rect = self.back_text.get_rect(center=(100, 50))

    # INPUT
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.back_rect.collidepoint(mouse_pos):
                    return "back_to_menu"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.settings_system.change_volume(-10)
            elif event.key == pygame.K_e:
                self.settings_system.change_volume(10)
            elif event.key == pygame.K_z:
                self.settings_system.change_sfx_volume(-10)
            elif event.key == pygame.K_x:
                self.settings_system.change_sfx_volume(10)
            elif event.key == pygame.K_a:
                new_screen = self.settings_system.change_resolution(-1)
                self.screen = new_screen
                return ("update_screen", new_screen)
            elif event.key == pygame.K_d:
                new_screen = self.settings_system.change_resolution(1)
                self.screen = new_screen
                return ("update_screen", new_screen)
            elif event.key == pygame.K_f:
                new_screen = self.settings_system.toggle_fullscreen()
                self.screen = new_screen
                return ("update_screen", new_screen)

        return None

    # UPDATE
    def update(self):
        pass

    # DRAW
    def draw(self):
        self.screen.fill((10, 10, 20))

        title = self.font.render(
            "Settings",
            True,
            (143, 205, 217)
        )

        center_x = self.screen.get_width() // 2

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, 120))
        )

        volume_text = self.small_font.render(
            f"Volume: {self.settings_system.volume}%",
            True,
            (255, 255, 255)
        )
        self.screen.blit(volume_text, volume_text.get_rect(center=(center_x, 280)))

        sfx_text = self.small_font.render(
            f"SFX Volume: {getattr(self.settings_system, 'sfx_volume', self.settings_system.volume)}%",
            True,
            (255, 255, 255)
        )
        self.screen.blit(sfx_text, sfx_text.get_rect(center=(center_x, 320)))

        resolution_text = self.small_font.render(
            f"Resolution: {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}",
            True,
            (255, 255, 255)
        )
        self.screen.blit(resolution_text, resolution_text.get_rect(center=(center_x, 340)))

        fullscreen_text = self.small_font.render(
            f"Fullscreen: {'On' if self.settings_system.fullscreen else 'Off'}",
            True,
            (255, 255, 255)
        )
        self.screen.blit(fullscreen_text, fullscreen_text.get_rect(center=(center_x, 400)))

        hint_text = self.small_font.render(
            "Q/E Music  Z/X SFX  A/D Resolution  F Fullscreen",
            True,
            (120, 120, 120)
        )
        self.screen.blit(hint_text, hint_text.get_rect(center=(center_x, 500)))

        mouse_pos = pygame.mouse.get_pos()
        if self.back_rect.collidepoint(mouse_pos):
            color = (255, 255, 255)
        else:
            color = (150, 150, 150)

        self.back_text = self.small_font.render("Back", True, color)
        self.screen.blit(self.back_text, self.back_rect)
