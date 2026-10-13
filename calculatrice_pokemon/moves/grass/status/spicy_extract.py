try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SpicyExtract(Moves):
    def __init__(self):
        """Create the Grass-type status move Spicy Extract."""
        super().__init__(
            name="Spicy Extract",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=15,
        )

    def effect(self, user, target):
        """Raise the target's Attack and lower its Defense by two stages."""
        attack_change = self._change_stat(target, "attack", 2)
        defense_change = self._change_stat(target, "defense", -2)
        return {
            "name": self.name,
            "stat_changes": [attack_change, defense_change],
        }

    @staticmethod
    def _change_stat(target, stat, stages):
        current_stage = target.stat_modifiers[stat]
        new_stage = max(-6, min(6, current_stage + stages))
        applied_stages = new_stage - current_stage
        target.stat_modifiers[stat] = new_stage
        return {
            "stat": stat,
            "stages": applied_stages,
            "applied": applied_stages != 0,
            "recipient": "target",
        }
