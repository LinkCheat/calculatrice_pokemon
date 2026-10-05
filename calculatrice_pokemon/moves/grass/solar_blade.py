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


class SolarBlade(Moves):
    def __init__(self):
        """Create the Grass-type physical move Solar Blade."""
        super().__init__(
            name="Solar Blade",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=125,
            accuracy=100,
            max_pp=10,
        )

    def requires_charge(self, field):
        """Skip the charging turn in sunny or extremely sunny weather."""
        return field.weather not in (Weather.SUNNY, Weather.DESOLATE_LAND)

    def effect(self, user, target):
        """Solar Blade has no secondary effect."""
        return None
