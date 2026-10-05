try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class TropKick(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Trop Kick."""
        super().__init__(
            name="Trop Kick",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=70,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Lower the target's Attack by one stage, down to the stage limit."""
        attack_stage = target.stat_modifiers["attack"]
        if attack_stage <= -6:
            return {
                "name": self.name,
                "stat": "attack",
                "stages": 0,
                "applied": False,
            }

        target.stat_modifiers["attack"] = attack_stage - 1
        return {
            "name": self.name,
            "stat": "attack",
            "stages": -1,
            "applied": True,
        }
