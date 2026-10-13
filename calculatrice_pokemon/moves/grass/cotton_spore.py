try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class CottonSpore(Moves):
    def __init__(self):
        """Create the Grass-type status move Cotton Spore."""
        super().__init__(
            name="Cotton Spore",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=100,
            max_pp=40,
        )

    def effect(self, user, target):
        """Lower the target's Speed by two stages, respecting the stage limit."""
        speed_stage = target.stat_modifiers["speed"]
        new_stage = max(-6, speed_stage - 2)
        stages_applied = new_stage - speed_stage
        target.stat_modifiers["speed"] = new_stage
        return {
            "name": self.name,
            "stat": "speed",
            "stages": stages_applied,
            "applied": stages_applied != 0,
        }
