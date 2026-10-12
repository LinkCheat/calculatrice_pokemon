try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SleepPowder(Moves):
    def __init__(self):
        """Create the Grass-type powder move Sleep Powder."""
        super().__init__(
            name="Sleep Powder",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=75,
            max_pp=10,
            powder=True,
        )

    def effect(self, user, target):
        """Put an eligible target to sleep for one to three turns."""
        return self.inflict_sleep(target)
