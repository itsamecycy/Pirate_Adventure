import pygame
from sys import exit

from scenes.mainmenu import MainMenu
from scenes.charcreation import CharacterCreation
from scenes.settings import Settings
from scenes.loadgame import LoadGame
from scenes.loading import LoadingScreen
from maps.overworld import Overworld
from scenes.pause import PauseMenu

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pirate Adventure")

clock = pygame.time.Clock()

# START SCENE
current_scene = MainMenu(screen)

player_name = ""  # store final name


# GAME LOOP
while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        result = current_scene.handle_events(event)

        if isinstance(result, tuple):
            if result[0] == "update_screen":
                screen = result[1]
                current_scene.screen = screen
                continue
            if result[0] == "start_loading":
                # tuple: ("start_loading", player_name, next_scene_factory)
                player_name = result[1] if len(result) > 1 else ""
                factory = result[2] if len(result) > 2 else None
                current_scene = LoadingScreen(screen, player_name, next_scene_factory=factory)
                continue
            if result[0] == "switch_scene":
                current_scene = result[1]
                screen = current_scene.screen
                continue

        if result == "quit":
            pygame.quit()
            exit()

        elif result == "char_create":
            current_scene = CharacterCreation(screen)

        elif result == "load_game":
            current_scene = LoadGame(screen)

        elif result == "settings":
            current_scene = Settings(screen)

        elif result == "start_game":
            if isinstance(current_scene, CharacterCreation):
                player_name = current_scene.name
            current_scene = LoadingScreen(screen, player_name)

        elif result == "loading_done":
            current_scene = Overworld(screen, player_name)

        elif result == "pause":
            if isinstance(current_scene, Overworld):
                current_scene = PauseMenu(screen, current_scene)

        elif result == "back_to_menu":
            # show loading screen when returning to main menu
            current_scene = LoadingScreen(screen, player_name, next_scene_factory=lambda: MainMenu(screen))

    update_result = current_scene.update()
    if isinstance(update_result, tuple):
        if update_result[0] == "update_screen":
            screen = update_result[1]
            current_scene.screen = screen
        elif update_result[0] == "start_loading":
            player_name = update_result[1] if len(update_result) > 1 else ""
            factory = update_result[2] if len(update_result) > 2 else None
            current_scene = LoadingScreen(screen, player_name, next_scene_factory=factory)
            screen = current_scene.screen
        elif update_result[0] == "switch_scene":
            current_scene = update_result[1]
            screen = current_scene.screen
    elif update_result == "quit":
        pygame.quit()
        exit()
    elif update_result == "char_create":
        current_scene = CharacterCreation(screen)
    elif update_result == "load_game":
        current_scene = LoadGame(screen)
    elif update_result == "settings":
        current_scene = Settings(screen)
    elif update_result == "start_game":
        if isinstance(current_scene, CharacterCreation):
            player_name = current_scene.name
        current_scene = LoadingScreen(screen, player_name)
    elif update_result == "loading_done":
        current_scene = Overworld(screen, player_name)
    elif update_result == "back_to_menu":
        current_scene = MainMenu(screen)

    current_scene.draw()

    pygame.display.update()
    clock.tick(60)