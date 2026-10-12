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


class MatchaGotcha(Moves):
    BURN_CHANCE = 0.2

    def __init__(self):
        """Create the Grass-type special move Matcha Gotcha."""
        super().__init__(
            name="Matcha Gotcha",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=80,
            accuracy=90,
            max_pp=15,
        )

    def effect(self, user, target):
        """Matcha Gotcha's drain and burn use the actual damage context."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Heal half the actual damage and try to burn the target."""
        healing = min(damage_dealt // 2, user.max_hp - user.current_hp)
        user.current_hp += healing

        if target.current_hp <= 0:
            burn_effect = {
                "status": None,
                "applied": False,
                "reason": "target_fainted",
            }
        elif Type.FIRE in target.type:
            burn_effect = {
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        elif target.status_condition is not None:
            burn_effect = {
                "status": None,
                "applied": False,
                "reason": "already_statused",
            }
        elif random.random() < self.BURN_CHANCE:
            target.status_condition = STATUS_CONDITION.BURN
            burn_effect = {
                "status": STATUS_CONDITION.BURN,
                "applied": True,
            }
        else:
            burn_effect = {
                "status": None,
                "applied": False,
                "reason": "chance_failed",
            }

        return {
            "name": self.name,
            "healed": healing,
            **burn_effect,
        }
