try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Ingrain(Moves):
    def __init__(self):
        """Create the Grass-type status move Ingrain."""
        super().__init__(
            name="Ingrain",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=20,
        )

    def effect(self, user, target):
        """Root the user, granting end-of-turn healing and grounding."""
        user.ingrain_active = True
        return {
            "condition": "ingrain",
            "applied": True,
        }
