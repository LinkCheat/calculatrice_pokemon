from enum import Enum


class Terrain(Enum):
    NONE = ""
    ELECTRIC = "Electric"
    GRASSY = "Grassy"
    MISTY = "Misty"
    PSYCHIC = "Psychic"

    def __repr__(self):
        """Display the terrain's human-readable name."""
        return self.value