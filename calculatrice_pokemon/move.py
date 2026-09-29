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
    ):
        self.name = name
        self.type = move_type
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.priority = priority

    @abstractmethod
    def effect(self, user, target):
        """Applique l'effet réel de l'attaque."""
        raise NotImplementedError

    def use(self, user, target):
        """Méthode générique pour utiliser l'attaque."""
        return self.effect(user, target)

    def __str__(self):
        return f"{self.name} ({self.type.value})"

    def __repr__(self):
        return self.__str__()


# Exemple de structure concrète pour illustrer le principe
