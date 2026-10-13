try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class GrassKnot(Moves):
    def __init__(self):
        """Create the Grass-type special move Grass Knot."""
        super().__init__(
            name="Grass Knot",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=0,
            accuracy=100,
            max_pp=20,
        )

    def get_power(self, user, target, field=None):
        """Return power based on the target's weight in kilograms."""
        if target.weight <= 10:
            return 20
        if target.weight <= 25:
            return 40
        if target.weight <= 50:
            return 60
        if target.weight <= 100:
            return 80
        if target.weight <= 200:
            return 100
        return 120

    def effect(self, user, target):
        """Grass Knot has no secondary effect."""
        return None
