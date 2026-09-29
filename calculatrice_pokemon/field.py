import pokemon
from enums.weather import Weather
from enums.terrain import Terrain
import move


class Field:
    def __init__(self):
        self.playerPokemon = None
        self.opponentPokemon = None

        self.playerMove = None
        self.opponentMove = None

        self.weather = None
        self.terrain = None