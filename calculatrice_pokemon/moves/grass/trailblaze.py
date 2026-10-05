try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Trailblaze(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Trailblaze."""
        super().__init__(
            name="Trailblaze",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=50,
            accuracy=100,
            max_pp=20,
            contact=True,
        )

    def effect(self, user, target):
        """Raise the user's Attack by one stage, up to the stage limit."""
        attack_stage = user.stat_modifiers["attack"]
        if attack_stage >= 6:
            return {
                "name": self.name,
                "stat": "attack",
                "stages": 0,
                "applied": False,
                "recipient": "user",
            }

        user.stat_modifiers["attack"] = attack_stage + 1
        return {
            "name": self.name,
            "stat": "attack",
            "stages": 1,
            "applied": True,
            "recipient": "user",
        }
