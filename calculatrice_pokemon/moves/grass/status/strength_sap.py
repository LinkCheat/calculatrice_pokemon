try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class StrengthSap(Moves):
    IGNORE_TARGET_ITEM_AND_ABILITY = True

    def __init__(self):
        """Create the Grass-type status move Strength Sap."""
        super().__init__(
            name="Strength Sap",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Lower target Attack, then heal using its prior effective value."""
        target.calculateStats()
        attack_before_drop = target.stats["attack"]
        attack_stage = target.stat_modifiers["attack"]
        if attack_stage <= -6:
            return {
                "condition": "strength_sap",
                "failed": True,
                "healed": 0,
                "stat_changes": [{
                    "stat": "attack",
                    "stages": 0,
                    "applied": False,
                    "recipient": "target",
                }],
            }

        target.stat_modifiers["attack"] = attack_stage - 1
        target.calculateStats()
        healing = min(attack_before_drop, user.max_hp - user.current_hp)
        user.current_hp += healing
        return {
            "condition": "strength_sap",
            "failed": False,
            "healed": healing,
            "stat_changes": [{
                "stat": "attack",
                "stages": -1,
                "applied": True,
                "recipient": "target",
            }],
        }
