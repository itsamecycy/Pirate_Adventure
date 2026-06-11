class InventorySystem:
    """Inventory manager for equipping and unequipping weapons."""

    VALID_WEAPONS = {
        "Cutlass": {
            "category": "sword",
            "attack_power": (20, 30),
            "description": "A sharp pirate cutlass.",
        },
        "Pistol": {
            "category": "gun",
            "attack_power": (20, 30),
            "description": "A quick pistol for ranged attacks.",
        },
        "Golden Pistol": {
            "category": "gun",
            "attack_power": (40, 60),
            "description": "The gun of a once-known pirate. DMG: 40-60",
        },
        "Falchion Sword": {
            "category": "sword",
            "attack_power": (50, 75),
            "description": "The sword of a fine pirate. DMG: 50-75",
        },
    }

    EQUIP_CATEGORIES = {"gun", "sword"}

    def __init__(self, owner=None):
        self.owner = owner
        self.equipped_weapons = {"gun": None, "sword": None}
        self.inventory = {}

        if owner is not None:
            self.sync_from_owner()

    def sync_from_owner(self):
        if self.owner is None:
            return

        self.inventory = getattr(self.owner, "items", {}) or {}
        self.equipped_weapons = getattr(self.owner, "equipped_weapons", {"gun": None, "sword": None})
        self._sync_owner_attack_state()

    def sync_to_owner(self):
        if self.owner is None:
            return

        self.owner.items = self.inventory
        self.owner.equipped_weapons = self.equipped_weapons
        self._sync_owner_attack_state()

    def _sync_owner_attack_state(self):
        if self.owner is None:
            return
        # Ensure we remember the owner's base max HP so bonuses don't stack
        if not hasattr(self.owner, '_base_max_hp'):
            try:
                self.owner._base_max_hp = int(getattr(self.owner, 'max_hp', 120))
            except Exception:
                self.owner._base_max_hp = 120

        # Determine if reward weapons are equipped
        equipped = [v for v in self.equipped_weapons.values() if v]
        has_reward_weapon = any(w in ("Golden Pistol", "Falchion Sword") for w in equipped)

        # Apply HP bonus when reward weapons are equipped
        bonus_hp = 80 if has_reward_weapon else 0
        base_max = getattr(self.owner, '_base_max_hp', 120)
        new_max_hp = base_max + bonus_hp

        # Adjust current HP sensibly: if the player was at or below base, boost by bonus
        current_hp = int(getattr(self.owner, 'hp', new_max_hp))
        if bonus_hp and current_hp <= base_max:
            current_hp = min(new_max_hp, current_hp + bonus_hp)
        else:
            current_hp = min(new_max_hp, current_hp)

        self.owner.max_hp = new_max_hp
        self.owner.hp = current_hp

        # Boss damage reduction when reward weapons are equipped
        self.owner.boss_damage_reduction = 0.2 if has_reward_weapon else 0.0

        # Base attack comes from owner; if a gun is equipped override attack power.
        gun = self.equipped_weapons.get("gun")
        if gun:
            atk = self.weapon_attack_power(gun)
            # apply blessing multiplier if owner blessed
            if getattr(self.owner, 'blessed', False):
                mul_min = int(atk[0] * 1.25)
                mul_max = int(atk[1] * 1.25)
                atk = (mul_min, mul_max)
            self.owner.attack_power = atk
        else:
            # keep owner's default/base attack power
            base = getattr(self.owner, 'attack_power', (12, 20))
            if getattr(self.owner, 'blessed', False):
                base = (int(base[0] * 1.25), int(base[1] * 1.25))
            self.owner.attack_power = base

        self.owner.equipped_weapons = self.equipped_weapons

    def available_weapons(self):
        return [name for name in self.inventory if self.is_weapon(name) and self.inventory.get(name, 0) > 0]

    def is_weapon(self, item_name):
        return item_name in self.VALID_WEAPONS

    def weapon_category(self, item_name):
        return self.VALID_WEAPONS.get(item_name, {}).get("category")

    def weapon_attack_power(self, item_name):
        if item_name in self.VALID_WEAPONS:
            return self.VALID_WEAPONS[item_name]["attack_power"]
        return (12, 20)

    def can_equip(self, item_name):
        if item_name not in self.inventory:
            return False, "Item not in inventory"

        if self.inventory.get(item_name, 0) <= 0:
            return False, "No item quantity available"

        if not self.is_weapon(item_name):
            return False, "Item is not equipable"

        category = self.weapon_category(item_name)
        if category not in self.EQUIP_CATEGORIES:
            return False, f"Cannot equip item of category '{category}'"

        return True, "Can equip"

    def equip_weapon(self, item_name):
        can_equip, message = self.can_equip(item_name)
        if not can_equip:
            return False, message

        category = self.weapon_category(item_name)
        self.equipped_weapons[category] = item_name
        self._sync_owner_attack_state()
        self.sync_to_owner()
        return True, f"Equipped {item_name}"

    def unequip_weapon(self, item_name=None):
        if item_name is None:
            if not any(self.equipped_weapons.values()):
                return False, "No weapon equipped"
            self.equipped_weapons = {"gun": None, "sword": None}
            self._sync_owner_attack_state()
            self.sync_to_owner()
            return True, "Unequipped all weapons"

        category = self.weapon_category(item_name)
        if category is None:
            return False, "Item is not equipable"

        if self.equipped_weapons.get(category) != item_name:
            return False, "Weapon not equipped"

        self.equipped_weapons[category] = None
        self._sync_owner_attack_state()
        self.sync_to_owner()
        return True, f"Unequipped {item_name}"

    def is_equipped(self, item_name):
        return item_name in self.equipped_weapons.values()

    def add_item(self, item_name, quantity=1):
        if quantity <= 0:
            return False

        current = self.inventory.get(item_name, 0)
        self.inventory[item_name] = current + quantity
        self.sync_to_owner()
        return True

    def remove_item(self, item_name, quantity=1):
        if quantity <= 0:
            return False

        current = self.inventory.get(item_name, 0)
        if current < quantity:
            return False

        self.inventory[item_name] = current - quantity
        if self.inventory[item_name] <= 0:
            self.inventory.pop(item_name, None)

        if self.is_equipped(item_name) and self.inventory.get(item_name, 0) <= 0:
            self.unequip_weapon(item_name)

        self.sync_to_owner()
        return True
