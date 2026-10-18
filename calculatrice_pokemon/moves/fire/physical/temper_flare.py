try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class TemperFlare(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Temper Flare."""
        super().__init__(
            name="Temper Flare",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=75,
            accuracy=100,
            max_pp=10,
            contact=True,
        )

    def get_power(self, user, target, field=None):
        """Double power if the user's previous move failed."""
        if user.last_move_failed:
            return self.power * 2
        return self.power

    def effect(self, user, target):
        """Temper Flare has no secondary effect."""
        return None
