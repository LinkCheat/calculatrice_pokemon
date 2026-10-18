import random

try:
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BlazeKick(Moves):
    BURN_CHANCE = 0.1

    def __init__(self):
        """Create the Fire-type physical contact move Blaze Kick."""
        super().__init__(
            name="Blaze Kick",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=85,
            accuracy=90,
            max_pp=10,
            contact=True,
        )

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Raise the critical-hit stage by one for its high critical rate."""
        return 1

    def effect(self, user, target):
        """Try to burn the target with a 10% chance."""
        result = {
            "name": self.name,
            "status": None,
            "applied": False,
        }
        if Type.FIRE in target.type:
            result["reason"] = "type_immune"
        elif target.status_condition is not None:
            result["reason"] = "already_statused"
        elif random.random() < self.BURN_CHANCE:
            target.status_condition = STATUS_CONDITION.BURN
            result["status"] = STATUS_CONDITION.BURN
            result["applied"] = True
        else:
            result["reason"] = "chance_failed"

        return result
