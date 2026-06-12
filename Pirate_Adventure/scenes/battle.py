import copy
import os
import re
import pygame
import random
from systems.combatsys import CombatSystem
from systems.settingsys import SFX_VOLUME


class BattleScene:

    def __init__(self, screen, player_name, player_entity, enemy_entity, return_scene, boss_npc=None):
        self.screen = screen
        self.screen_w, self.screen_h = self.screen.get_size()
        self.player_name = player_name

        # Boss area NPC reference for boss battles
        self.boss_npc = None
        if boss_npc is not None:
            try:
                self.boss_npc = copy.copy(boss_npc)
            except Exception:
                self.boss_npc = boss_npc

        # Player combat stats
        self.player_entity = player_entity
        self.player = {
            "max_hp": 120,
            "hp": 120,
            "max_mp": 40,
            "mp": 40,
            "defending": False,
            "items": {"potion": 2},
            "attack_power": getattr(self.player_entity, "attack_power", (12, 20)),
            "equipped_weapons": getattr(self.player_entity, "equipped_weapons", {"gun": None, "sword": None}),
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
        self.message_color = (0, 0, 0)
        self.message_timer = 0
        self.return_scene = return_scene

        self.font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 28)
        self.title_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 40)
        self.small_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 22)
        # load SFX
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        def _load_sfx(base_name):
            sfx_dir = os.path.join("assets", "sfx")
            for ext in ("wav", "ogg", "mp3"):
                path = os.path.join(sfx_dir, f"{base_name}.{ext}")
                if os.path.exists(path):
                    try:
                        return pygame.mixer.Sound(path)
                    except Exception:
                        continue
            return None

        self.sfx_gunshot = _load_sfx("gunshot")
        self.sfx_slash = _load_sfx("slash")
        self.healthbar_frame = self.load_trimmed_image(os.path.join("assets", "ui", "healthbar.png"))
        self.mpbar_frame = self.load_trimmed_image(os.path.join("assets", "ui", "mp-bar.png"))
        self.battle_frame = self.load_trimmed_image(os.path.join("assets", "ui", "battle-frame.png"))
        self.long_wood = self.load_trimmed_image(os.path.join("assets", "ui", "long-wood.png"))
        self.short_wood = self.load_trimmed_image(os.path.join("assets", "ui", "short-wood.png"))
        self.scroll = self.load_trimmed_image(os.path.join("assets", "ui", "scroll.png"))
        battleground_path = os.path.join("assets", "ui", "battleground.png")
        boss_arena_path = os.path.join("assets", "ui", "boss-arena.png")
        if hasattr(enemy_entity, "__class__") and enemy_entity.__class__.__name__ == "EnemyBoss" and os.path.exists(boss_arena_path):
            battleground_path = boss_arena_path
        self.battleground = pygame.image.load(battleground_path).convert()
        self.battleground = pygame.transform.smoothscale(self.battleground, (self.screen_w, self.screen_h))

        # Change these values to resize or move the battle button frame.
        self.battle_frame_size = (260, 260)
        self.battle_frame_pos = (0, self.screen_h - self.battle_frame_size[1] - 0)

        available_width = max(320, self.screen_w - self.battle_frame_pos[0] - self.battle_frame_size[0] - 40)
        self.long_wood_size = (self.screen_w - self.battle_frame_pos[0] - self.battle_frame_size[0],200,)
        self.long_wood_pos = (
            self.screen_w - self.long_wood_size[0],
            self.screen_h - self.long_wood_size[1],
        )

        self.scroll_size = (max(280, self.long_wood_size[0] - 120), 150)
        self.scroll_pos = (
            self.long_wood_pos[0] + (self.long_wood_size[0] - self.scroll_size[0]) // 2,
            self.long_wood_pos[1] + 20,
        )

        # Player layout controls
        self.player_base_x = 170
        self.player_base_y = self.screen_h - 20
        self.enemy_scale = 2
        self.boss_scale = 2.2  # change this to adjust boss size in boss battles

        # player animation frames from newplayer1 assets
        self.frame_width = 64
        self.frame_height = 64
        self.player_attack1_frames = self.load_attack_frames(os.path.join("assets", "newplayer1", "attack"), None)
        self.player_attack2_frames = self.load_attack_frames(os.path.join("assets", "newplayer1", "double-slash"), None)
        self.player_idle_frames = self.load_attack_frames(os.path.join("assets", "newplayer1", "idle-stance"), None)
        if not self.player_idle_frames:
            raw_idle = getattr(self.player_entity, "idle_right", []) if self.player_entity else []
            if len(raw_idle) >= 8:
                stable_indices = [0, 4]
                self.player_idle_frames = [raw_idle[i] for i in stable_indices if i < len(raw_idle)]
            else:
                self.player_idle_frames = raw_idle

        self.player_anim_state = "idle"
        self.player_frame_index = 0.0
        self.player_idle_index = 0.0
        self.player_anim_speed = 14 / 60.0
        self.player_idle_speed = 6 / 60.0
        self.player_action = None
        self.skill_menu_open = False
        self.skill_options = ["Fireball", "Double Slash", "Back"]
        self.double_slash_power = (16, 28)

        # menu rects for mouse interaction
        self.menu_rects = []
        # initialize dynamic player state from the authoritative entity
        try:
            self.refresh_player_weapon_state()
        except Exception:
            pass

    def refresh_player_weapon_state(self):
        # sync dynamic player state from the entity so buffs persist into battle
        self.player["attack_power"] = getattr(self.player_entity, "attack_power", (12, 20))
        self.player["equipped_weapons"] = getattr(self.player_entity, "equipped_weapons", {"gun": None, "sword": None})
        self.player["blessed"] = getattr(self.player_entity, "blessed", False)
        self.player["max_hp"] = getattr(self.player_entity, "max_hp", self.player.get("max_hp", 120))
        self.player["hp"] = getattr(self.player_entity, "hp", self.player.get("hp", 120))
        self.player["max_mp"] = getattr(self.player_entity, "max_mp", self.player.get("max_mp", 40))
        self.player["mp"] = getattr(self.player_entity, "mp", self.player.get("mp", 40))

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
            self.refresh_player_weapon_state()
            if not self.player_attack1_frames:
                dmg = self.combat.attack(self.player, self.enemy_entity)
                self.set_message(f"You attack for {dmg} damage.")
                self.turn = "enemy"
                return None

            self.player_action = "attack"
            self.player_anim_state = "attack1"
            self.player_frame_index = 0.0
            self.player_idle_index = 0.0
            self.set_message("You slash the enemy.")
            self.turn = "busy"
            return None

        if choice == "Defend":
            self.combat.defend(self.player)
            self.set_message("You brace for the next attack.")
            self.turn = "enemy"
            return None

        if choice == "Skills":
            self.menu_options = self.skill_options
            self.selected = 0
            return None

        if choice == "Fireball":
            cost = 8
            if self.player["mp"] < cost:
                self.set_message("Not enough MP for Fireball.")
                self.turn = "player"
                return None
            self.player["mp"] -= cost
            self.player_action = "fireball"
            self.player_anim_state = "attack1"
            self.player_frame_index = 0.0
            self.player_idle_index = 0.0
            self.set_message("You cast Fireball!")
            self.turn = "busy"
            self.menu_options = ["Attack", "Defend", "Skills", "Item", "Run"]
            self.selected = 0
            return None

        if choice == "Double Slash":
            cost = 10
            if self.player["mp"] < cost:
                self.set_message("Not enough MP for Double Slash.")
                self.turn = "player"
                return None
            if not self.player_attack2_frames:
                self.set_message("Double Slash unavailable.")
                self.turn = "player"
                return None
            self.refresh_player_weapon_state()
            base_range = self.player["attack_power"]
            sword = self.player.get("equipped_weapons", {}).get("sword")
            if sword == "Cutlass":
                self.double_slash_power = (base_range[0] + 4, base_range[1] + 8)
            else:
                self.double_slash_power = (max(12, base_range[0]), base_range[1] + 4)
            self.player["mp"] -= cost
            self.player_action = "double_slash"
            self.player_anim_state = "attack2"
            self.player_frame_index = 0.0
            self.player_idle_index = 0.0
            self.set_message("You perform Double Slash!")
            self.turn = "busy"
            self.menu_options = ["Attack", "Defend", "Skills", "Item", "Run"]
            self.selected = 0
            return None

        if choice == "Back":
            self.menu_options = ["Attack", "Defend", "Skills", "Item", "Run"]
            self.selected = 0
            return None

        if choice == "Item":
            ok, msg, val = self.combat.use_item(self.player, "potion")
            self.set_message(msg)
            # persist healed HP back to the player entity
            try:
                if hasattr(self.player_entity, 'hp'):
                    self.player_entity.hp = int(self.player.get('hp', getattr(self.player_entity, 'hp', 0)))
            except Exception:
                pass
            # Trigger enemy attack animation
            try:
                if hasattr(self.enemy_entity, 'set_state'):
                    self.enemy_entity.set_state("attack")
            except Exception:
                pass
            self.set_message("Enemy attacks!")
            self.message_timer = pygame.time.get_ticks()
            self.turn = "enemy_attack"
            return None

        if choice == "Run":
            success = self.combat.try_run(self.player, self.enemy_entity, base_chance=0.6)
            if success:
                self.set_message("You successfully ran away!")
                return ("switch_scene", self.return_scene)
            else:
                self.set_message("Failed to run away!")
                self.turn = "enemy"
                return None

    def load_attack_frames(self, folder, prefix):
        frames = []
        try:
            if not os.path.isdir(folder):
                return frames
            candidates = []
            for fname in sorted(os.listdir(folder)):
                lname = fname.lower()
                if not lname.endswith(".png"):
                    continue
                if prefix and (prefix not in lname or "right" not in lname):
                    continue
                candidates.append(fname)

            def sort_key(name):
                digits = re.findall(r"(\d+)", name)
                return int(digits[-1]) if digits else name.lower()

            use_candidates = sorted(candidates, key=sort_key)

            for fname in use_candidates:
                path = os.path.join(folder, fname)
                sheet = pygame.image.load(path).convert_alpha()
                sheet_w, sheet_h = sheet.get_size()

                # If this folder contains multiple frames, treat each PNG as its own frame.
                if len(use_candidates) > 1:
                    frames.append(sheet)
                    continue

                # If this is a single image with a wide 8-frame layout, slice it.
                if sheet_h > 0 and sheet_w == sheet_h * 8:
                    frame_width = sheet_h
                    cols = 8
                    for i in range(cols):
                        frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, sheet_h)).copy()
                        frames.append(frame)
                else:
                    frames.append(sheet)
        except Exception:
            pass
        return frames

    def load_trimmed_image(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            bounds = image.get_bounding_rect()
            if bounds.width > 0 and bounds.height > 0:
                return image.subsurface(bounds).copy()
            return image
        except Exception:
            return None

    # UPDATE
    def update(self):
        # check end conditions
        if getattr(self.enemy_entity, "hp", 0) <= 0:
            # increment player's demon kill count when applicable
            try:
                from entities.enemy_demon import EnemyDemon
                if isinstance(self.enemy_entity, EnemyDemon):
                    try:
                        # global counter
                        self.player_entity.enemy_demon_kills += 1
                        # quest counter increments only if quest active and not blessed
                        if getattr(self.player_entity, 'quest_active', False) and not getattr(self.player_entity, 'quest_rewards_given', False):
                            self.player_entity.quest_demon_kills = getattr(self.player_entity, 'quest_demon_kills', 0) + 1
                    except Exception:
                        pass
            except Exception:
                pass
            self.set_message("Enemy defeated!")
            # ensure entity HP reflects current battle HP before exiting
            try:
                if hasattr(self.player_entity, 'hp'):
                    self.player_entity.hp = int(self.player.get('hp', getattr(self.player_entity, 'hp', 0)))
            except Exception:
                pass
            return ("switch_scene", self.return_scene)
            return ("switch_scene", self.return_scene)

        if self.player["hp"] <= 0:
            self.set_message("You were defeated...")
            # force one HP on return to overworld
            try:
                if hasattr(self.player_entity, 'hp'):
                    self.player_entity.hp = 1
                self.player["hp"] = 1
            except Exception:
                pass
            return ("switch_scene", self.return_scene)

        if self.player_anim_state == "attack1":
            self.player_frame_index += self.player_anim_speed
            if self.player_frame_index >= len(self.player_attack1_frames):
                if self.player_action == "double_slash":
                    self.player_anim_state = "attack2"
                    self.player_frame_index = 0.0
                    self.set_message("Double Slash!")
                    self.message_timer = pygame.time.get_ticks()
                else:
                    # play gunshot SFX for attack if available
                    try:
                        if getattr(self, 'sfx_gunshot', None):
                            self.sfx_gunshot.set_volume(max(0.0, min(1.0, SFX_VOLUME / 100)))
                            self.sfx_gunshot.play()
                    except Exception:
                        pass
                    dmg = self.combat.attack(self.player, self.enemy_entity)
                    self.set_message(f"You hit for {dmg} damage.")
                    try:
                        if hasattr(self.enemy_entity, 'set_state'):
                            self.enemy_entity.set_state("hurt")
                    except Exception:
                        pass
                    self.player_anim_state = "idle"
                    self.player_frame_index = 0.0
                    self.player_idle_index = 0.0
                    self.player_action = None
                    self.turn = "enemy_hurt"
        elif self.player_anim_state == "attack2":
            self.player_frame_index += self.player_anim_speed
            if self.player_frame_index >= len(self.player_attack2_frames):
                # play slash SFX for double slash if available
                try:
                    if getattr(self, 'sfx_slash', None):
                        self.sfx_slash.set_volume(max(0.0, min(1.0, SFX_VOLUME / 100)))
                        self.sfx_slash.play()
                except Exception:
                    pass
                dmg = self.combat.attack(self.player, self.enemy_entity, power_range=self.double_slash_power)
                self.set_message(f"Double Slash hits for {dmg} damage.")
                try:
                    if hasattr(self.enemy_entity, 'set_state'):
                        self.enemy_entity.set_state("hurt")
                except Exception:
                    pass
                self.player_anim_state = "idle"
                self.player_frame_index = 0.0
                self.player_idle_index = 0.0
                self.player_action = None
                self.turn = "enemy_hurt"
        else:
            if self.player_idle_frames:
                self.player_idle_index += self.player_idle_speed
                if self.player_idle_index >= len(self.player_idle_frames):
                    self.player_idle_index = 0.0

        # update enemy animation/state
        try:
            if hasattr(self.enemy_entity, 'update'):
                self.enemy_entity.update()
            else:
                if hasattr(self.enemy_entity, 'animate'):
                    self.enemy_entity.animate()
        except Exception:
            pass

        # update boss area NPC animation if present
        try:
            if hasattr(self, 'boss_npc') and self.boss_npc is not None and hasattr(self.boss_npc, 'update'):
                self.boss_npc.update()
        except Exception:
            pass

        if self.turn == "enemy_hurt":
            finished = False
            try:
                finished = getattr(self.enemy_entity, 'is_animation_finished', lambda: True)()
            except Exception:
                finished = True

            if finished:
                try:
                    if hasattr(self.enemy_entity, 'set_state'):
                        self.enemy_entity.set_state("attack")
                except Exception:
                    pass
                self.set_message("Enemy attacks!")
                self.message_timer = pygame.time.get_ticks()
                self.turn = "enemy_attack"
            return None

        if self.turn == "enemy_attack":
            attack_finished = False
            try:
                attack_finished = getattr(self.enemy_entity, 'is_animation_finished', lambda: True)()
            except Exception:
                attack_finished = True

            if not attack_finished:
                return None

            dmg = self.combat.attack(self.enemy_entity, self.player)
            self.set_message(f"Enemy hits for {dmg} damage.")
            self.message_timer = pygame.time.get_ticks()
            try:
                if hasattr(self.enemy_entity, 'set_state'):
                    self.enemy_entity.set_state("idle")
            except Exception:
                pass
            try:
                if hasattr(self.player_entity, 'hp'):
                    self.player_entity.hp = int(self.player.get('hp', getattr(self.player_entity, 'hp', 0)))
            except Exception:
                pass
            self.turn = "player"
            return None

        if self.turn == "enemy":
            if pygame.time.get_ticks() - self.message_timer < 600:
                return None

            dmg = self.combat.attack(self.enemy_entity, self.player)
            self.set_message(f"Enemy hits for {dmg} damage.")
            self.message_timer = pygame.time.get_ticks()
            # persist damage back to the player entity so battle state remains authoritative
            try:
                if hasattr(self.player_entity, 'hp'):
                    self.player_entity.hp = int(self.player.get('hp', getattr(self.player_entity, 'hp', 0)))
            except Exception:
                pass
            self.turn = "player"

        return None

    # DRAW HELPERS
    def draw_label_text(self, text, center, color=(245, 230, 170)):
        shadow = self.font.render(text, True, (18, 12, 8))
        label = self.font.render(text, True, color)
        shadow_rect = shadow.get_rect(center=(center[0] + 2, center[1] + 2))
        label_rect = label.get_rect(center=center)
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(label, label_rect)

    def set_message(self, text, color=(0, 0, 0)):
        self.message = text
        self.message_color = color

    def draw_bar(self, x, y, w, h, current, maximum, fg=(200, 40, 40), bg=(60, 60, 60), label=None, frame_image=None):
        frame_source = frame_image or self.healthbar_frame
        if frame_source:
            pct = max(0, min(1.0, current / maximum if maximum else 0))
            frame_h = max(h, int(w * frame_source.get_height() / frame_source.get_width()))
            frame = pygame.transform.smoothscale(frame_source, (w, frame_h))

            inner_x = x + int(w * 0.226)
            inner_y = y + int(frame_h * 0.286)
            inner_w = int(w * 0.704)
            inner_h = int(frame_h * 0.449)
            pygame.draw.rect(self.screen, bg, (inner_x, inner_y, inner_w, inner_h))
            pygame.draw.rect(self.screen, fg, (inner_x, inner_y, int(inner_w * pct), inner_h))
            self.screen.blit(frame, (x, y))
            if label:
                self.draw_label_text(label, (inner_x + inner_w // 2, inner_y + inner_h // 2))
            return frame_h

        pygame.draw.rect(self.screen, bg, (x, y, w, h))
        pct = max(0, min(1.0, current / maximum if maximum else 0))
        pygame.draw.rect(self.screen, fg, (x, y, int(w * pct), h))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, w, h), 2)
        if label:
            self.draw_label_text(label, (x + w // 2, y + h // 2))
        return h

    # DRAW
    def draw(self):
        if getattr(self, "battleground", None):
            self.screen.blit(self.battleground, (0, 0))
        else:
            self.screen.fill((18, 18, 28))

        center_x = self.screen.get_width() // 2

        title = self.title_font.render("Battle", True, (200, 200, 220))
        # Draw a decorative short-wood behind the title if available
        if getattr(self, "short_wood", None):
            try:
                pad = 60
                target_w = max(120, title.get_width() + pad)
                short_h = int(self.short_wood.get_height() * (target_w / max(1, self.short_wood.get_width())))
                short_img = pygame.transform.smoothscale(self.short_wood, (target_w, short_h))
                self.screen.blit(short_img, short_img.get_rect(center=(center_x, 40)))
            except Exception:
                pass
        self.screen.blit(title, title.get_rect(center=(center_x, 40)))

        # enemy on right
        enemy_img = getattr(self.enemy_entity, "image", None)
        if enemy_img:
            enemy_img = pygame.transform.smoothscale(
                enemy_img,
                (
                    int(enemy_img.get_width() * self.enemy_scale),
                    int(enemy_img.get_height() * self.enemy_scale),
                ),
            )
            enemy_rect = enemy_img.get_rect(center=(center_x + 260, self.screen.get_height() // 2 - 40))
            self.screen.blit(enemy_img, enemy_rect)

            # boss NPC overlay for boss battle
            if getattr(self, 'boss_npc', None) is not None:
                try:
                    if hasattr(self.boss_npc, 'images') and self.boss_npc.images:
                        idx = int(self.boss_npc.frame) % len(self.boss_npc.images)
                        boss_img = self.boss_npc.images[idx]
                        scaled_boss = pygame.transform.scale(
                            boss_img,
                            (
                                int(boss_img.get_width() * self.boss_scale),
                                int(boss_img.get_height() * self.boss_scale),
                            ),
                        )
                        boss_rect = scaled_boss.get_rect(center=(enemy_rect.centerx, enemy_rect.centery - 50))
                        self.screen.blit(scaled_boss, boss_rect)
                except Exception:
                    pass

        # player on left (use attack animation when playing)
        player_img = None
        if self.player_anim_state == "attack1" and self.player_attack1_frames:
            idx = int(self.player_frame_index) % max(1, len(self.player_attack1_frames))
            player_img = self.player_attack1_frames[idx]
        elif self.player_anim_state == "attack2" and self.player_attack2_frames:
            idx = int(self.player_frame_index) % max(1, len(self.player_attack2_frames))
            player_img = self.player_attack2_frames[idx]
        elif self.player_idle_frames:
            idx = int(self.player_idle_index) % max(1, len(self.player_idle_frames))
            player_img = self.player_idle_frames[idx]
        else:
            player_img = getattr(self.player_entity, "image", None)

        if player_img:
            # Scale the player to a sensible size and anchor them to the bottom-left
            original_w = player_img.get_width()
            original_h = player_img.get_height()
            max_width_scale = (self.screen.get_width() * 0.35) / original_w
            max_height_scale = (self.screen.get_height() - 180) / original_h
            combat_scale = min(1.1, max_width_scale, max_height_scale)
            combat_scale = max(0.28, combat_scale)

            scaled_w = int(original_w * combat_scale)
            scaled_h = int(original_h * combat_scale)
            player_img = pygame.transform.smoothscale(player_img, (scaled_w, scaled_h))

            player_rect = player_img.get_rect(bottomleft=(self.player_base_x, self.player_base_y))
            self.screen.blit(player_img, player_rect)

        # HUD bars (player)
        self.draw_bar(
            30,
            18,
            400,
            90,
            self.player["hp"],
            self.player["max_hp"],
            fg=(36, 205, 47),
            label=f"HP {self.player['hp']} / {self.player['max_hp']}",
        )
        self.draw_bar(
            30,
            18 + 90 + 10,
            300,
            40,
            self.player["mp"],
            self.player["max_mp"],
            fg=(80, 150, 240),
            label=f"MP {self.player['mp']} / {self.player['max_mp']}",
            frame_image=self.mpbar_frame,
        )

        equipped = self.player.get("equipped_weapons", {"gun": None, "sword": None})
        parts = []
        if equipped.get("gun"):
            parts.append(f"Gun: {equipped.get('gun')}")
        if equipped.get("sword"):
            parts.append(f"Sword: {equipped.get('sword')}")
        if parts:
            weapon_text = self.small_font.render(f"Weapons: {', '.join(parts)}", True, (210, 210, 255))
            self.screen.blit(weapon_text, (30, 18 + 90 + 10 + 50))

        enemy_hp = int(getattr(self.enemy_entity, "hp", getattr(self.enemy_entity, "max_hp", 0)))
        enemy_max = int(getattr(self.enemy_entity, "max_hp", 1))
        enemy_bar_x = self.screen.get_width() - 420
        self.draw_bar(
            enemy_bar_x,
            18,
            400,
            90,
            enemy_hp,
            enemy_max,
            fg=(190, 38, 38),
            label=f"HP {enemy_hp} / {enemy_max}",
        )

        # Action menu
        frame_x, frame_y = self.battle_frame_pos
        frame_w, frame_h = self.battle_frame_size
        wood_x, wood_y = self.long_wood_pos
        wood_w, wood_h = self.long_wood_size

        if self.long_wood:
            wood = pygame.transform.smoothscale(self.long_wood, self.long_wood_size)
            self.screen.blit(wood, self.long_wood_pos)
        else:
            pygame.draw.rect(self.screen, (70, 42, 20), (wood_x, wood_y, wood_w, wood_h))

        if self.scroll:
            scroll = pygame.transform.smoothscale(self.scroll, self.scroll_size)
            self.screen.blit(scroll, self.scroll_pos)
        else:
            scroll_x, scroll_y = self.scroll_pos
            scroll_w, scroll_h = self.scroll_size
            pygame.draw.rect(self.screen, (210, 178, 115), (scroll_x, scroll_y, scroll_w, scroll_h))

        if self.battle_frame:
            frame = pygame.transform.smoothscale(self.battle_frame, self.battle_frame_size)
            self.screen.blit(frame, self.battle_frame_pos)
        else:
            pygame.draw.rect(self.screen, (64, 40, 24), (frame_x, frame_y, frame_w, frame_h))
            pygame.draw.rect(self.screen, (180, 120, 55), (frame_x, frame_y, frame_w, frame_h), 4)

        menu_x = frame_x + 62
        menu_y = frame_y + 36
        self.menu_rects = []
        for i, opt in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected and self.turn == "player" else (180, 180, 180)
            opt_text = self.font.render(opt, True, color)
            rect = opt_text.get_rect(topleft=(menu_x, menu_y + i * 34))
            self.screen.blit(opt_text, rect)
            self.menu_rects.append(rect)

        # Message
        msg_text = self.font.render(self.message, True, getattr(self, "message_color", (0, 0, 0)))
        scroll_x, scroll_y = self.scroll_pos
        scroll_w, scroll_h = self.scroll_size
        self.screen.blit(msg_text, msg_text.get_rect(center=(scroll_x + scroll_w // 2, scroll_y + scroll_h // 2)))
