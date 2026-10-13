from enum import Enum


class Ability(Enum):
    NONE = ""
    INTIMIDATION = "Intimidation"

    def __repr__(self):
        """Display the ability's human-readable name."""
        return self.value
