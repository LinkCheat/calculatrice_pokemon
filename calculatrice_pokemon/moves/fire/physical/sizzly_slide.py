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


class SizzlySlide(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Sizzly Slide."""
        super().__init__(
            name="Sizzly Slide",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=60,
            accuracy=100,
            max_pp=20,
            contact=True,
        )

    def effect(self, user, target):
        """Burn the target unless its type or current status prevents it."""
        result = {
            "name": self.name,
            "status": None,
            "applied": False,
        }
        if Type.FIRE in target.type:
            result["reason"] = "type_immune"
        elif target.status_condition is not None:
            result["reason"] = "already_statused"
        else:
            target.status_condition = STATUS_CONDITION.BURN
            result["status"] = STATUS_CONDITION.BURN
            result["applied"] = True

        return result
