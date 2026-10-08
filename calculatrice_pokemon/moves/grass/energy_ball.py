import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class EnergyBall(Moves):
    SP_DEF_DROP_CHANCE = 0.1

    def __init__(self):
        """Create the Grass-type special move Energy Ball."""
        super().__init__(
            name="Energy Ball",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=90,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower the target's Special Defense by one stage with 10% chance."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
                "reason": "target_fainted",
            }
        if random.random() >= self.SP_DEF_DROP_CHANCE:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
                "reason": "chance_failed",
            }

        sp_def_stage = target.stat_modifiers["sp_def"]
        if sp_def_stage <= -6:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
            }

        target.stat_modifiers["sp_def"] = sp_def_stage - 1
        return {
            "name": self.name,
            "stat": "sp_def",
            "stages": -1,
            "applied": True,
        }
