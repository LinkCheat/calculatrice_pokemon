import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class LeafTornado(Moves):
    ACCURACY_DROP_CHANCE = 0.5

    def __init__(self):
        """Create the Grass-type special move Leaf Tornado."""
        super().__init__(
            name="Leaf Tornado",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=65,
            accuracy=90,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower the target's Accuracy by one stage with 50% chance."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "stat": "accuracy",
                "stages": 0,
                "applied": False,
                "reason": "target_fainted",
            }
        if random.random() >= self.ACCURACY_DROP_CHANCE:
            return {
                "name": self.name,
                "stat": "accuracy",
                "stages": 0,
                "applied": False,
                "reason": "chance_failed",
            }

        accuracy_stage = target.stat_modifiers["accuracy"]
        if accuracy_stage <= -6:
            return {
                "name": self.name,
                "stat": "accuracy",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
            }

        target.stat_modifiers["accuracy"] = accuracy_stage - 1
        return {
            "name": self.name,
            "stat": "accuracy",
            "stages": -1,
            "applied": True,
        }
