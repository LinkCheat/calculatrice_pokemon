try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class GrassWhistle(Moves):
    def __init__(self):
        """Create the Grass-type sound move Grass Whistle."""
        super().__init__(
            name="Grass Whistle",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=55,
            max_pp=15,
            sound=True,
        )

    def effect(self, user, target):
        """Put an eligible target to sleep for one to three turns."""
        return self.inflict_sleep(target)
