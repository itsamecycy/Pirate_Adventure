import random
from entities.enemy_demon import EnemyDemon


class CombatSystem:
    """Simple Pokemon-style random encounter system.

    Usage: call `player_step(x, y)` each time the player takes a step/moves.
    If an encounter occurs, `player_step` returns an enemy instance, otherwise None.
    """

    def __init__(self, screen=None, encounter_chance=8, steps_per_check=1, enemy_pool=None):
        self.screen = screen
        # percent chance per step (0-100)
        self.encounter_chance = max(0, min(100, encounter_chance))
        # perform a roll every N steps
        self.steps_per_check = max(1, int(steps_per_check))
        self.step_counter = 0

        # enemy_pool: list of (EnemyClass, weight)
        if enemy_pool is None:
            self.enemy_pool = [(EnemyDemon, 1)]
        else:
            self.enemy_pool = enemy_pool

        # build weighted list for random selection
        self._build_weighted()
        # encounters enabled flag (can be toggled to disable random encounters)
        self.enabled = True

    def _build_weighted(self):
        self._choices = []
        for cls, w in self.enemy_pool:
            if w <= 0:
                continue
            self._choices.extend([cls] * int(w))
        if not self._choices:
            self._choices = [EnemyDemon]

    def player_step(self, player_x, player_y):
        """Call when player moves. Returns enemy instance on encounter, else None."""
        # if encounters are disabled, never spawn
        if not getattr(self, "enabled", True):
            return None

        self.step_counter += 1
        if self.step_counter < self.steps_per_check:
            return None

        self.step_counter = 0
        roll = random.random() * 100
        if roll < self.encounter_chance:
            # pick enemy class
            cls = random.choice(self._choices)
            # spawn enemy near player
            ex = player_x + 32
            ey = player_y
            try:
                enemy = cls(ex, ey)
            except Exception:
                enemy = EnemyDemon(ex, ey)
            return enemy

        return None

    def set_encounter_chance(self, percent):
        self.encounter_chance = max(0, min(100, percent))

    def change_encounter_chance(self, delta):
        self.set_encounter_chance(self.encounter_chance + delta)

    def set_encounters_enabled(self, enabled: bool):
        """Enable or disable random encounters."""
        self.enabled = bool(enabled)

    def toggle_encounters(self):
        """Toggle encounters on/off and return the new state."""
        self.enabled = not getattr(self, "enabled", True)
        return self.enabled

    # -------------------------
    # Combat action helpers
    # -------------------------
    def _get(self, entity, key, default=0):
        if entity is None:
            return default
        if isinstance(entity, dict):
            return entity.get(key, default)
        return getattr(entity, key, default)

    def _set(self, entity, key, value):
        if entity is None:
            return
        if isinstance(entity, dict):
            entity[key] = value
        else:
            try:
                setattr(entity, key, value)
            except Exception:
                pass

    def attack(self, attacker, defender, power_range=(12, 20)):
        """Perform a basic attack from attacker to defender.

        attacker/defender can be objects with attributes or dicts with keys.
        Returns damage dealt (int).
        """
        dmg = random.randint(power_range[0], power_range[1])

        # apply defender defend flag if present
        defending = bool(self._get(defender, "defending", False))
        if defending:
            dmg = dmg // 2

        hp = int(self._get(defender, "hp", self._get(defender, "max_hp", 0)))
        new_hp = max(0, hp - dmg)
        self._set(defender, "hp", new_hp)

        # clear defending state after being hit
        if defending:
            self._set(defender, "defending", False)

        return dmg

    def defend(self, entity):
        """Set defending flag on entity (halves incoming damage)."""
        self._set(entity, "defending", True)
        return True

    def skill(self, attacker, defender, name="fireball"):
        """Perform a skill. Returns (success:bool, message:str, value:int).
        For fireball, consumes MP and deals damage.
        """
        if name == "fireball":
            cost = 8
            mp = int(self._get(attacker, "mp", self._get(attacker, "max_mp", 0)))
            if mp < cost:
                return False, "Not enough MP", 0
            # deduct mp
            self._set(attacker, "mp", max(0, mp - cost))
            dmg = random.randint(24, 34)
            hp = int(self._get(defender, "hp", self._get(defender, "max_hp", 0)))
            new_hp = max(0, hp - dmg)
            self._set(defender, "hp", new_hp)
            return True, f"{name.title()} hits for {dmg}", dmg

        return False, "Unknown skill", 0

    def use_item(self, user, item_name="potion"):
        """Apply an item effect. Returns (success,bool, message, value)."""
        if item_name == "potion":
            heal = 40
            hp = int(self._get(user, "hp", self._get(user, "max_hp", 0)))
            max_hp = int(self._get(user, "max_hp", hp))
            new_hp = min(max_hp, hp + heal)
            self._set(user, "hp", new_hp)
            # if inventory dict present, decrement
            if isinstance(user, dict) and isinstance(user.get("items"), dict):
                items = user.get("items")
                if items.get("potion", 0) > 0:
                    items["potion"] -= 1
            return True, f"Healed {new_hp - hp} HP", new_hp - hp

        return False, "Unknown item", 0

    def try_run(self, player, enemy, base_chance=0.6):
        """Attempt to flee. Returns True on success, False on failure."""
        roll = random.random()
        return roll < base_chance
