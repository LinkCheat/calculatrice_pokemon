try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class TorchSong(Moves):
    def __init__(self):
        """Create the Fire-type special sound move Torch Song."""
        super().__init__(
            name="Torch Song",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=100,
            max_pp=10,
            sound=True,
        )

    def effect(self, user, target):
        """Raise the user's Special Attack by one stage."""
        current_stage = user.stat_modifiers["sp_atk"]
        if current_stage >= 6:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
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
