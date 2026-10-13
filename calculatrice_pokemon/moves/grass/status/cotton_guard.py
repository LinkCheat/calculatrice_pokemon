try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class CottonGuard(Moves):
    DEFENSE_RAISE_STAGES = 3

    def __init__(self):
        """Create the Grass-type status move Cotton Guard."""
        super().__init__(
            name="Cotton Guard",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
        )

    def effect(self, user, target):
        """Raise the user's Defense by up to three stages, capped at +6."""
        defense_stage = user.stat_modifiers["defense"]
        stages_to_raise = min(
            self.DEFENSE_RAISE_STAGES,
            6 - defense_stage,
        )
        if stages_to_raise <= 0:
            return {
                "name": self.name,
                "stat": "defense",
                "stages": 0,
                "applied": False,
                "recipient": "user",
            }

        user.stat_modifiers["defense"] = defense_stage + stages_to_raise
        return {
            "name": self.name,
            "stat": "defense",
            "stages": stages_to_raise,
            "applied": True,
            "recipient": "user",
        }
