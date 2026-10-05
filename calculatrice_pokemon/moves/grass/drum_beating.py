try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class DrumBeating(Moves):
    def __init__(self):
        """Create the Grass-type physical move Drum Beating."""
        super().__init__(
            name="Drum Beating",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=80,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower the target's Speed by one stage, down to the stage limit."""
        speed_stage = target.stat_modifiers["speed"]
        if speed_stage <= -6:
            return {
                "name": self.name,
                "stat": "speed",
                "stages": 0,
                "applied": False,
            }

        target.stat_modifiers["speed"] = speed_stage - 1
        return {
            "name": self.name,
            "stat": "speed",
            "stages": -1,
            "applied": True,
        }
