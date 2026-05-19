import pygame
import random
from systems.combatsys import CombatSystem


class BattleScene:

    def __init__(self, screen, player_name, player_entity, enemy_entity, return_scene):
        self.screen = screen
        self.screen_w, self.screen_h = self.screen.get_size()
        self.player_name = player_name

        # Player combat stats
        self.player_entity = player_entity
        self.player = {
            "max_hp": 120,
            "hp": 120,
            "max_mp": 40,
            "mp": 40,
            "defending": False,
            "items": {"potion": 2},
        }

        # Enemy
        self.enemy_entity = enemy_entity
        if not hasattr(self.enemy_entity, "max_hp"):
            self.enemy_entity.max_hp = 90
            self.enemy_entity.hp = 90
        else:
            if not hasattr(self.enemy_entity, "hp"):
                self.enemy_entity.hp = self.enemy_entity.max_hp

        # Combat helper
        self.combat = CombatSystem()

        # turn state
        self.turn = "player"
        self.menu_options = ["Attack", "Defend", "Skills", "Item", "Run"]
        self.selected = 0
        self.message = "A wild enemy appears!"
        self.message_timer = 0
        self.return_scene = return_scene

        self.font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 28)
        self.title_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 40)

        # player attack animation frames (use ATTACK 1 down sheet)
        self.frame_width = 64
        self.frame_height = 64
        self.player_attack_frames = []
        try:
            atk_sheet = pygame.image.load("assets/player1/ATTACK 1/attack1_down.png").convert_alpha()
            cols = max(1, atk_sheet.get_width() // self.frame_width)
            for i in range(cols):
                f = atk_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)).copy()
                self.player_attack_frames.append(f)
        except Exception:
            self.player_attack_frames = []

        self.player_anim_state = "idle"
        self.player_frame_index = 0
        self.player_anim_speed = 0.18

        # menu rects for mouse interaction
        self.menu_rects = []

    # INPUT
    def handle_events(self, event):
        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if self.turn != "player":
                return None
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu_options)
                return None
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu_options)
                return None
            if event.key == pygame.K_RETURN:
                return self.execute_choice(self.menu_options[self.selected])

        # Mouse navigation & clicks
        if event.type == pygame.MOUSEMOTION:
            if not self.menu_rects:
                return None
            mx, my = event.pos
            for i, r in enumerate(self.menu_rects):
                if r.collidepoint(mx, my) and self.turn == "player":
                    self.selected = i
                    break
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.menu_rects:
                return None
            mx, my = event.pos
            for i, r in enumerate(self.menu_rects):
                if r.collidepoint(mx, my) and self.turn == "player":
                    return self.execute_choice(self.menu_options[i])
            return None

        return None

    def execute_choice(self, choice):
        self.message_timer = pygame.time.get_ticks()
        if choice == "Attack":
            # play attack animation and apply damage
            self.player_anim_state = "attack"
            self.player_frame_index = 0
            dmg = self.combat.attack(self.player, self.enemy_entity)
            self.message = f"You attack for {dmg} damage."
            self.turn = "enemy"
            return None

        if choice == "Defend":
            self.combat.defend(self.player)
            self.message = "You brace for the next attack."
            self.turn = "enemy"
            return None

        if choice == "Skills":
            ok, msg, val = self.combat.skill(self.player, self.enemy_entity, name="fireball")
            self.message = msg
            self.turn = "enemy"
            return None

        if choice == "Item":
            ok, msg, val = self.combat.use_item(self.player, "potion")
            self.message = msg
            self.turn = "enemy"
            return None

        if choice == "Run":
            success = self.combat.try_run(self.player, self.enemy_entity, base_chance=0.6)
            if success:
                self.message = "You successfully ran away!"
                return ("switch_scene", self.return_scene)
            else:
                self.message = "Failed to run away!"
                self.turn = "enemy"
                return None

    # UPDATE
    def update(self):
        # check end conditions
        if getattr(self.enemy_entity, "hp", 0) <= 0:
            self.message = "Enemy defeated!"
            return ("switch_scene", self.return_scene)

        if self.player["hp"] <= 0:
            self.message = "You were defeated..."
            return "back_to_menu"

        # player animation update (attack)
        if self.player_anim_state == "attack":
            self.player_frame_index += self.player_anim_speed
            if self.player_frame_index >= len(self.player_attack_frames):
                # animation finished
                self.player_anim_state = "idle"
                self.player_frame_index = 0

        # enemy turn handling
        if self.turn == "enemy":
            # simple delay
            if pygame.time.get_ticks() - self.message_timer < 600:
                return None

            dmg = self.combat.attack(self.enemy_entity, self.player)
            self.message = f"Enemy hits for {dmg} damage."
            self.message_timer = pygame.time.get_ticks()
            self.turn = "player"

        return None

    # DRAW HELPERS
    def draw_bar(self, x, y, w, h, current, maximum, fg=(200, 40, 40), bg=(60, 60, 60)):
        pygame.draw.rect(self.screen, bg, (x, y, w, h))
        pct = max(0, min(1.0, current / maximum if maximum else 0))
        pygame.draw.rect(self.screen, fg, (x, y, int(w * pct), h))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, w, h), 2)

    # DRAW
    def draw(self):
        self.screen.fill((18, 18, 28))

        center_x = self.screen.get_width() // 2

        title = self.title_font.render("Battle", True, (200, 200, 220))
        self.screen.blit(title, title.get_rect(center=(center_x, 40)))

        # enemy on right
        enemy_img = getattr(self.enemy_entity, "image", None)
        if enemy_img:
            enemy_rect = enemy_img.get_rect(center=(center_x + 220, self.screen.get_height() // 2 - 40))
            self.screen.blit(enemy_img, enemy_rect)

        # player on left (use attack animation when playing)
        player_img = None
        if self.player_anim_state == "attack" and self.player_attack_frames:
            idx = int(self.player_frame_index) % max(1, len(self.player_attack_frames))
            player_img = self.player_attack_frames[idx]
        else:
            player_img = getattr(self.player_entity, "image", None)

        if player_img:
            player_rect = player_img.get_rect(center=(center_x - 220, self.screen.get_height() // 2 + 20))
            self.screen.blit(player_img, player_rect)

        # HUD bars (player)
        self.draw_bar(80, 80, 360, 28, self.player["hp"], self.player["max_hp"], fg=(40, 200, 40))
        hp_text = self.font.render(f"HP: {self.player['hp']}/{self.player['max_hp']}", True, (220, 220, 220))
        self.screen.blit(hp_text, (460, 80))
        mp_text = self.font.render(f"MP: {self.player['mp']}/{self.player['max_mp']}", True, (200, 200, 220))
        self.screen.blit(mp_text, (80, 110))

        enemy_hp = int(getattr(self.enemy_entity, "hp", getattr(self.enemy_entity, "max_hp", 0)))
        enemy_max = int(getattr(self.enemy_entity, "max_hp", 1))
        enemy_bar_x = self.screen.get_width() - 440
        self.draw_bar(enemy_bar_x, 80, 360, 28, enemy_hp, enemy_max, fg=(200, 40, 40))
        enemy_name = getattr(self.enemy_entity, "name", "Enemy")
        enemy_name_text = self.font.render(enemy_name, True, (220, 220, 220))
        self.screen.blit(enemy_name_text, (enemy_bar_x, 50))
        enemy_hp_text = self.font.render(f"HP: {enemy_hp}/{enemy_max}", True, (220, 220, 220))
        self.screen.blit(enemy_hp_text, (enemy_bar_x + 260, 80))

        # Action menu
        menu_x = 80
        menu_y = self.screen.get_height() - 220
        self.menu_rects = []
        for i, opt in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected and self.turn == "player" else (180, 180, 180)
            opt_text = self.font.render(opt, True, color)
            rect = opt_text.get_rect(topleft=(menu_x, menu_y + i * 36))
            self.screen.blit(opt_text, rect)
            self.menu_rects.append(rect)

        # Message
        msg_text = self.font.render(self.message, True, (210, 230, 255))
        self.screen.blit(msg_text, msg_text.get_rect(center=(center_x, self.screen.get_height() - 60)))
