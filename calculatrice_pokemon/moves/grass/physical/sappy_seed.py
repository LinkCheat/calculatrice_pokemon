try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SappySeed(Moves):
    def __init__(self):
        """Create the Grass-type physical move Sappy Seed."""
        super().__init__(
            name="Sappy Seed",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=90,
            accuracy=100,
            max_pp=15,
            grass_type_immune=True,
        )

    def effect(self, user, target):
        """Apply Leech Seed to the target after a successful damaging hit."""
        return self.inflict_leech_seed(target)
