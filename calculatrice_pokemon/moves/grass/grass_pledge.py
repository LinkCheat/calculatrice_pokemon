try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class GrassPledge(Moves):
    def __init__(self):
        """Create the Grass-type special move Grass Pledge."""
        super().__init__(
            name="Grass Pledge",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Grass Pledge has no secondary effect."""
        return None
