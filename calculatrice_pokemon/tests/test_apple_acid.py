import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import AppleAcid
from pokemon import Pokemon


class AppleAcidTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = AppleAcid()

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Apple Acid")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_hit_lowers_special_defense_and_consumes_pp(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -1)
        self.assertEqual(result["effect"]["stat"], "sp_def")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 9)

    def test_special_defense_drop_is_guaranteed(self):
        self.defender.stat_modifiers["sp_def"] = -5

        effect = self.move.effect(self.attacker, self.defender)

        self.assertTrue(effect["applied"])
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -6)

    def test_special_defense_drop_respects_minimum_stage(self):
        self.defender.stat_modifiers["sp_def"] = -6

        effect = self.move.effect(self.attacker, self.defender)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["stages"], 0)
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -6)

    def test_special_category_uses_special_attack_and_special_defense(self):
        with (
            patch.object(self.battle_field, "calculate_damage_modifiers", return_value=1.0),
            patch.object(self.attacker, "calculateStats"),
            patch.object(self.defender, "calculateStats"),
        ):
            special_damage = self.battle_field.calculate_damage(
                self.attacker,
                self.defender,
                self.move,
            )

        self.assertGreater(special_damage, 0)


if __name__ == "__main__":
    unittest.main()
