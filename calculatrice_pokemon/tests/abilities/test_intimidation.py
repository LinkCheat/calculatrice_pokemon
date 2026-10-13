import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from enums.ability import Ability
from field import Field
from pokemon import Pokemon


class IntimidationTests(unittest.TestCase):
    def test_pokemon_defaults_to_no_ability(self):
        self.assertIs(Pokemon("Bulbasaur").ability, Ability.NONE)

    def test_intimidation_lowers_active_opponent_attack_on_battle_initialization(self):
        battle_field = Field()
        intimidator = Pokemon("Arcanine")
        opponent = Pokemon("Eevee")
        reserve = Pokemon("Pikachu")
        intimidator.ability = Ability.INTIMIDATION
        opponent.stat_modifiers["attack"] = 2
        reserve.stat_modifiers["attack"] = 1
        battle_field.add_pokemon(intimidator, "player")
        battle_field.add_pokemon(reserve, "player")
        battle_field.add_pokemon(opponent, "opponent")

        battle_field.initialize_battle()

        self.assertEqual(opponent.stat_modifiers["attack"], 1)
        self.assertEqual(reserve.stat_modifiers["attack"], 1)

    def test_intimidation_activates_when_holder_switches_in_and_respects_stage_limit(self):
        battle_field = Field()
        outgoing_pokemon = Pokemon("Bulbasaur")
        intimidator = Pokemon("Arcanine")
        opponent = Pokemon("Eevee")
        outgoing_pokemon.stat_modifiers["speed"] = 2
        opponent.stat_modifiers["attack"] = -5
        intimidator.ability = Ability.INTIMIDATION
        battle_field.add_pokemon(outgoing_pokemon, "player")
        battle_field.add_pokemon(intimidator, "player")
        battle_field.add_pokemon(opponent, "opponent")

        battle_field.switch_pokemon("player", 1)

        self.assertEqual(opponent.stat_modifiers["attack"], -6)
        self.assertEqual(outgoing_pokemon.stat_modifiers["speed"], 0)

    def test_intimidation_does_not_affect_a_fainted_active_opponent(self):
        battle_field = Field()
        outgoing_pokemon = Pokemon("Bulbasaur")
        intimidator = Pokemon("Arcanine")
        opponent = Pokemon("Eevee")
        intimidator.ability = Ability.INTIMIDATION
        battle_field.add_pokemon(outgoing_pokemon, "player")
        battle_field.add_pokemon(intimidator, "player")
        battle_field.add_pokemon(opponent, "opponent")
        opponent.current_hp = 0

        battle_field.switch_pokemon("player", 1)

        self.assertEqual(opponent.stat_modifiers["attack"], 0)


if __name__ == "__main__":
    unittest.main()
