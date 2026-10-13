try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Leafage(Moves):
    def __init__(self):
        """Create the Grass-type physical move Leafage."""
        super().__init__(
            name="Leafage",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            max_pp=40,
        )

    def effect(self, user, target):
        """Leafage has no secondary effect."""
        return None
