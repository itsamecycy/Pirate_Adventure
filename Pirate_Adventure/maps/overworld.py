import pygame
from entities.player1 import Player
from entities.quartermaster import Quartermaster
from maps.bossArea import BossArea
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

        # place quartermaster a little below center
        qm_x = self.screen_w // 2
        qm_y = int(self.screen_h * 0.55)
        self.quartermaster = Quartermaster(qm_x, qm_y)

        # transient dialog display
        self.dialog_text = None
        self.dialog_timer = 0

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
            if event.key == pygame.K_e:
                # interact with quartermaster if colliding
                try:
                    if hasattr(self, 'quartermaster') and self.player.rect.colliderect(self.quartermaster.rect):
                        self.quartermaster.interact(self.player, self)
                except Exception:
                    pass
        # mouse click interaction
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                if hasattr(self, 'quartermaster') and self.quartermaster.rect.collidepoint(event.pos):
                    self.quartermaster.interact(self.player, self)
            except Exception:
                pass
        return None

    # UPDATE
    def update(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        old_center = self.player.rect.center
        old_rect = self.player.rect.copy()
        self.player.update()

        # detect movement and roll for encounters
        if self.player.rect.center != old_center:
            enemy = self.combat.player_step(self.player.rect.centerx, self.player.rect.centery)
            if enemy:
                # create battle scene and switch
                print(f"Encounter! Spawned: {type(enemy).__name__}")
                battle = BattleScene(self.screen, self.player_name, self.player, enemy, self)
                return ("switch_scene", battle)

        # boss area entry zone at the top center of the overworld
        entry_width = 240
        entry_height = 40
        entry_rect = pygame.Rect(
            (self.screen_w - entry_width) // 2,
            0,
            entry_width,
            entry_height,
        )
        if self.player.rect.top <= 0 and entry_rect.collidepoint(self.player.rect.centerx, self.player.rect.top):
            self.player.rect.midbottom = (self.screen_w // 2, self.screen_h - 40)
            boss_area = BossArea(self.screen, self.player_name, self.player, self)
            return ("switch_scene", boss_area)

        self.player.rect.x = max(0, min(self.player.rect.x, self.screen_w - self.player.rect.width))
        self.player.rect.y = max(0, min(self.player.rect.y, self.screen_h - self.player.rect.height))
        # update quartermaster
        try:
            if hasattr(self, 'quartermaster'):
                self.quartermaster.update()
        except Exception:
            pass

        # dialog timer
        if getattr(self, 'dialog_timer', 0) > 0:
            self.dialog_timer -= 16
            if self.dialog_timer <= 0:
                self.dialog_text = None
                self.dialog_timer = 0

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

        # draw quartermaster
        try:
            if hasattr(self, 'quartermaster'):
                self.quartermaster.draw(self.screen)
        except Exception:
            pass

        name_text = pygame.font.Font("assets/fonts/Pixeltype.ttf", 28).render(
            f"Captain: {self.player_name}",
            True,
            (220, 220, 220)
        )
        self.screen.blit(name_text, (18, 14))
        # Demon counter UI
        try:
            kills = getattr(self.player, 'quest_demon_kills', 0)
            counter_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 20)
            counter_text = counter_font.render(f"Demons: {kills}/10", True, (240, 200, 80))
            counter_bg = pygame.Surface((counter_text.get_width() + 12, counter_text.get_height() + 8), pygame.SRCALPHA)
            counter_bg.fill((8, 8, 12, 180))
            self.screen.blit(counter_bg, (18, 48))
            self.screen.blit(counter_text, (18 + 6, 48 + 4))
        except Exception:
            pass

        hint_text = pygame.font.Font("assets/fonts/Pixeltype.ttf", 24).render(
            "Press ESC to pause",
            True,
            (170, 170, 170)
        )
        self.screen.blit(hint_text, (18, self.screen_h - 40))

        # draw dialog text if present (improved panel)
        if getattr(self, 'dialog_text', None):
            # larger dialog font for readability
            font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 30)
            # support short wrapping if needed
            text = getattr(self, 'dialog_text', '')
            txt = font.render(text, True, (240, 240, 240))
            rect = txt.get_rect(center=(self.screen_w // 2, 80))
            panel_w = min(self.screen_w - 120, rect.width + 40)
            panel_h = rect.height + 24
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((6, 6, 12, 220))
            # border
            pygame.draw.rect(panel, (120, 140, 170, 220), panel.get_rect(), 2)
            panel_x = (self.screen_w - panel_w) // 2
            panel_y = rect.y - 12
            self.screen.blit(panel, (panel_x, panel_y))
            # center text within panel
            txt_rect = txt.get_rect(center=(panel_x + panel_w // 2, panel_y + panel_h // 2))
            self.screen.blit(txt, txt_rect)
