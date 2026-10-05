try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BranchPoke(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Branch Poke."""
        super().__init__(
            name="Branch Poke",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            max_pp=40,
            contact=True,
        )

    def effect(self, user, target):
        """Branch Poke has no secondary effect."""
        return None
