try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FlameBurst(Moves):
    def __init__(self):
        """Create the Fire-type special move Flame Burst."""
        super().__init__(
            name="Flame Burst",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=70,
            accuracy=100,
            max_pp=15,
        )

    def effect(self, _user, _target):
        """Flame Burst has no additional effect in single battles."""
        return None
