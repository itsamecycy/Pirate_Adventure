import pygame


class CharacterCreation:

    def __init__(self, screen):

        self.screen = screen

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            50
        )

        self.small_font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            40
        )

        self.name = ""

        self.done = False

        # BACK BUTTON
        self.back_text = self.small_font.render(
            "Back",
            True,
            (255, 255, 255)
        )

        self.back_rect = self.back_text.get_rect(center=(100, 50))

    # INPUT HANDLING
    def handle_events(self, event):

        mouse_pos = pygame.mouse.get_pos()

        # MOUSE CLICK (BACK BUTTON)
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.back_rect.collidepoint(mouse_pos):
                    return "back_to_menu"

        # NAME INPUT
        if event.type == pygame.KEYDOWN:

            # ENTER = confirm name
            if event.key == pygame.K_RETURN:

                if len(self.name) > 0:
                    self.done = True
                    return "start_game"

            # BACKSPACE = delete letter
            elif event.key == pygame.K_BACKSPACE:

                self.name = self.name[:-1]

            else:
                if len(self.name) < 12:
                    self.name += event.unicode

        return None

    # UPDATE
    def update(self):
        pass

    # DRAW
    def draw(self):

        self.screen.fill((10, 10, 20))

        # TITLE
        title = self.font.render(
            "Create Your Character",
            True,
            (143, 205, 217)
        )

        center_x = self.screen.get_width() // 2

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, 120))
        )

        # NAME INPUT LABEL
        prompt = self.small_font.render(
            "Enter Name:",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            prompt,
            prompt.get_rect(center=(center_x, 300))
        )

        # NAME TEXT
        name_text = self.font.render(
            self.name if self.name else "_",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            name_text,
            name_text.get_rect(center=(center_x, 380))
        )

        # INSTRUCTION
        hint = self.small_font.render(
            "Press ENTER to continue",
            True,
            (120, 120, 120)
        )

        self.screen.blit(
            hint,
            hint.get_rect(center=(center_x, 500))
        )

        # BACK BUTTON DRAW + HOVER
        mouse_pos = pygame.mouse.get_pos()

        if self.back_rect.collidepoint(mouse_pos):
            color = (255, 255, 255)
        else:
            color = (150, 150, 150)

        self.back_text = self.small_font.render("Back", True, color)

        self.screen.blit(self.back_text, self.back_rect)