try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SpikyShield(Moves):
    def __init__(self):
        """Create the Grass-type status move Spiky Shield."""
        super().__init__(
            name="Spiky Shield",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
            priority=4,
        )

    def is_protection_move(self):
        return True

    def effect(self, user, target):
        """Report that Spiky Shield successfully protected its user."""
        return {
            "name": self.name,
            "condition": "spiky_shield",
            "applied": True,
        }
