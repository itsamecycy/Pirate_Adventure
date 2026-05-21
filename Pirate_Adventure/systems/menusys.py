import pygame


class MenuSystem:

    def __init__(self, font, screen):

        self.font = font
        self.screen = screen

        self.options = ["Start", "Load", "Settings", "Quit"]

        # LOAD BUTTON IMAGES
        self.button_imgs = {
            "Start": pygame.image.load("assets/ui/start-btn.png").convert_alpha(),
            "Load": pygame.image.load("assets/ui/load-btn.png").convert_alpha(),
            "Settings": pygame.image.load("assets/ui/settings-btn.png").convert_alpha(),
            "Quit": pygame.image.load("assets/ui/quit-btn.png").convert_alpha(),
        }

        self.button_hover_imgs = {
            "Start": pygame.image.load("assets/ui/start-hover.png").convert_alpha(),
            "Load": pygame.image.load("assets/ui/load-hover.png").convert_alpha(),
            "Settings": pygame.image.load("assets/ui/settings-hover.png").convert_alpha(),
            "Quit": pygame.image.load("assets/ui/quit-hover.png").convert_alpha(),
        }

        # RESIZE BUTTONS
        for key in self.button_imgs:
            self.button_imgs[key] = pygame.transform.smoothscale(
                self.button_imgs[key], (190, 130)
            )

        for key in self.button_hover_imgs:
            self.button_hover_imgs[key] = pygame.transform.smoothscale(
                self.button_hover_imgs[key], (190, 130)
            )

        self.buttons = []

        self.setup_buttons()

    # -------------------------
    # CREATE BUTTON POSITIONS
    # -------------------------
    def setup_buttons(self):

        self.buttons = []

        start_y = 350
        screen_center_x = self.screen.get_width() // 2

        for i, option in enumerate(self.options):

            rect = self.button_imgs[option].get_rect(
                center=(screen_center_x, start_y + i * 90)
            )

            self.buttons.append((option, rect))

    # -------------------------
    # HANDLE MOUSE INPUT
    # -------------------------
    def handle_input(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

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

            # HOVER CHECK
            if rect.collidepoint(mouse_pos):
                button_img = self.button_hover_imgs[option]
            else:
                button_img = self.button_imgs[option]

            # DRAW BUTTON IMAGE
            self.screen.blit(button_img, rect)
