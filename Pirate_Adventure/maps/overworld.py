import pygame

from entities.player1 import Player
from systems.combatsys import CombatSystem
from scenes.battle import BattleScene


class Overworld:

    def __init__(self, screen, player_name, player_x=None, player_y=None):

        self.screen = screen
        self.player_name = player_name

        self.screen_w, self.screen_h = self.screen.get_size()

        # WORLD SETTINGS
        self.tile_size = 64

        # ZOOM SCALE
        self.zoom = 2

        # SCALED TILE SIZE
        self.render_tile_size = self.tile_size * self.zoom

        # CAMERA
        self.camera_x = 0
        self.camera_y = 0

        # MAP SIZE (BIGGER WORLD)
        self.map_cols = 40
        self.map_rows = 25

        self.world_width = self.map_cols * self.render_tile_size
        self.world_height = self.map_rows * self.render_tile_size

        # LOAD TILESETS
        self.tile_sheet = pygame.image.load(
            "assets/maps/TileSet.png"
        ).convert_alpha()

        self.trees_sheet = pygame.image.load(
            "assets/maps/Trees.png"
        ).convert_alpha()

        self.props_sheet = pygame.image.load(
            "assets/maps/Props.png"
        ).convert_alpha()

        # BACKGROUND
        try:
            self.bg = pygame.image.load(
                "assets/maps/skull_island.png"
            ).convert()

            self.bg = pygame.transform.smoothscale(
                self.bg,
                (self.world_width, self.world_height)
            )

        except Exception:
            self.bg = None

        # TILES
        self.ground_tile = self.scale_tile(
            self.get_tile(self.tile_sheet, 0, 0)
        )

        self.tree_tile = self.scale_tile(
            self.get_tile(self.trees_sheet, 0, 0)
        )

        self.prop_tile = self.scale_tile(
            self.get_tile(self.props_sheet, 0, 0)
        )

        # PLAYER
        self.player = Player(
            player_x if player_x is not None else self.world_width // 2,
            player_y if player_y is not None else self.world_height // 2
        )

        # COMBAT
        self.combat = CombatSystem(
            self.screen,
            encounter_chance=8,
            steps_per_check=1
        )

        # MAP
        self.map_data = self.build_map()

    # SCALE TILE
    def scale_tile(self, tile):

        return pygame.transform.scale(
            tile,
            (self.render_tile_size, self.render_tile_size)
        )

    # GET TILE
    def get_tile(self, sheet, col, row):

        return sheet.subsurface(
            pygame.Rect(
                col * self.tile_size,
                row * self.tile_size,
                self.tile_size,
                self.tile_size
            )
        ).copy()

    # BUILD MAP
    def build_map(self):

        game_map = [
            [0 for _ in range(self.map_cols)]
            for _ in range(self.map_rows)
        ]

        for y in range(self.map_rows):

            for x in range(self.map_cols):

                # BORDER WALLS
                if (
                    y == 0 or
                    y == self.map_rows - 1 or
                    x == 0 or
                    x == self.map_cols - 1
                ):
                    game_map[y][x] = 2

                # TREES
                elif (
                    (3 <= x <= 8 and 4 <= y <= 8)
                    or
                    (15 <= x <= 20 and 5 <= y <= 10)
                    or
                    (25 <= x <= 30 and 15 <= y <= 18)
                ):
                    game_map[y][x] = 1

                # PROPS
                elif (
                    (10 <= x <= 12 and 14 <= y <= 16)
                    or
                    (28 <= x <= 32 and 7 <= y <= 9)
                ):
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

        old_center = self.player.rect.center

        self.player.update()

        # WORLD BOUNDS
        self.player.rect.x = max(
            0,
            min(
                self.player.rect.x,
                self.world_width - self.player.rect.width
            )
        )

        self.player.rect.y = max(
            0,
            min(
                self.player.rect.y,
                self.world_height - self.player.rect.height
            )
        )

        # CAMERA FOLLOW
        target_x = (
            self.player.rect.centerx - self.screen_w // 2
        )

        target_y = (
            self.player.rect.centery - self.screen_h // 2
        )

        # SMOOTH CAMERA
        self.camera_x += (target_x - self.camera_x) * 0.08
        self.camera_y += (target_y - self.camera_y) * 0.08

        # CLAMP CAMERA
        self.camera_x = max(
            0,
            min(
                self.camera_x,
                self.world_width - self.screen_w
            )
        )

        self.camera_y = max(
            0,
            min(
                self.camera_y,
                self.world_height - self.screen_h
            )
        )

        # RANDOM ENCOUNTERS
        if self.player.rect.center != old_center:

            enemy = self.combat.player_step(
                self.player.rect.centerx,
                self.player.rect.centery
            )

            if enemy:

                print(f"Encounter! Spawned: {type(enemy).__name__}")

                battle = BattleScene(
                    self.screen,
                    self.player_name,
                    self.player,
                    enemy,
                    self
                )

                return ("switch_scene", battle)

    # DRAW
    def draw(self):

        # DRAW BACKGROUND
        if self.bg:

            self.screen.blit(
                self.bg,
                (-self.camera_x, -self.camera_y)
            )

        else:

            self.screen.fill((9, 15, 33))

            for y, row in enumerate(self.map_data):

                for x, tile_id in enumerate(row):

                    draw_x = (
                        x * self.render_tile_size
                        - self.camera_x
                    )

                    draw_y = (
                        y * self.render_tile_size
                        - self.camera_y
                    )

                    pos = (draw_x, draw_y)

                    self.screen.blit(self.ground_tile, pos)

                    if tile_id == 1:
                        self.screen.blit(self.tree_tile, pos)

                    elif tile_id == 2:
                        self.screen.blit(self.prop_tile, pos)

                    elif tile_id == 3:
                        self.screen.blit(self.prop_tile, pos)

        # DRAW PLAYER
        player_draw_x = self.player.rect.x - self.camera_x
        player_draw_y = self.player.rect.y - self.camera_y

        self.screen.blit(
            self.player.image,
            (player_draw_x, player_draw_y)
        )

        # UI
        name_text = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            28
        ).render(
            f"Captain: {self.player_name}",
            True,
            (220, 220, 220)
        )

        self.screen.blit(name_text, (18, 14))

        hint_text = pygame.font.Font(
            "assets/fonts/Pixeltype.ttf",
            24
        ).render(
            "Press ESC to pause",
            True,
            (170, 170, 170)
        )

        self.screen.blit(
            hint_text,
            (18, self.screen_h - 40)
        )
