import os
import pygame


class Quartermaster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = []
        self.frame = 0.0
        self.frame_speed = 0.12
        self.rect = pygame.Rect(x, y, 48, 64)
        self.load_sprites()

    def load_sprites(self):
        folder = os.path.join("assets", "quartermaster")
        if not os.path.isdir(folder):
            return
        files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
        files = sorted(files)
        for fname in files:
            try:
                img = pygame.image.load(os.path.join(folder, fname)).convert_alpha()
                # scale images to ~50px radius (100x100)
                try:
                    img = pygame.transform.smoothscale(img, (100, 100))
                except Exception:
                    pass
                self.images.append(img)
            except Exception:
                continue
        if self.images:
            w, h = self.images[0].get_size()
            self.rect = pygame.Rect(self.x - w // 2, self.y - h // 2, w, h)

    def update(self):
        if not self.images:
            return
        self.frame += self.frame_speed
        if self.frame >= len(self.images):
            self.frame = 0.0

    def draw(self, screen):
        if not self.images:
            return
        idx = int(self.frame) % len(self.images)
        img = self.images[idx]
        screen.blit(img, self.rect.topleft)

    def interact(self, player, overworld):
        # player: Player instance
        # overworld: Overworld instance (for setting dialog)
        kills = getattr(player, 'quest_demon_kills', 0)
        blessed = getattr(player, 'blessed', False)

        if blessed:
            overworld.dialog_text = "Quartermaster: Your equipments are already blessed."
            overworld.dialog_timer = 3000
            return

        # If player hasn't started the quest, start it and instruct
        if not getattr(player, 'quest_active', False):
            player.quest_active = True
            # don't reset existing progress, but ensure counter exists
            player.quest_demon_kills = getattr(player, 'quest_demon_kills', 0)
            overworld.dialog_text = "Quartermaster: If you want to defeat Black Beard, defeat 10 enemy demon and I will bless your equipments"
            overworld.dialog_timer = 5000
            return

        # If quest active, check progress
        if kills >= 10:
            # apply blessing
            player.blessed = True
            player.max_hp = getattr(player, 'max_hp', 120) + 80
            player.hp = getattr(player, 'hp', 120) + 80
            # sync inventory/system attack state
            try:
                if hasattr(player, 'inventory_system'):
                    player.inventory_system.sync_from_owner()
            except Exception:
                pass
            overworld.dialog_text = "Quartermaster: I have blessed your equipments. Damage increased and Boss hits reduced."
            overworld.dialog_timer = 4000
        else:
            overworld.dialog_text = f"Quartermaster: You have defeated {kills}/10 demons. Keep going." 
            overworld.dialog_timer = 3500