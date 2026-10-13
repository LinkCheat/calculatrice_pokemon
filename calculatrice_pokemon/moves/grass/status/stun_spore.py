try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class StunSpore(Moves):
    def __init__(self):
        """Create the Grass-type powder move Stun Spore."""
        super().__init__(
            name="Stun Spore",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=75,
            max_pp=30,
            powder=True,
            electric_type_immune=True,
        )

    def effect(self, user, target):
        """Paralyze the target if it is not already affected by a status."""
        return self.inflict_paralysis(target)
