try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class PetalBlizzard(Moves):
    def __init__(self):
        """Create the Grass-type physical move Petal Blizzard."""
        super().__init__(
            name="Petal Blizzard",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=90,
            accuracy=100,
            max_pp=15,
        )

    def effect(self, user, target):
        """Petal Blizzard has no secondary effect."""
        return None
