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


class FlareBlitz(Moves):
    BURN_CHANCE = 0.1

    def __init__(self):
        """Create the Fire-type physical contact move Flare Blitz."""
        super().__init__(
            name="Flare Blitz",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Flare Blitz has no effect before damage is calculated."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Apply Flare Blitz's recoil, thawing, and chance to burn."""
        user_thawed = user.status_condition is STATUS_CONDITION.FREEZE
        if user_thawed:
            user.status_condition = None

        recoil = min(damage_dealt // 3, user.current_hp)
        user.current_hp -= recoil

        result = {
            "name": self.name,
            "applied": False,
            "user_thawed": user_thawed,
            "recoil": recoil,
            "status": None,
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
