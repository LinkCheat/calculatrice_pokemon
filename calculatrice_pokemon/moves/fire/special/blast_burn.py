try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BlastBurn(Moves):
    def __init__(self):
        """Create the Fire-type special move Blast Burn."""
        super().__init__(
            name="Blast Burn",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=150,
            accuracy=90,
            max_pp=5,
        )

    def requires_recharge_after_use(self):
        """Require a recovery turn after Blast Burn hits."""
        return True

    def effect(self, _user, _target):
        """Blast Burn has no additional effect."""
        return None
