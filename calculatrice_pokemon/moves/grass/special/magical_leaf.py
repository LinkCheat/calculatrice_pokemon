try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MagicalLeaf(Moves):
    def __init__(self):
        """Create the Grass-type special move Magical Leaf."""
        super().__init__(
            name="Magical Leaf",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=60,
            accuracy=101,
            max_pp=20,
        )

    def effect(self, user, target):
        """Magical Leaf has no secondary effect."""
        return None
