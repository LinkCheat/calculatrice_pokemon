try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FlameCharge(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Flame Charge."""
        super().__init__(
            name="Flame Charge",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=50,
            accuracy=100,
            max_pp=20,
            contact=True,
        )

    def effect(self, user, target):
        """Raise the user's Speed by one stage, up to the stage limit."""
        speed_stage = user.stat_modifiers["speed"]
        if speed_stage >= 6:
            return {
                "name": self.name,
                "stat": "speed",
                "stages": 0,
                "applied": False,
                "recipient": "user",
            }

        user.stat_modifiers["speed"] = speed_stage + 1
        return {
            "name": self.name,
            "stat": "speed",
            "stages": 1,
            "applied": True,
            "recipient": "user",
        }
