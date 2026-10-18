import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class RagingFury(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Raging Fury."""
        super().__init__(
            name="Raging Fury",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=100,
            max_pp=10,
            contact=True,
        )

    def get_lock_turn_count(self, user, target):
        """Lock the user into Raging Fury for two or three turns."""
        return random.randint(2, 3)

    def confuses_user_after_lock(self):
        """Confuse the user when its Raging Fury lock ends."""
        return True

    def effect(self, user, target):
        """Raging Fury has no additional effect on its target."""
        return None
