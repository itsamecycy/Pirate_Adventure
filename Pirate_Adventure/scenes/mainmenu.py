import pygame
from systems.menusys import MenuSystem


class MainMenu:

    def __init__(self, screen):

        self.screen = screen

        self.font = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            50
        )


        # LOAD BACKGROUND

        self.bg = pygame.image.load(
            "assets/maps/menu_bg.png"
        ).convert()

        # Screen size from the passed surface
        self.screen_w, self.screen_h = self.screen.get_size()

        # SCALE BACKGROUND TO FIT EXACT SCREEN SIZE
        self.bg = pygame.transform.smoothscale(
            self.bg,
            (self.screen_w, self.screen_h)
        )


        # MENU SYSTEM

        self.menu = MenuSystem(self.font, self.screen)
        # PLAY MENU BGM (looping)
        try:
            pygame.mixer.music.load("assets/sfx/Pirates Of The Caribbean Theme Song.mp3")
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"MainMenu BGM error: {e}")

    # INPUT
    def handle_events(self, event):

        result = self.menu.handle_input(event)

        if result == "Start":
            return "char_create"

        elif result == "Load":
            return "load_game"

        elif result == "Settings":
            return "settings"

        elif result == "Quit":
            return "quit"

        return None

    # UPDATE
    def update(self):
        pass

    # DRAW
    def draw(self):


        # DRAW BACKGROUND FULLSCREEN
        self.screen.blit(self.bg, (0, 0))

        # DARK OVERLAY (JRPG STYLE READABILITY)

        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))


        # TITLE

        title = self.font.render(
            "Pirate Adventure",
            True,
            (143, 205, 217)
        )

        center_x = self.screen.get_width() // 2

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, 120))
        )

        # MENU DRAW
        self.menu.draw()