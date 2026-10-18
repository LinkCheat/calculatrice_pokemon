try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Overheat(Moves):
    SP_ATK_DROP_STAGES = 2

    def __init__(self):
        """Create the Fire-type special move Overheat."""
        super().__init__(
            name="Overheat",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=130,
            accuracy=90,
            max_pp=5,
        )

    def effect(self, user, target):
        """Lower the user's Special Attack by two stages, down to -6."""
        sp_atk_stage = user.stat_modifiers["sp_atk"]
        stages_to_lower = min(self.SP_ATK_DROP_STAGES, sp_atk_stage + 6)
        if stages_to_lower <= 0:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "recipient": "user",
            }

        user.stat_modifiers["sp_atk"] = sp_atk_stage - stages_to_lower
        return {
            "name": self.name,
            "stat": "sp_atk",
            "stages": -stages_to_lower,
            "applied": True,
            "recipient": "user",
        }
