import pokemon
from enums.weather import Weather
from enums.terrain import Terrain


class Field:
    def __init__(self):
        self.playerPokemon = None
        self.opponentPokemon = None
        self.weather = None
        self.terrain = None