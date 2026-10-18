try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FireLash(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Fire Lash."""
        super().__init__(
            name="Fire Lash",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=80,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Lower the target's Defense by one stage, down to the stage limit."""
        defense_stage = target.stat_modifiers["defense"]
        if defense_stage <= -6:
            return {
                "name": self.name,
                "stat": "defense",
                "stages": 0,
                "applied": False,
            }

        target.stat_modifiers["defense"] = defense_stage - 1
        return {
            "name": self.name,
            "stat": "defense",
            "stages": -1,
            "applied": True,
        }
