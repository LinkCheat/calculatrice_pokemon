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


class PyroBall(Moves):
    BURN_CHANCE = 0.1

    def __init__(self):
        """Create the Fire-type physical move Pyro Ball."""
        super().__init__(
            name="Pyro Ball",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=90,
            max_pp=5,
            bullet=True,
        )

    def effect(self, user, target):
        """Try to burn the target and thaw the user if Pyro Ball is used."""
        user_thawed = user.status_condition is STATUS_CONDITION.FREEZE
        if user_thawed:
            user.status_condition = None

        result = {
            "name": self.name,
            "applied": False,
            "user_thawed": user_thawed,
        }

        result["status"] = None
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
