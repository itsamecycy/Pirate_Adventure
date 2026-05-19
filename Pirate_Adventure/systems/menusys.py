import pygame


class MenuSystem:

    def __init__(self, font, screen):

        self.font = font
        self.screen = screen

        self.options = ["Start", "Load", "Settings", "Quit"]

        self.buttons = []  # store rects for clicking

        self.color_active = (255, 255, 255)
        self.color_inactive = (120, 120, 120)

        self.setup_buttons()

    # -------------------------
    # CREATE BUTTON POSITIONS
    # -------------------------
    def setup_buttons(self):

        self.buttons = []

        start_y = 250

        screen_center_x = self.screen.get_width() // 2

        for i, option in enumerate(self.options):

            text = self.font.render(option, True, (255, 255, 255))

            rect = text.get_rect(center=(screen_center_x, start_y + i * 60))

            self.buttons.append((option, rect))

    # -------------------------
    # HANDLE MOUSE INPUT
    # -------------------------
    def handle_input(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:  # LEFT CLICK

                mouse_pos = pygame.mouse.get_pos()

                for option, rect in self.buttons:

                    if rect.collidepoint(mouse_pos):

                        return option

        return None

    # -------------------------
    # DRAW MENU
    # -------------------------
    def draw(self):

        mouse_pos = pygame.mouse.get_pos()

        for option, rect in self.buttons:

            # hover effect
            if rect.collidepoint(mouse_pos):
                color = self.color_active
            else:
                color = self.color_inactive

            text = self.font.render(option, True, color)

            self.screen.blit(text, rect)