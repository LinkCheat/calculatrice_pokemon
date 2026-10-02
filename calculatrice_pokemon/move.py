from abc import ABC, abstractmethod
from enum import Enum
from enums.type import Type
from enums.move_category import MoveCategory





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

    @abstractmethod
    def effect(self, user, target):
        """Apply this move's move-specific effect and return its result."""
        raise NotImplementedError

    def use(self, user, target):
        """Consume one PP and apply the move's effect to its target."""
        self.consume_pp()
        return self.effect(user, target)

    def consume_pp(self):
        """Spend one PP, raising ValueError if the move has no PP remaining."""
        if self.pp <= 0:
            raise ValueError(f"{self.name} n'a plus de PP et ne peut pas être utilisée.")

        self.pp -= 1

    def get_power(self, user, target):
        """Return this move's base power; subclasses can make it situational."""
        return self.power

    def calculate_damage(self, user, target, standard_damage):
        """Return the calculated damage unchanged unless a subclass overrides it."""
        return standard_damage

    def __str__(self):
        """Format the move name and type for display."""
        return f"{self.name} ({self.type.value})"

    def __repr__(self):
        """Use the display representation when inspecting the move."""
        return self.__str__()
