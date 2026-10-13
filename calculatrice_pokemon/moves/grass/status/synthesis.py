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


class Synthesis(Moves):
    SUNNY_WEATHER = (Weather.SUNNY, Weather.DESOLATE_LAND)

    def __init__(self):
        """Create the Grass-type status move Synthesis."""
        super().__init__(
            name="Synthesis",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=5,
        )

    def effect(self, user, target):
        """Restore HP according to the current weather."""
        return self._restore_hp(user, 1, 2)

    def apply_effect_with_field(self, user, target, damage_dealt, field):
        if field.weather in self.SUNNY_WEATHER:
            return self._restore_hp(user, 2, 3)
        if field.weather is not None:
            return self._restore_hp(user, 1, 4)
        return self._restore_hp(user, 1, 2)

    def _restore_hp(self, user, numerator, denominator):
        healing = min(
            user.max_hp * numerator // denominator,
            user.max_hp - user.current_hp,
        )
        user.current_hp += healing
        return {
            "condition": "synthesis",
            "healed": healing,
        }
