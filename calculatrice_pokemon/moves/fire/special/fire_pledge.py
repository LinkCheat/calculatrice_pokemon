try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FirePledge(Moves):
    def __init__(self):
        """Create the Fire-type special move Fire Pledge."""
        super().__init__(
            name="Fire Pledge",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Fire Pledge has no individual secondary effect."""
        return None
