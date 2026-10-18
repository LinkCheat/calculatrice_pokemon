import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import FireLash
from pokemon import Pokemon


class FireLashTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Heatmor")
        self.defender = Pokemon("Eevee")
        self.move = FireLash()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Fire Lash")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_successful_hit_lowers_target_defense_and_consumes_pp(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["defense"], -1)
        self.assertEqual(result["effect"]["stat"], "defense")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 14)

    def test_defense_drop_respects_minimum_stage(self):
        self.defender.stat_modifiers["defense"] = -6

        effect = self.move.effect(self.attacker, self.defender)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["stages"], 0)
        self.assertEqual(self.defender.stat_modifiers["defense"], -6)

    def test_miss_does_not_lower_target_defense(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.defender.stat_modifiers["defense"], 0)


if __name__ == "__main__":
    unittest.main()
