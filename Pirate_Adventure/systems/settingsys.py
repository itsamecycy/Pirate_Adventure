import pygame


class SettingsSystem:

    def __init__(self, screen, initial_resolution=None, fullscreen=False, volume=100):
        self.screen = screen
        self.fullscreen = fullscreen
        self.available_resolutions = [
            (1280, 720),
            (1600, 900),
            (1920, 1080),
        ]

        if initial_resolution and initial_resolution in self.available_resolutions:
            self.resolution_index = self.available_resolutions.index(initial_resolution)
        else:
            current_size = self.screen.get_size()
            self.resolution_index = (
                self.available_resolutions.index(current_size)
                if current_size in self.available_resolutions
                else 0
            )

        self.volume = max(0, min(100, volume))
        self.apply_display_mode()
        self.set_volume(self.volume)
        # SFX volume (stored separately from music)
        self.sfx_volume = self.volume

    # -------------------------
    # DISPLAY / WINDOW MODE
    # -------------------------
    def current_resolution(self):
        return self.available_resolutions[self.resolution_index]

    def apply_display_mode(self):
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        size = self.current_resolution()
        self.screen = pygame.display.set_mode(size, flags)
        return self.screen

    def change_resolution(self, direction=1):
        self.resolution_index = (
            self.resolution_index + direction
        ) % len(self.available_resolutions)
        return self.apply_display_mode()

    def set_resolution(self, resolution):
        if resolution in self.available_resolutions:
            self.resolution_index = self.available_resolutions.index(resolution)
        return self.apply_display_mode()

    # -------------------------
    # FULLSCREEN
    # -------------------------
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        return self.apply_display_mode()

    def set_fullscreen(self, enabled):
        self.fullscreen = bool(enabled)
        return self.apply_display_mode()

    # -------------------------
    # AUDIO
    # -------------------------
    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        pygame.mixer.music.set_volume(self.volume / 100)
        return self.volume

    def change_volume(self, delta):
        self.volume = max(0, min(100, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume / 100)
        return self.volume

    # -------------------------
    # SFX VOLUME
    # -------------------------
    def set_sfx_volume(self, value):
        self.sfx_volume = max(0, min(100, value))
        return self.sfx_volume

    def change_sfx_volume(self, delta):
        self.sfx_volume = max(0, min(100, self.sfx_volume + delta))
        return self.sfx_volume
