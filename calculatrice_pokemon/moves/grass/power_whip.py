try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class PowerWhip(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Power Whip."""
        super().__init__(
            name="Power Whip",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=85,
            max_pp=10,
            contact=True,
        )

    def effect(self, user, target):
        """Power Whip has no secondary effect."""
        return None
