try:
    from enums.move_category import MoveCategory
    from enums.weather import Weather
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.weather import Weather
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SolarBeam(Moves):
    REDUCED_POWER_WEATHER = (Weather.RAINY, Weather.SANDSTORM, Weather.SNOW)

    def __init__(self):
        """Create the Grass-type special move Solar Beam."""
        super().__init__(
            name="Solar Beam",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=120,
            accuracy=100,
            max_pp=10,
        )

    def requires_charge(self, field):
        """Skip the charging turn in sunny or extremely sunny weather."""
        return field.weather not in (Weather.SUNNY, Weather.DESOLATE_LAND)

    def get_power(self, user, target, field=None):
        """Halve Solar Beam's power in rain, sandstorm, or snow."""
        if field is not None and field.weather in self.REDUCED_POWER_WEATHER:
            return self.power // 2
        return self.power

    def effect(self, user, target):
        """Solar Beam has no secondary effect."""
        return None
