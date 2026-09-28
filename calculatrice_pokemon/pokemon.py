import csv
import math
from pathlib import Path

from enums.type import Type
from enums.nature import Nature


class Pokemon:
    def __init__(self, name):
        data = self.find_by_name(name)

        self.name = data["name"]
        self.type = data["type"]
        self.base_stats = data["stats"]
        self.weight = data["weight"]

        self.level = 50
        self.stats = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "sp_atk": 0,   
            "sp_def": 0,
            "speed": 0,
        }
        self.nature = Nature.HARDY
        self.ability = None
        self.item = None
        self.moves = []

        self.ivs = {
            "hp": 31,
            "attack": 31,
            "defense": 31,
            "sp_atk": 31,   
            "sp_def": 31,
            "speed": 31,
        }
        self.evs = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "sp_atk": 0,
            "sp_def": 0,
            "speed": 0,
        }
        
        self.status_condition = None
        self.stat_modifiers = {
            "attack": 0,
            "defense": 0,
            "sp_atk": 0,
            "sp_def": 0,
            "speed": 0,
            "accuracy": 0,
            "evasion": 0,
            "critical_hit": 0,
        }
        self.debuffs = [] #pour tout statut stackable hormis burn, freeze, paralysis, poison, sleep et modificateurs de stats
        self.teracristal_type = self.type[0]  # Par défaut, le type de Teracristal est le premier type du Pokémon
        self.teracristal_active = False  # Par défaut, le Teracristal n'est pas actif

        self.calculateStats()


    @staticmethod
    def _parse_type(type_name):
        if type_name is None or not type_name.strip():
            return Type.NONE

        for pokemon_type in Type:
            if pokemon_type.value.lower() == type_name.strip().lower():
                return pokemon_type

        raise ValueError(f"Type inconnu : {type_name}")

    @staticmethod
    def find_by_name(name):
        csv_path = Path(__file__).resolve().parent / "database" / "Pokemon.csv"

        with open(csv_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row["Name"].strip().lower() == name.strip().lower():
                    types = [Pokemon._parse_type(row["Type1"])]
                    if row["Type2"].strip():
                        types.append(Pokemon._parse_type(row["Type2"]))

                    stats = {
                        "total": int(row["Total"]),
                        "hp": int(row["HP"]),
                        "attack": int(row["Attack"]),
                        "defense": int(row["Defense"]),
                        "sp_atk": int(row["Sp. Atk"]),
                        "sp_def": int(row["Sp. Def"]),
                        "speed": int(row["Speed"]),
                    }

                    return {
                        "name": row["Name"],
                        "type": types,
                        "stats": stats,
                        "weight": float(row["Weight"]),
                    }

        raise ValueError(f"Pokémon '{name}' introuvable dans la base de données.")
        
    def _nature_multiplier(self, stat_name):
        nature_multipliers = {
            Nature.HARDY: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.LONELY: {"hp": 1.0, "attack": 1.1, "defense": 0.9, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.BRAVE: {"hp": 1.0, "attack": 1.1, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 0.9},
            Nature.ADAMANT: {"hp": 1.0, "attack": 1.1, "defense": 1.0, "sp_atk": 0.9, "sp_def": 1.0, "speed": 1.0},
            Nature.NAUGHTY: {"hp": 1.0, "attack": 1.1, "defense": 1.0, "sp_atk": 1.0, "sp_def": 0.9, "speed": 1.0},
            Nature.BOLD: {"hp": 1.0, "attack": 0.9, "defense": 1.1, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.DOCILE: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.RELAXED: {"hp": 1.0, "attack": 1.0, "defense": 1.1, "sp_atk": 1.0, "sp_def": 1.0, "speed": 0.9},
            Nature.IMPISH: {"hp": 1.0, "attack": 1.0, "defense": 1.1, "sp_atk": 0.9, "sp_def": 1.0, "speed": 1.0},
            Nature.LAX: {"hp": 1.0, "attack": 1.0, "defense": 1.1, "sp_atk": 1.0, "sp_def": 0.9, "speed": 1.0},
            Nature.TIMID: {"hp": 1.0, "attack": 0.9, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.1},
            Nature.HASTY: {"hp": 1.0, "attack": 1.0, "defense": 0.9, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.1},
            Nature.SERIOUS: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.JOLLY: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 0.9, "sp_def": 1.0, "speed": 1.1},
            Nature.NAIVE: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 0.9, "speed": 1.1},
            Nature.MODEST: {"hp": 1.0, "attack": 0.9, "defense": 1.0, "sp_atk": 1.1, "sp_def": 1.0, "speed": 1.0},
            Nature.MILD: {"hp": 1.0, "attack": 1.0, "defense": 0.9, "sp_atk": 1.1, "sp_def": 1.0, "speed": 1.0},
            Nature.QUIET: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.1, "sp_def": 1.0, "speed": 0.9},
            Nature.BASHFUL: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0},
            Nature.RASH: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.1, "sp_def": 0.9, "speed": 1.0},
            Nature.CALM: {"hp": 1.0, "attack": 0.9, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.1, "speed": 1.0},
            Nature.GENTLE: {"hp": 1.0, "attack": 1.0, "defense": 0.9, "sp_atk": 1.0, "sp_def": 1.1, "speed": 1.0},
            Nature.SASSY: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.1, "speed": 0.9},
            Nature.CAREFUL: {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 0.9, "sp_def": 1.1, "speed": 1.0},
        }
        return nature_multipliers.get(self.nature, {"hp": 1.0, "attack": 1.0, "defense": 1.0, "sp_atk": 1.0, "sp_def": 1.0, "speed": 1.0}).get(stat_name, 1.0)

    def calculateStats(self):
        for stat_name in self.base_stats:
            if stat_name == "total":
                continue

            base = self.base_stats[stat_name]
            iv = self.ivs[stat_name]
            ev = self.evs[stat_name]
            level = self.level

            if stat_name == "hp":
                stat_value = math.floor((2 * base + iv + math.floor(ev / 4)) * level / 100) + level + 10
            else:
                stat_value = math.floor((((2 * base + iv + math.floor(ev / 4)) * level / 100) + 5) * self._nature_multiplier(stat_name))

                statMod = self.stat_modifiers[stat_name]
                if statMod>0:
                    stat_value=stat_value*(1+0.5*statMod)
                else:
                    stat_value=stat_value/(1+0.5*abs(statMod))

            self.stats[stat_name] = int(stat_value)

        return self.stats

    def calculate_stats(self):
        return self.calculateStats()