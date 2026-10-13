try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from enums.weather import Weather
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.enums.weather import Weather
    from calculatrice_pokemon.moves.move import Moves


class Growth(Moves):
    def __init__(self):
        """Create the Grass-type status move Growth."""
        super().__init__(
            name="Growth",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=20,
        )

    def effect(self, user, target):
        """Raise Attack and Special Attack by one or two stages."""
        return self._apply_growth(user, 1)

    def apply_effect_with_field(self, user, target, damage_dealt, field):
        stages = 2 if field.weather in (Weather.SUNNY, Weather.DESOLATE_LAND) else 1
        return self._apply_growth(user, stages)

    def _apply_growth(self, user, stages):
        changes = []
        for stat in ("attack", "sp_atk"):
            current_stage = user.stat_modifiers[stat]
            stages_applied = min(stages, 6 - current_stage)
            user.stat_modifiers[stat] = current_stage + stages_applied
            changes.append({
                "stat": stat,
                "stages": stages_applied,
                "applied": stages_applied > 0,
                "recipient": "user",
            })

        return {
            "name": self.name,
            "stat_changes": changes,
        }
