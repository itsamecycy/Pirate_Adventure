import pygame
from systems.pausesys import PauseSystem
from systems.settingsys import SettingsSystem
from systems.savedata import SaveData
from maps.overworld import Overworld


class PauseMenu:

    def __init__(self, screen, overworld):
        self.screen = screen
        self.overworld = overworld
        self.screen_w, self.screen_h = self.screen.get_size()

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            50
        )
        self.small_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            28
        )

        self.pause_system = PauseSystem(self.font, self.screen)
        self.settings_system = SettingsSystem(self.screen)
        self.save_data = SaveData()

        self.mode = None
        self.selected_slot = 0
        self.slots = []
        self.slot_rects = []
        self.refresh_slots()

        self.status_message = "Paused"
        self.status_timer = 0
        # ensure pause options reflect current encounter state
        self.update_pause_options()

    def refresh_slots(self):
        self.slots = self.save_data.get_slot_list()
        if self.selected_slot >= len(self.slots):
            self.selected_slot = len(self.slots) - 1

    def set_status(self, text):
        self.status_message = text
        self.status_timer = pygame.time.get_ticks()

    def update_pause_options(self):
        # dynamic label for encounters
        combat = getattr(self.overworld, 'combat', None)
        encounters_on = True if combat is None else getattr(combat, 'enabled', True)
        enc_label = "Encounters: On" if encounters_on else "Encounters: Off"
        self.pause_system.options = [
            "Resume",
            "Resources",
            "Save Slot",
            "Load Slot",
            "Delete Slot",
            enc_label,
            "Settings",
            "Quit to Menu"
        ]
        self.pause_system.build_buttons()

    def slot_label(self, index):
        slot = self.slots[index]
        if slot is None:
            return f"Slot {index + 1}: Empty"

        name = slot.get("player_name", "Captain")
        saved_at = slot.get("saved_at", "unknown")
        short_date = saved_at.split("T")[0] if "T" in saved_at else saved_at
        res = slot.get("settings", {}).get("resolution")
        resolution = f" {res[0]}x{res[1]}" if isinstance(res, (list, tuple)) else ""
        return f"Slot {index + 1}: {name}{resolution} ({short_date})"

    def handle_slot_action(self):
        if self.mode == "save":
            return self.save_slot(self.selected_slot)
        if self.mode == "load":
            return self.load_slot(self.selected_slot)
        if self.mode == "delete":
            return self.delete_slot(self.selected_slot)
        return None

    def save_slot(self, index):
        save_state = {
            "player_name": self.overworld.player_name,
            "player_x": self.overworld.player.rect.centerx,
            "player_y": self.overworld.player.rect.centery,
            "player_hp": getattr(self.overworld.player, 'hp', 120),
            "player_max_hp": getattr(self.overworld.player, 'max_hp', 120),
            "player_mp": getattr(self.overworld.player, 'mp', 40),
            "player_max_mp": getattr(self.overworld.player, 'max_mp', 40),
            "player_items": getattr(self.overworld.player, 'items', {}),
            "player_skills": getattr(self.overworld.player, 'skills', []),
            "player_status": getattr(self.overworld.player, 'status_effects', ['Healthy']),
            "settings": {
                "resolution": self.settings_system.current_resolution(),
                "fullscreen": self.settings_system.fullscreen,
                "volume": self.settings_system.volume,
            },
        }
        if self.save_data.save_slot(index, save_state):
            self.set_status(f"Saved slot {index + 1}")
            self.refresh_slots()
            self.mode = None
        else:
            self.set_status("Unable to save slot")
        return None

    def load_slot(self, index):
        saved = self.save_data.load_slot(index)
        if not saved:
            self.set_status("Empty slot")
            return None

        settings = saved.get("settings", {})
        if settings.get("resolution"):
            self.settings_system.set_resolution(tuple(settings.get("resolution")))
        self.settings_system.set_fullscreen(settings.get("fullscreen", self.settings_system.fullscreen))
        self.settings_system.set_volume(settings.get("volume", self.settings_system.volume))

        self.screen = self.settings_system.screen
        self.pause_system.update_screen(self.screen)

        new_overworld = Overworld(
            self.screen,
            saved.get("player_name", self.overworld.player_name),
            saved.get("player_x", self.overworld.player.rect.centerx),
            saved.get("player_y", self.overworld.player.rect.centery),
        )
        new_overworld.player.hp = saved.get("player_hp", getattr(new_overworld.player, 'hp', 120))
        new_overworld.player.max_hp = saved.get("player_max_hp", getattr(new_overworld.player, 'max_hp', 120))
        new_overworld.player.mp = saved.get("player_mp", getattr(new_overworld.player, 'mp', 40))
        new_overworld.player.max_mp = saved.get("player_max_mp", getattr(new_overworld.player, 'max_mp', 40))
        new_overworld.player.items = saved.get("player_items", getattr(new_overworld.player, 'items', {}))
        new_overworld.player.skills = saved.get("player_skills", getattr(new_overworld.player, 'skills', []))
        new_overworld.player.status_effects = saved.get("player_status", getattr(new_overworld.player, 'status_effects', ['Healthy']))
        player_name = saved.get("player_name", self.overworld.player_name)
        return ("start_loading", player_name, lambda: new_overworld)

    def delete_slot(self, index):
        if not self.save_data.has_slot(index):
            self.set_status("Empty slot")
            return None

        self.save_data.clear_slot(index)
        self.refresh_slots()
        self.set_status(f"Deleted slot {index + 1}")
        return None

    def get_player_status_lines(self):
        player = getattr(self.overworld, 'player', None)
        hp = getattr(player, 'hp', 120)
        max_hp = getattr(player, 'max_hp', 120)
        mp = getattr(player, 'mp', 40)
        max_mp = getattr(player, 'max_mp', 40)
        items = getattr(player, 'items', {}) or {}
        skills = getattr(player, 'skills', []) or []
        status = getattr(player, 'status_effects', ['Healthy']) or ['Healthy']

        lines = [
            f"Name: {self.overworld.player_name}",
            f"HP: {hp}/{max_hp}",
            f"MP: {mp}/{max_mp}",
            f"Status: {', '.join(status)}",
            "",
            "Skills:",
        ]
        if skills:
            lines.extend([f"  - {skill}" for skill in skills])
        else:
            lines.append("  None")

        lines.append("")
        lines.append("Items:")
        if items:
            lines.extend([f"  - {name}: {qty}" for name, qty in items.items()])
        else:
            lines.append("  None")
        return lines

    # INPUT
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode:
                if event.key == pygame.K_ESCAPE:
                    self.mode = None
                    return None
                if self.mode == "settings":
                    if event.key == pygame.K_q:
                        self.settings_system.change_volume(-10)
                        self.set_status(f"Volume {self.settings_system.volume}%")
                        return ("update_screen", self.settings_system.screen)
                    elif event.key == pygame.K_e:
                        self.settings_system.change_volume(10)
                        self.set_status(f"Volume {self.settings_system.volume}%")
                        return ("update_screen", self.settings_system.screen)
                    elif event.key == pygame.K_z:
                        self.settings_system.change_sfx_volume(-10)
                        self.set_status(f"SFX {self.settings_system.sfx_volume}%")
                        return None
                    elif event.key == pygame.K_x:
                        self.settings_system.change_sfx_volume(10)
                        self.set_status(f"SFX {self.settings_system.sfx_volume}%")
                        return None
                    elif event.key == pygame.K_a:
                        new_screen = self.settings_system.change_resolution(-1)
                        self.screen = new_screen
                        self.pause_system.update_screen(self.screen)
                        self.set_status(f"Resolution {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}")
                        return ("update_screen", new_screen)
                    elif event.key == pygame.K_d:
                        new_screen = self.settings_system.change_resolution(1)
                        self.screen = new_screen
                        self.pause_system.update_screen(self.screen)
                        self.set_status(f"Resolution {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}")
                        return ("update_screen", new_screen)
                    elif event.key == pygame.K_f:
                        new_screen = self.settings_system.toggle_fullscreen()
                        self.screen = new_screen
                        self.pause_system.update_screen(self.screen)
                        self.set_status("Fullscreen toggled")
                        return ("update_screen", new_screen)
                    return None

                if event.key == pygame.K_UP:
                    self.selected_slot = (self.selected_slot - 1) % len(self.slots)
                    return None
                if event.key == pygame.K_DOWN:
                    self.selected_slot = (self.selected_slot + 1) % len(self.slots)
                    return None
                if event.key == pygame.K_RETURN:
                    return self.handle_slot_action()
                if event.key == pygame.K_DELETE and self.mode == "delete":
                    return self.delete_slot(self.selected_slot)
                return None

            if event.key == pygame.K_ESCAPE:
                self.overworld.screen = self.screen
                self.overworld.screen_w, self.overworld.screen_h = self.screen.get_size()
                return ("switch_scene", self.overworld)

            if event.key == pygame.K_UP:
                self.pause_system.navigate(-1)
            elif event.key == pygame.K_DOWN:
                self.pause_system.navigate(1)
            elif event.key == pygame.K_RETURN:
                return self.handle_selection(self.pause_system.select())
            elif event.key == pygame.K_q:
                self.settings_system.change_volume(-10)
                self.set_status(f"Volume {self.settings_system.volume}%")
                return ("update_screen", self.settings_system.screen)
            elif event.key == pygame.K_e:
                self.settings_system.change_volume(10)
                self.set_status(f"Volume {self.settings_system.volume}%")
                return ("update_screen", self.settings_system.screen)
            elif event.key == pygame.K_a:
                new_screen = self.settings_system.change_resolution(-1)
                self.screen = new_screen
                self.pause_system.update_screen(self.screen)
                self.set_status(f"Resolution {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}")
                return ("update_screen", new_screen)
            elif event.key == pygame.K_d:
                new_screen = self.settings_system.change_resolution(1)
                self.screen = new_screen
                self.pause_system.update_screen(self.screen)
                self.set_status(f"Resolution {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}")
                return ("update_screen", new_screen)
            elif event.key == pygame.K_f:
                new_screen = self.settings_system.toggle_fullscreen()
                self.screen = new_screen
                self.pause_system.update_screen(self.screen)
                self.set_status("Fullscreen toggled")
                return ("update_screen", new_screen)

        if self.mode is None:
            mouse_result = self.pause_system.handle_mouse(event)
            if mouse_result:
                return self.handle_selection(mouse_result)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.slot_rects):
                if rect.collidepoint(pygame.mouse.get_pos()):
                    self.selected_slot = index
                    return self.handle_slot_action()

        return None

    def handle_selection(self, option):
        if option == "Resume":
            self.overworld.screen = self.screen
            self.overworld.screen_w, self.overworld.screen_h = self.screen.get_size()
            return ("switch_scene", self.overworld)

        if option and option.startswith("Encounters"):
            combat = getattr(self.overworld, 'combat', None)
            if combat:
                new_state = not getattr(combat, 'enabled', True)
                # prefer API if available
                if hasattr(combat, 'set_encounters_enabled'):
                    combat.set_encounters_enabled(new_state)
                else:
                    combat.enabled = new_state
                self.update_pause_options()
                self.set_status("Encounters disabled" if not new_state else "Encounters enabled")
            else:
                self.set_status("No combat system")
            return None

        if option == "Resources":
            self.mode = "resources"
            return None

        if option == "Save Slot":
            self.mode = "save"
            self.selected_slot = 0
            self.refresh_slots()
            return None

        if option == "Load Slot":
            self.mode = "load"
            self.selected_slot = 0
            self.refresh_slots()
            return None

        if option == "Delete Slot":
            self.mode = "delete"
            self.selected_slot = 0
            self.refresh_slots()
            return None

        if option == "Settings":
            self.mode = "settings"
            self.set_status("Settings mode")
            return None

        if option == "Quit to Menu":
            return "back_to_menu"

        return None

    # UPDATE
    def update(self):
        if self.status_timer and pygame.time.get_ticks() - self.status_timer > 1800:
            self.status_message = "Paused"
            self.status_timer = 0

    # DRAW
    def draw(self):
        self.screen.fill((12, 24, 48))

        center_x = self.screen.get_width() // 2

        title = self.font.render(
            "Pause Menu",
            True,
            (143, 205, 217)
        )
        self.screen.blit(title, title.get_rect(center=(center_x, 100)))

        if self.mode is None:
            self.pause_system.draw()
            prompt = self.small_font.render(
                "Select Save, Load, or Delete slot.",
                True,
                (180, 180, 180)
            )
            self.screen.blit(prompt, prompt.get_rect(center=(center_x, 500)))
        else:
            mode_title = {
                "save": "Save to Slot",
                "load": "Load Slot",
                "delete": "Delete Slot",
                "settings": "Settings"
            }.get(self.mode, "Slot Menu")

            label = self.small_font.render(
                mode_title,
                True,
                (220, 220, 255)
            )
            self.screen.blit(label, label.get_rect(center=(center_x, 140)))

            if self.mode == "settings":
                setting_lines = [
                    f"Volume: {self.settings_system.volume}%",
                    f"SFX Volume: {getattr(self.settings_system, 'sfx_volume', self.settings_system.volume)}%",
                    f"Resolution: {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}",
                    f"Fullscreen: {'On' if self.settings_system.fullscreen else 'Off'}",
                    "Q/E change volume",
                    "Z/X change SFX",
                    "A/D change resolution",
                    "F toggle fullscreen",
                    "ESC return"
                ]
                for i, line in enumerate(setting_lines):
                    option_text = self.small_font.render(line, True, (180, 180, 180))
                    self.screen.blit(option_text, option_text.get_rect(center=(center_x, 220 + i * 40)))
            elif self.mode == "resources":
                status_lines = self.get_player_status_lines()
                for i, line in enumerate(status_lines):
                    option_text = self.small_font.render(line, True, (200, 200, 220) if line and not line.startswith('  -') else (180, 180, 180))
                    self.screen.blit(option_text, option_text.get_rect(topleft=(80, 220 + i * 34)))
                instructions = self.small_font.render(
                    "ESC return",
                    True,
                    (160, 160, 160)
                )
                self.screen.blit(instructions, instructions.get_rect(center=(center_x, self.screen.get_height() - 80)))
            else:
                base_y = 220
                self.slot_rects = []
                for index, _ in enumerate(self.slots):
                    text = self.slot_label(index)
                    color = (255, 255, 255) if index == self.selected_slot else (180, 180, 180)
                    option_text = self.small_font.render(text, True, color)
                    rect = option_text.get_rect(center=(center_x, base_y + index * 40))
                    self.screen.blit(option_text, rect)
                    self.slot_rects.append(rect)

                instructions = self.small_font.render(
                    "ENTER select  ESC cancel  DEL delete (delete mode)",
                    True,
                    (160, 160, 160)
                )
                self.screen.blit(instructions, instructions.get_rect(center=(center_x, self.screen.get_height() - 80)))

        status = self.small_font.render(
            self.status_message,
            True,
            (210, 230, 255)
        )
        self.screen.blit(status, status.get_rect(center=(center_x, self.screen.get_height() - 40)))

        settings_text = self.small_font.render(
            f"Volume: {self.settings_system.volume}%  Res: {self.settings_system.current_resolution()[0]}x{self.settings_system.current_resolution()[1]}  Fullscreen: {'On' if self.settings_system.fullscreen else 'Off'}",
            True,
            (200, 200, 200)
        )
        self.screen.blit(settings_text, settings_text.get_rect(center=(center_x, self.screen.get_height() - 20)))
