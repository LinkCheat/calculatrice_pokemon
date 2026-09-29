from enum import Enum

class MoveCategory(Enum):
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"

    def __repr__(self):
            return self.value