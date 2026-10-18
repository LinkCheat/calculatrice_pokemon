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


class SunnyDay(Moves):
    DURATION = 5

    def __init__(self):
        """Create the Fire-type status move Sunny Day."""
        super().__init__(
            name="Sunny Day",
            move_type=Type.FIRE,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=5,
        )

    def effect(self, user, target):
        """Sunny Day changes weather through the field effect hook."""
        return None

    def applies_field_effect(self):
        return True

    def apply_field_effect(self, user, field):
        """Set or refresh sunny weather for five turns."""
        field.weather = Weather.SUNNY
        field.weather_turns_remaining = self.DURATION
        return {
            "condition": "sunny_day",
            "applied": True,
            "turns": self.DURATION,
        }
