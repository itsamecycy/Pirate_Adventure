import pygame
from entities.player1 import Player
from systems.combatsys import CombatSystem
from scenes.battle import BattleScene


class Overworld:

    def __init__(self, screen, player_name, player_x=None, player_y=None):
        self.screen = screen
        self.player_name = player_name
        self.screen_w, self.screen_h = self.screen.get_size()

        self.tile_size = 64
        self.tile_sheet = pygame.image.load(
            "assets/maps/TileSet.png"
        ).convert_alpha()
        self.trees_sheet = pygame.image.load(
            "assets/maps/Trees.png"
        ).convert_alpha()
        self.props_sheet = pygame.image.load(
            "assets/maps/Props.png"
        ).convert_alpha()

        # Use final area background image if available
        try:
            self.bg = pygame.image.load("assets/maps/final_area.png").convert()
        except Exception:
            self.bg = None

        self.ground_tile = self.get_tile(self.tile_sheet, 0, 0)
        self.tree_tile = self.get_tile(self.trees_sheet, 0, 0)
        self.prop_tile = self.get_tile(self.props_sheet, 0, 0)

        self.player = Player(
            player_x if player_x is not None else self.screen_w // 2,
            player_y if player_y is not None else self.screen_h // 2
        )

        # Combat system for random encounters
        self.combat = CombatSystem(self.screen, encounter_chance=8, steps_per_check=1)
        self.pending_encounter = None

        self.map_data = self.build_map()

    def get_tile(self, sheet, col, row):
        return sheet.subsurface(
            pygame.Rect(
                col * self.tile_size,
                row * self.tile_size,
                self.tile_size,
                self.tile_size
            )
        ).copy()

    def build_map(self):
        cols = self.screen_w // self.tile_size
        rows = self.screen_h // self.tile_size

        game_map = [[0 for _ in range(cols)] for _ in range(rows)]

        for y in range(rows):
            for x in range(cols):
                if y == 0 or y == rows - 1 or x == 0 or x == cols - 1:
                    game_map[y][x] = 2
                elif (3 <= x <= 5 and 4 <= y <= 6) or (10 <= x <= 12 and 2 <= y <= 3):
                    game_map[y][x] = 1
                elif (14 <= x <= 15 and 7 <= y <= 8) or (6 <= x <= 7 and 8 <= y <= 9):
                    game_map[y][x] = 3

        return game_map

    # INPUT
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "pause"
        return None

    # UPDATE
    def update(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        old_center = self.player.rect.center
        self.player.update()

        # detect movement and roll for encounters
        if self.player.rect.center != old_center:
            enemy = self.combat.player_step(self.player.rect.centerx, self.player.rect.centery)
            if enemy:
                # create battle scene and switch
                print(f"Encounter! Spawned: {type(enemy).__name__}")
                battle = BattleScene(self.screen, self.player_name, self.player, enemy, self)
                return ("switch_scene", battle)

        self.player.rect.x = max(0, min(self.player.rect.x, self.screen_w - self.player.rect.width))
        self.player.rect.y = max(0, min(self.player.rect.y, self.screen_h - self.player.rect.height))

    # DRAW
    def draw(self):
        # Draw background: prefer final area image, fallback to tiled ground
        if self.bg:
            bg_scaled = pygame.transform.smoothscale(self.bg, (self.screen_w, self.screen_h))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            self.screen.fill((9, 15, 33))

            for y, row in enumerate(self.map_data):
                for x, tile_id in enumerate(row):
                    pos = (x * self.tile_size, y * self.tile_size)
                    self.screen.blit(self.ground_tile, pos)

                    if tile_id == 1:
                        self.screen.blit(self.tree_tile, pos)
                    elif tile_id == 2:
                        self.screen.blit(self.prop_tile, pos)
                    elif tile_id == 3:
                        self.screen.blit(self.prop_tile, pos)

        self.screen.blit(self.player.image, self.player.rect)

        name_text = pygame.font.Font("assets/fonts/Pixeltype.ttf", 28).render(
            f"Captain: {self.player_name}",
            True,
            (220, 220, 220)
        )
        self.screen.blit(name_text, (18, 14))

        hint_text = pygame.font.Font("assets/fonts/Pixeltype.ttf", 24).render(
            "Press ESC to pause",
            True,
            (170, 170, 170)
        )
        self.screen.blit(hint_text, (18, self.screen_h - 40))
