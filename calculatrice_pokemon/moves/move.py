from abc import ABC, abstractmethod
from enum import Enum
import random

try:
    from enums.type import Type
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION





class Moves(ABC):
    def __init__(
        self,
        name: str,
        move_type: Type,
        category: MoveCategory,
        power: int = 0,
        accuracy: int = 100,
        priority: int = 0,
        max_pp: int = 35,

        contact: bool = False,
        powder: bool = False,
        grass_type_immune: bool = False,
    ):
        """Initialize move metadata and set current PP to the maximum PP.

        Raises:
            ValueError: If ``max_pp`` is less than one.
        """
        if max_pp < 1:
            raise ValueError("Les PP maximum d'une attaque doivent être supérieurs à zéro.")

        self.name = name
        self.type = move_type
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.priority = priority
        self.max_pp = max_pp
        self.pp = max_pp

        self.contact = contact
        self.powder = powder
        self.grass_type_immune = grass_type_immune

    @abstractmethod
    def effect(self, user, target):
        """Apply this move's move-specific effect and return its result."""
        raise NotImplementedError

    def apply_effect(self, user, target, damage_dealt):
        """Apply this move's effect after damage has been dealt."""
        return self.effect(user, target)

    def use(self, user, target):
        """Consume one PP and apply the move's effect to its target."""
        self.consume_pp()
        return self.effect(user, target)

    def consume_pp(self):
        """Spend one PP, raising ValueError if the move has no PP remaining."""
        if self.pp <= 0:
            raise ValueError(f"{self.name} n'a plus de PP et ne peut pas être utilisée.")

        self.pp -= 1

    def get_power(self, user, target, field=None):
        """Return this move's base power; subclasses can make it situational."""
        return self.power

    def get_priority(self, user, target, field=None):
        """Return this move's priority; subclasses can make it situational."""
        return self.priority

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Return this move's bonus to the critical-hit stage."""
        return 0

    def requires_charge(self, field):
        """Return whether this move needs a charging turn in the current field."""
        return False

    def get_hit_count(self, user, target):
        """Return the number of strikes this use of the move makes."""
        return 1

    def calculate_damage(self, user, target, standard_damage):
        """Return the calculated damage unchanged unless a subclass overrides it."""
        return standard_damage

    def inflict_sleep(self, target):
        """Put an unstatused target to sleep for one to three turns."""
        if target.status_condition is not None:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "already_statused",
            }

        sleep_turns = random.randint(1, 3)
        target.status_condition = STATUS_CONDITION.SLEEP
        target.sleep_turns_remaining = sleep_turns
        return {
            "name": self.name,
            "status": STATUS_CONDITION.SLEEP,
            "applied": True,
            "sleep_turns": sleep_turns,
        }

    def inflict_leech_seed(self, target):
        """Seed a living, unseeded target until it leaves the field."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "condition": "leech_seed",
                "applied": False,
                "reason": "target_fainted",
            }
        if target.leech_seeded:
            return {
                "name": self.name,
                "condition": "leech_seed",
                "applied": False,
                "reason": "already_seeded",
            }

        target.leech_seeded = True
        return {
            "name": self.name,
            "condition": "leech_seed",
            "applied": True,
        }

    def __str__(self):
        """Format the move name and type for display."""
        return f"{self.name} ({self.type.value})"

    def __repr__(self):
        """Use the display representation when inspecting the move."""
        return self.__str__()
