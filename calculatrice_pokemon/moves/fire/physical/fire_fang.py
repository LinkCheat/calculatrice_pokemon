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


class FireFang(Moves):
    BURN_CHANCE = 0.1
    FLINCH_CHANCE = 0.1

    def __init__(self):
        """Create the Fire-type physical contact move Fire Fang."""
        super().__init__(
            name="Fire Fang",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=65,
            accuracy=95,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Independently try to burn and flinch the target."""
        result = {
            "name": self.name,
            "status": None,
            "applied": False,
            "flinched": False,
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

        if target.has_acted_this_turn:
            result["flinch_reason"] = "target_already_acted"
        elif random.random() < self.FLINCH_CHANCE:
            target.flinched = True
            result["flinched"] = True
        else:
            result["flinch_reason"] = "chance_failed"

        return result
