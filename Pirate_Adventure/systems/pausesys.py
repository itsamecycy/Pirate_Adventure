import pygame


class PauseSystem:

    def __init__(self, font, screen):
        self.font = font
        self.screen = screen
        self.options = [
            "Resume",
            "Save Slot",
            "Load Slot",
            "Delete Slot",
            "Settings",
            "Quit to Menu"
        ]
        self.selected_index = 0
        self.buttons = []
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        center_x = self.screen.get_width() // 2
        base_y = 240

        for index, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            rect = text.get_rect(center=(center_x, base_y + index * 60))
            self.buttons.append((option, rect))

    def update_screen(self, screen):
        if screen != self.screen:
            self.screen = screen
            self.build_buttons()

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.options)
        return self.options[self.selected_index]

    def select(self):
        return self.options[self.selected_index]

    def handle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for option, rect in self.buttons:
                if rect.collidepoint(mouse_pos):
                    return option
        return None

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        for index, (option, rect) in enumerate(self.buttons):
            if index == self.selected_index:
                color = (210, 235, 255)
            elif rect.collidepoint(mouse_pos):
                color = (255, 255, 255)
            else:
                color = (160, 160, 160)

            text = self.font.render(option, True, color)
            self.screen.blit(text, rect)
