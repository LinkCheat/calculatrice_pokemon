import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import LeafStorm
from pokemon import Pokemon


class LeafStormTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = LeafStorm()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Leaf Storm")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 130)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_lowers_user_special_attack_by_two_stages(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], -2)
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], 0)
        self.assertEqual(result["effect"]["stat"], "sp_atk")
        self.assertEqual(result["effect"]["stages"], -2)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["recipient"], "user")
        self.assertEqual(self.move.pp, 4)

    def test_special_attack_drop_respects_negative_six_limit(self):
        self.attacker.stat_modifiers["sp_atk"] = -5

        effect = self.move.effect(self.attacker, self.defender)

        self.assertTrue(effect["applied"])
        self.assertEqual(effect["stages"], -1)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], -6)

    def test_special_attack_cannot_be_lowered_below_negative_six(self):
        self.attacker.stat_modifiers["sp_atk"] = -6

        effect = self.move.effect(self.attacker, self.defender)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["stages"], 0)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], -6)

    def test_miss_does_not_lower_user_special_attack(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 0)
        self.assertEqual(self.move.pp, 4)


if __name__ == "__main__":
    unittest.main()
