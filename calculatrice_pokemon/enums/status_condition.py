from enum import Enum


class STATUS_CONDITION(Enum):
    NONE = ""
    BURN = "Burn"
    FREEZE = "Freeze"
    PARALYSIS = "Paralysis"
    POISON = "Poison"
    SLEEP = "Sleep"

    def __repr__(self):
        return self.value