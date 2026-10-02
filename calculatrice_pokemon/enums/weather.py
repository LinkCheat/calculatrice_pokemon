from enum import Enum


class Weather(Enum):
    NONE = ""
    SUNNY = "Sunny"
    RAINY = "Rainy"
    SANDSTORM = "Sandstorm"
    SNOW = "Snow"
    DESOLATE_LAND = "Desolate Land"
    PRIMORDIAL_SEA = "Primordial Sea"
    DELTA_STREAM = "Delta Stream"

    def __repr__(self):
        """Display the weather's human-readable name."""
        return self.value