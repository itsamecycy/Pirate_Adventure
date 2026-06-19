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
        rewards_given = getattr(player, 'quest_rewards_given', False)

        # Fully restore HP and MP
        player.hp = getattr(player, 'max_hp', 120)
        player.mp = getattr(player, 'max_mp', 40)
        if hasattr(player, 'inventory_system') and player.inventory_system is not None:
            player.inventory_system.sync_to_owner()

        if rewards_given:
            overworld.dialog_text = "Quartermaster: You already received the rewards for completing the quest. Your HP and MP have been fully restored!"
            overworld.dialog_timer = 3000
            return

        # If player hasn't started the quest, start it and instruct
        if not getattr(player, 'quest_active', False):
            player.quest_active = True
            # don't reset existing progress, but ensure counter exists
            player.quest_demon_kills = getattr(player, 'quest_demon_kills', 0)
            overworld.dialog_text = "Quartermaster: If you want to defeat Black Beard, defeat 10 demons and I will reward you with powerful weapons. (HP & MP restored)"
            overworld.dialog_timer = 5000
            return

        # If quest active, check progress
        if kills >= 10:
            # Add reward weapons to inventory via the InventorySystem so they're equipable
            try:
                if hasattr(player, 'inventory_system') and player.inventory_system is not None:
                    player.inventory_system.add_item("Golden Pistol", 1)
                    player.inventory_system.add_item("Falchion Sword", 1)
                else:
                    # fallback: modify the raw items dict
                    player.items["Golden Pistol"] = player.items.get("Golden Pistol", 0) + 1
                    player.items["Falchion Sword"] = player.items.get("Falchion Sword", 0) + 1
            except Exception:
                # ensure items still get added in case of unexpected error
                player.items["Golden Pistol"] = player.items.get("Golden Pistol", 0) + 1
                player.items["Falchion Sword"] = player.items.get("Falchion Sword", 0) + 1

            # mark rewards given to prevent repeats (separate from 'blessed')
            player.quest_rewards_given = True
            overworld.dialog_text = "Quartermaster: Excellent work! Here are your rewards: Golden Pistol and Falchion Sword! (HP & MP restored)"
            overworld.dialog_timer = 4000
        else:
            overworld.dialog_text = f"Quartermaster: You have defeated {kills}/10 demons. Keep going. (HP & MP restored)" 
            overworld.dialog_timer = 3500
