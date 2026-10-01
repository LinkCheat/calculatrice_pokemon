import math
import random

from enums.weather import Weather
from enums.terrain import Terrain
from enums.move_category import MoveCategory
from enums.type import Type
from enums.type_chart import TypeChart


class Field:
    MAX_TEAM_SIZE = 6
    SWITCH_INDEX_OFFSET = 5
    SWITCH_PRIORITY = 6

    def __init__(self):
        self._player_team = []
        self._opponent_team = []
        self._player_active_index = None
        self._opponent_active_index = None
        self.player_action_index = None
        self.opponent_action_index = None

        self.weather = None
        self.terrain = None

    @property
    def player_team(self):
        return tuple(self._player_team)

    @property
    def opponent_team(self):
        return tuple(self._opponent_team)

    @property
    def player_active_pokemon(self):
        return self._get_active_pokemon("player")

    @property
    def opponent_active_pokemon(self):
        return self._get_active_pokemon("opponent")

    def add_pokemon(self, pokemon, side):
        team = self._get_team(side)

        if len(team) >= self.MAX_TEAM_SIZE:
            raise ValueError(f"Une équipe ne peut pas contenir plus de {self.MAX_TEAM_SIZE} Pokémon.")

        team.append(pokemon)
        if len(team) == 1:
            self._set_active_index(side, 0)

    def initialize_battle(self):
        for pokemon in self._player_team + self._opponent_team:
            pokemon.calculateStats()
            pokemon.current_hp = pokemon.max_hp

    def switch_pokemon(self, side, team_index):
        team = self._get_team(side)
        if not isinstance(team_index, int) or not 0 <= team_index < len(team):
            raise ValueError("L'index du Pokémon à sélectionner est invalide.")
        if team_index == self._get_active_index(side):
            raise ValueError("Ce Pokémon est déjà actif.")

        self._set_active_index(side, team_index)
        return team[team_index]

    def _get_team(self, side):
        if side == "player":
            return self._player_team
        if side == "opponent":
            return self._opponent_team
        raise ValueError("side doit être 'player' ou 'opponent'.")

    def _get_active_index(self, side):
        if side == "player":
            return self._player_active_index
        if side == "opponent":
            return self._opponent_active_index
        raise ValueError("side doit être 'player' ou 'opponent'.")

    def _set_active_index(self, side, team_index):
        if side == "player":
            self._player_active_index = team_index
        elif side == "opponent":
            self._opponent_active_index = team_index
        else:
            raise ValueError("side doit être 'player' ou 'opponent'.")

    def _get_active_pokemon(self, side):
        team = self._get_team(side)
        active_index = self._get_active_index(side)
        if active_index is None:
            return None
        return team[active_index]

    def _resolve_action(self, side, action_index):
        team = self._get_team(side)
        active_pokemon = self._get_active_pokemon(side)
        if active_pokemon is None:
            raise ValueError(f"L'équipe {side} ne contient aucun Pokémon.")

        if isinstance(action_index, int) and 0 <= action_index < 4:
            if action_index >= len(active_pokemon.moves):
                raise ValueError(f"Aucune attaque à l'index {action_index} pour le Pokémon actif.")
            selected_move = active_pokemon.moves[action_index]
            if selected_move.pp <= 0:
                raise ValueError(f"{selected_move.name} n'a plus de PP et ne peut pas être sélectionnée.")
            return {
                "side": side,
                "type": "move",
                "pokemon": active_pokemon,
                "move": selected_move,
                "priority": selected_move.priority,
            }

        if isinstance(action_index, int) and action_index > 4:
            team_index = action_index - self.SWITCH_INDEX_OFFSET
            if not 0 <= team_index < len(team):
                raise ValueError(f"L'index de switch {action_index} ne désigne aucun Pokémon de l'équipe.")
            if team_index == self._get_active_index(side):
                raise ValueError("Impossible de switcher vers le Pokémon déjà actif.")
            return {
                "side": side,
                "type": "switch",
                "pokemon": team[team_index],
                "team_index": team_index,
                "move": None,
                "priority": self.SWITCH_PRIORITY,
            }

        raise ValueError("L'index d'action doit être entre 0 et 3 pour une attaque, ou entre 5 et 10 pour un switch.")

    def determine_attack_order(self, player_action_index, opponent_action_index):
        self.player_action_index = player_action_index
        self.opponent_action_index = opponent_action_index

        actions = {
            "player": self._resolve_action("player", player_action_index),
            "opponent": self._resolve_action("opponent", opponent_action_index),
        }
        player_pokemon = self.player_active_pokemon
        opponent_pokemon = self.opponent_active_pokemon
        player_pokemon.calculateStats()
        opponent_pokemon.calculateStats()

        player_priority = actions["player"]["priority"]
        opponent_priority = actions["opponent"]["priority"]

        if player_priority != opponent_priority:
            first_side = "player" if player_priority > opponent_priority else "opponent"
        elif player_pokemon.stats["speed"] != opponent_pokemon.stats["speed"]:
            first_side = "player" if player_pokemon.stats["speed"] > opponent_pokemon.stats["speed"] else "opponent"
        else:
            first_side = random.choice(("player", "opponent"))

        second_side = "opponent" if first_side == "player" else "player"
        return [actions[first_side], actions[second_side]]

    @staticmethod
    def _stage_multiplier(stage):
        if stage >= 0:
            return 1 + stage / 3
        return 1 / (1 + abs(stage) / 3)

    def attack_hits(self, attacker, defender, move):
        if move.accuracy >= 101:
            return True

        accuracy_multiplier = self._stage_multiplier(attacker.stat_modifiers["accuracy"])
        evasion_multiplier = self._stage_multiplier(defender.stat_modifiers["evasion"])
        hit_chance = move.accuracy * accuracy_multiplier / evasion_multiplier
        if hit_chance >= 100:
            return True
        return random.random() * 100 < max(0, hit_chance)

    def calculate_move_effectiveness(self, move, defender):
        effectiveness = 1.0
        for defending_type in defender.type:
            effectiveness *= self.calculate_type_effectiveness(move.type, defending_type)
        return effectiveness

    def is_immune_to_move(self, move, defender):
        return self.calculate_move_effectiveness(move, defender) == 0

    def calculate_stab_multiplier(self, attacker, move):
        return 1.5 if move.type in attacker.type else 1.0

    def calculate_damage_modifiers(self, attacker, defender, move):
        return (
            self.calculate_move_effectiveness(move, defender)
            * self.calculate_stab_multiplier(attacker, move)
        )

    def calculate_damage(self, attacker, defender, move):
        if move.category is MoveCategory.STATUS:
            return 0

        if move.category is MoveCategory.PHYSICAL:
            attack_stat = attacker.stats["attack"]
            defense_stat = defender.stats["defense"]
        elif move.category is MoveCategory.SPECIAL:
            attack_stat = attacker.stats["sp_atk"]
            defense_stat = defender.stats["sp_def"]
        else:
            raise ValueError(f"Catégorie d'attaque inconnue : {move.category}")

        power = move.get_power(attacker, defender)
        base_damage = math.floor(attacker.level * 0.4 + 2)
        base_damage = math.floor(base_damage * attack_stat * power / defense_stat)
        base_damage = math.floor(base_damage / 50) + 2

        modifiers = self.calculate_damage_modifiers(attacker, defender, move)
        standard_damage = math.floor(base_damage * modifiers)
        return move.calculate_damage(attacker, defender, standard_damage)

    def resolve_move(self, side, move):
        attacker = self._get_active_pokemon(side)
        opponent_side = "opponent" if side == "player" else "player"
        defender = self._get_active_pokemon(opponent_side)
        if attacker is None or defender is None:
            raise ValueError("Chaque camp doit avoir un Pokémon actif pour résoudre une attaque.")
        if move.pp <= 0:
            raise ValueError(f"{move.name} n'a plus de PP et ne peut pas être utilisée.")

        move.consume_pp()
        if not self.attack_hits(attacker, defender, move):
            return {"hit": False, "immune": False, "damage": 0, "effect": None}

        effectiveness = self.calculate_move_effectiveness(move, defender)
        if effectiveness == 0:
            return {"hit": True, "immune": True, "damage": 0, "effect": None}

        attacker.calculateStats()
        defender.calculateStats()
        damage = self.calculate_damage(attacker, defender, move)
        defender.current_hp = max(0, defender.current_hp - damage)
        effect = move.effect(attacker, defender)
        return {
            "hit": True,
            "immune": False,
            "damage": damage,
            "effect": effect,
        }

    @staticmethod
    def calculate_type_effectiveness(attack_type: Type, defending_type: Type) -> float:
        if attack_type is Type.NONE:
            raise ValueError("Le type d'une attaque ne peut pas être Type.NONE.")
        if not isinstance(defending_type, Type):
            raise ValueError("defending_type doit être une valeur de Type.")
        if defending_type is Type.NONE:
            return 1.0
        return TypeChart[attack_type.name].value.get(defending_type, 1.0)
