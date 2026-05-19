import pygame
from systems.savedata import SaveData
from systems.settingsys import SettingsSystem
from maps.overworld import Overworld


class LoadGame:

    def __init__(self, screen):
        self.screen = screen
        self.screen_w, self.screen_h = self.screen.get_size()

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            50
        )

        self.small_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            36
        )

        self.save_data = SaveData()
        self.selected_slot = 0
        self.status_message = ""
        self.status_timer = 0
        self.slot_rects = []

        self.back_text = self.small_font.render(
            "Back",
            True,
            (255, 255, 255)
        )

        self.back_rect = self.back_text.get_rect(center=(100, 50))

    def set_status(self, text):
        self.status_message = text
        self.status_timer = pygame.time.get_ticks()

    # INPUT
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back_to_menu"
            if event.key == pygame.K_UP:
                self.selected_slot = (self.selected_slot - 1) % self.save_data.slots
                return None
            if event.key == pygame.K_DOWN:
                self.selected_slot = (self.selected_slot + 1) % self.save_data.slots
                return None
            if event.key == pygame.K_RETURN:
                return self.load_selected_slot()
            if event.key == pygame.K_DELETE:
                self.delete_selected_slot()
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for index, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_slot = index
                    return self.load_selected_slot()
            if self.back_rect.collidepoint(mouse_pos):
                return "back_to_menu"

        return None

    def load_selected_slot(self):
        save_slot = self.save_data.load_slot(self.selected_slot)
        if not save_slot:
            self.set_status("Empty slot")
            return None

        settings = save_slot.get("settings", {})
        settings_system = SettingsSystem(self.screen)
        if settings.get("resolution"):
            settings_system.set_resolution(tuple(settings.get("resolution")))
        settings_system.set_fullscreen(settings.get("fullscreen", False))
        settings_system.set_volume(settings.get("volume", 100))

        self.screen = settings_system.screen

        new_overworld = Overworld(
            self.screen,
            save_slot.get("player_name", "Captain"),
            save_slot.get("player_x"),
            save_slot.get("player_y")
        )
        player_name = save_slot.get("player_name", "Captain")
        return ("start_loading", player_name, lambda: new_overworld)

    def delete_selected_slot(self):
        if not self.save_data.has_slot(self.selected_slot):
            self.set_status("Slot is already empty")
            return
        self.save_data.clear_slot(self.selected_slot)
        self.set_status(f"Deleted slot {self.selected_slot + 1}")

    # UPDATE
    def update(self):
        if self.status_timer and pygame.time.get_ticks() - self.status_timer > 1800:
            self.status_message = ""
            self.status_timer = 0

    # DRAW
    def draw(self):
        self.screen.fill((10, 10, 20))

        title = self.font.render(
            "Load Game",
            True,
            (143, 205, 217)
        )

        center_x = self.screen.get_width() // 2

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, 120))
        )

        base_y = 220
        slot_list = self.save_data.get_slot_list()
        self.slot_rects = []
        for index, slot in enumerate(slot_list):
            if slot:
                name = slot.get("player_name", "Captain")
                resolution = slot.get("settings", {}).get("resolution")
                res_text = f" {resolution[0]}x{resolution[1]}" if isinstance(resolution, (list, tuple)) else ""
                text = f"Slot {index + 1}: {name}{res_text}"
            else:
                text = f"Slot {index + 1}: Empty"

            color = (255, 255, 255) if index == self.selected_slot else (180, 180, 180)
            slot_text = self.small_font.render(text, True, color)
            rect = slot_text.get_rect(center=(center_x, base_y + index * 40))
            self.screen.blit(slot_text, rect)
            self.slot_rects.append(rect)

        hint_text = self.small_font.render(
            "ENTER load  DEL delete  UP/DOWN select  ESC back",
            True,
            (160, 160, 160)
        )
        self.screen.blit(hint_text, hint_text.get_rect(center=(center_x, self.screen.get_height() - 80)))

        status_text = self.small_font.render(
            self.status_message,
            True,
            (210, 230, 255)
        )
        self.screen.blit(status_text, status_text.get_rect(center=(center_x, self.screen.get_height() - 40)))

        mouse_pos = pygame.mouse.get_pos()
        color = (255, 255, 255) if self.back_rect.collidepoint(mouse_pos) else (150, 150, 150)
        self.back_text = self.small_font.render("Back", True, color)
        self.screen.blit(self.back_text, self.back_rect)
