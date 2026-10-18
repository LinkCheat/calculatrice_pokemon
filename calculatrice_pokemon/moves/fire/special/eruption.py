try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Eruption(Moves):
    def __init__(self):
        """Create the Fire-type special move Eruption."""
        super().__init__(
            name="Eruption",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=150,
            accuracy=100,
            max_pp=5,
        )

    def get_power(self, user, target, field=None):
        """Scale power with the user's current HP, with a minimum of one."""
        return max(1, self.power * user.current_hp // user.max_hp)

    def effect(self, user, target):
        """Eruption has no secondary effect."""
        return None
