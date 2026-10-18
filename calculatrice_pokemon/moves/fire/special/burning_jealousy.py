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


class BurningJealousy(Moves):
    def __init__(self):
        """Create the Fire-type special move Burning Jealousy."""
        super().__init__(
            name="Burning Jealousy",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=70,
            accuracy=100,
            max_pp=5,
        )

    def effect(self, user, target):
        """Burn the target if any of its stats were raised during this turn."""
        result = {
            "name": self.name,
            "status": None,
            "applied": False,
        }
        if not target.stat_boosted_this_turn:
            result["reason"] = "no_stat_boost"
        elif Type.FIRE in target.type:
            result["reason"] = "type_immune"
        elif target.status_condition is not None:
            result["reason"] = "already_statused"
        else:
            target.status_condition = STATUS_CONDITION.BURN
            result["status"] = STATUS_CONDITION.BURN
            result["applied"] = True

        return result
