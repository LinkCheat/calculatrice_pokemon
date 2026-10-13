import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SeedFlare(Moves):
    SP_DEF_DROP_CHANCE = 0.4
    SP_DEF_DROP_STAGES = 2

    def __init__(self):
        """Create the Grass-type special move Seed Flare."""
        super().__init__(
            name="Seed Flare",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=120,
            accuracy=85,
            max_pp=5,
        )

    def effect(self, _user, target):
        """Lower the target's Special Defense by up to two stages, with 40% chance."""
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
        stages_to_lower = min(self.SP_DEF_DROP_STAGES, sp_def_stage + 6)
        if stages_to_lower <= 0:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
            }

        target.stat_modifiers["sp_def"] = sp_def_stage - stages_to_lower
        return {
            "name": self.name,
            "stat": "sp_def",
            "stages": -stages_to_lower,
            "applied": True,
        }
