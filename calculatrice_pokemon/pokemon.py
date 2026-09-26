import csv
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
        self.nature = None
        self.ability = None
        self.item = None
        self.moves = []
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
        
