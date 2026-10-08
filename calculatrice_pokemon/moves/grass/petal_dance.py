import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class PetalDance(Moves):
    def __init__(self):
        """Create the Grass-type special move Petal Dance."""
        super().__init__(
            name="Petal Dance",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=120,
            accuracy=100,
            max_pp=10,
        )

    def get_lock_turn_count(self, user, target):
        """Lock the user into Petal Dance for two or three attacks."""
        return random.randint(2, 3)

    def confuses_user_after_lock(self):
        return True

    def effect(self, user, target):
        """Petal Dance has no effect on its target beyond damage."""
        return None
