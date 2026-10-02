from enum import Enum

class MoveCategory(Enum):
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"

    def __repr__(self):
        """Display the human-readable category name in representations."""
        return self.value