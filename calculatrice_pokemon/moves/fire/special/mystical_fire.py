try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MysticalFire(Moves):
    def __init__(self):
        """Create the Fire-type special move Mystical Fire."""
        super().__init__(
            name="Mystical Fire",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=75,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower the target's Special Attack by one stage, down to -6."""
        current_stage = target.stat_modifiers["sp_atk"]
        if current_stage <= -6:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "recipient": "target",
            }

        target.stat_modifiers["sp_atk"] = current_stage - 1
        return {
            "name": self.name,
            "stat": "sp_atk",
            "stages": -1,
            "applied": True,
            "recipient": "target",
        }
