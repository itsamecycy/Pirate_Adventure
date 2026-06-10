import random

from entities.enemy_demon import EnemyDemon
from entities.enemy_boss import EnemyBoss


class CombatSystem:
    """
    Simple Pokemon-style random encounter system.
    """

    def __init__(
        self,
        screen=None,
        encounter_chance=8,
        steps_per_check=1,
        enemy_pool=None,
    ):
        self.screen = screen

        self.encounter_chance = max(
            0,
            min(100, encounter_chance)
        )

        self.steps_per_check = max(
            1,
            int(steps_per_check)
        )

        self.step_counter = 0

        # IMPORTANT:
        # Boss is NOT included here.
        if enemy_pool is None:
            self.enemy_pool = [
                (EnemyDemon, 1)
            ]
        else:
            self.enemy_pool = enemy_pool

        self._build_weighted()

        self.enabled = True

    def _build_weighted(self):

        self._choices = []

        for cls, w in self.enemy_pool:

            if w <= 0:
                continue

            self._choices.extend(
                [cls] * int(w)
            )

        if not self._choices:
            self._choices = [EnemyDemon]

    def player_step(self, player_x, player_y):

        if not self.enabled:
            return None

        self.step_counter += 1

        if self.step_counter < self.steps_per_check:
            return None

        self.step_counter = 0

        roll = random.random() * 100

        if roll < self.encounter_chance:

            cls = random.choice(
                self._choices
            )

            ex = player_x + 32
            ey = player_y

            try:
                enemy = cls(ex, ey)
            except Exception:
                enemy = EnemyDemon(ex, ey)

            return enemy

        return None

    def set_encounter_chance(self, percent):

        self.encounter_chance = max(
            0,
            min(100, percent)
        )

    def change_encounter_chance(self, delta):

        self.set_encounter_chance(
            self.encounter_chance + delta
        )

    def set_encounters_enabled(
        self,
        enabled: bool
    ):
        self.enabled = bool(enabled)

    def toggle_encounters(self):

        self.enabled = not self.enabled

        return self.enabled

    # ---------------------------------
    # Helpers
    # ---------------------------------

    def _get(
        self,
        entity,
        key,
        default=0
    ):

        if entity is None:
            return default

        if isinstance(entity, dict):
            return entity.get(
                key,
                default
            )

        return getattr(
            entity,
            key,
            default
        )

    def _set(
        self,
        entity,
        key,
        value
    ):

        if entity is None:
            return

        if isinstance(entity, dict):

            entity[key] = value

        else:

            try:
                setattr(
                    entity,
                    key,
                    value
                )
            except Exception:
                pass

    # ---------------------------------
    # Combat
    # ---------------------------------

    def attack(
        self,
        attacker,
        defender,
        power_range=None
    ):

        # Attacker damage; allow object or dict based attack_power.
        attack_power = None
        if isinstance(attacker, dict):
            attack_power = attacker.get("attack_power")
        else:
            attack_power = getattr(attacker, "attack_power", None)

        if attack_power is not None and power_range is None:
            dmg = random.randint(attack_power[0], attack_power[1])
        else:
            if power_range is None:
                power_range = (12, 20)
            dmg = random.randint(power_range[0], power_range[1])

        # Apply boss->player blessing damage reduction if applicable
        attacker_is_boss = isinstance(attacker, EnemyBoss)

        defending = bool(
            self._get(
                defender,
                "defending",
                False
            )
        )

        # reduce boss damage by ~20% if defender is blessed
        if attacker_is_boss and self._get(defender, 'blessed', False):
            try:
                dmg = int(dmg * 0.8)
            except Exception:
                pass

        if defending:
            dmg //= 2

        hp = int(
            self._get(
                defender,
                "hp",
                self._get(
                    defender,
                    "max_hp",
                    0
                )
            )
        )

        new_hp = max(
            0,
            hp - dmg
        )

        self._set(
            defender,
            "hp",
            new_hp
        )

        if defending:

            self._set(
                defender,
                "defending",
                False
            )

        return dmg

    def defend(self, entity):

        self._set(
            entity,
            "defending",
            True
        )

        return True

    def skill(
        self,
        attacker,
        defender,
        name="fireball"
    ):

        if name == "fireball":

            cost = 8

            mp = int(
                self._get(
                    attacker,
                    "mp",
                    self._get(
                        attacker,
                        "max_mp",
                        0
                    )
                )
            )

            if mp < cost:
                return (
                    False,
                    "Not enough MP",
                    0
                )

            self._set(
                attacker,
                "mp",
                max(
                    0,
                    mp - cost
                )
            )

            dmg = random.randint(
                24,
                34
            )

            hp = int(
                self._get(
                    defender,
                    "hp",
                    self._get(
                        defender,
                        "max_hp",
                        0
                    )
                )
            )

            self._set(
                defender,
                "hp",
                max(
                    0,
                    hp - dmg
                )
            )

            return (
                True,
                f"{name.title()} hits for {dmg}",
                dmg
            )

        return (
            False,
            "Unknown skill",
            0
        )

    def use_item(
        self,
        user,
        item_name="potion"
    ):

        if item_name == "potion":

            heal = 40

            hp = int(
                self._get(
                    user,
                    "hp",
                    self._get(
                        user,
                        "max_hp",
                        0
                    )
                )
            )

            max_hp = int(
                self._get(
                    user,
                    "max_hp",
                    hp
                )
            )

            new_hp = min(
                max_hp,
                hp + heal
            )

            self._set(
                user,
                "hp",
                new_hp
            )

            return (
                True,
                f"Healed {new_hp - hp} HP",
                new_hp - hp
            )

        return (
            False,
            "Unknown item",
            0
        )

    def try_run(
        self,
        player,
        enemy,
        base_chance=0.6
    ):

        return (
            random.random()
            < base_chance
        )