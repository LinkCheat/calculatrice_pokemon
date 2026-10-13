try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class LeechSeed(Moves):
    def __init__(self):
        """Create the Grass-type status move Leech Seed."""
        super().__init__(
            name="Leech Seed",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=90,
            max_pp=10,
            grass_type_immune=True,
        )

    def effect(self, user, target):
        """Seed the target until it leaves the field, unless already seeded."""
        return self.inflict_leech_seed(target)
