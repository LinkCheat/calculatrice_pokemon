import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FieryDance(Moves):
    SP_ATK_BOOST_CHANCE = 0.5

    def __init__(self):
        """Create the Fire-type special move Fiery Dance."""
        super().__init__(
            name="Fiery Dance",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Raise the user's Special Attack by one stage with 50% chance."""
        if random.random() >= self.SP_ATK_BOOST_CHANCE:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "reason": "chance_failed",
                "recipient": "user",
            }

        current_stage = user.stat_modifiers["sp_atk"]
        if current_stage >= 6:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
                "recipient": "user",
            }

        user.stat_modifiers["sp_atk"] = current_stage + 1
        return {
            "name": self.name,
            "stat": "sp_atk",
            "stages": 1,
            "applied": True,
            "recipient": "user",
        }
