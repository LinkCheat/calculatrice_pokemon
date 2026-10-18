import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import MysticalFire
from pokemon import Pokemon


class MysticalFireTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = MysticalFire()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Mystical Fire")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 75)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_hit_lowers_target_special_attack(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], -1)
        self.assertEqual(result["effect"]["stat"], "sp_atk")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["recipient"], "target")
        self.assertEqual(self.move.pp, 9)

    def test_special_attack_drop_is_guaranteed(self):
        self.defender.stat_modifiers["sp_atk"] = -5

        result = self.move.effect(self.attacker, self.defender)

        self.assertTrue(result["applied"])
        self.assertEqual(result["stages"], -1)
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], -6)

    def test_special_attack_drop_respects_minimum_stage(self):
        self.defender.stat_modifiers["sp_atk"] = -6

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["stages"], 0)
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], -6)

    def test_miss_does_not_lower_target_special_attack(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], 0)


if __name__ == "__main__":
    unittest.main()
