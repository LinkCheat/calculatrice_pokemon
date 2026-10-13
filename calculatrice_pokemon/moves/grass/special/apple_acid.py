try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class AppleAcid(Moves):
    def __init__(self):
        """Create the Grass-type special move Apple Acid."""
        super().__init__(
            name="Apple Acid",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower the target's Special Defense by one stage, down to -6."""
        sp_def_stage = target.stat_modifiers["sp_def"]
        if sp_def_stage <= -6:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
            }

        target.stat_modifiers["sp_def"] = sp_def_stage - 1
        return {
            "name": self.name,
            "stat": "sp_def",
            "stages": -1,
            "applied": True,
        }
