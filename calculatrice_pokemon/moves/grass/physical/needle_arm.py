import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class NeedleArm(Moves):
    FLINCH_CHANCE = 0.3

    def __init__(self):
        """Create the Grass-type physical contact move Needle Arm."""
        super().__init__(
            name="Needle Arm",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=60,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Flinch a living target that has not acted yet, with 30% chance."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "flinched": False,
                "applied": False,
                "reason": "target_fainted",
            }
        if target.has_acted_this_turn:
            return {
                "name": self.name,
                "flinched": False,
                "applied": False,
                "reason": "target_already_acted",
            }
        if random.random() >= self.FLINCH_CHANCE:
            return {
                "name": self.name,
                "flinched": False,
                "applied": False,
                "reason": "chance_failed",
            }

        target.flinched = True
        return {
            "name": self.name,
            "flinched": True,
            "applied": True,
        }
