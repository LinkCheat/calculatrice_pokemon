try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class VineWhip(Moves):
    def __init__(self):
        """Create the Grass-type physical move Vine Whip."""
        super().__init__(
            name="Vine Whip",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=45,
            accuracy=100,
            max_pp=25,
            contact=True,
        )

    def effect(self, user, target):
        """Vine Whip has no secondary effect."""
        return None
