import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import SpicyExtract
from pokemon import Pokemon


class SpicyExtractTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = SpicyExtract()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Spicy Extract")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_raises_target_attack_and_lowers_target_defense_by_two_stages(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(self.target.stat_modifiers["attack"], 2)
        self.assertEqual(self.target.stat_modifiers["defense"], -2)
        self.assertEqual(
            [change["stages"] for change in result["effect"]["stat_changes"]],
            [2, -2],
        )
        self.assertTrue(all(change["applied"] for change in result["effect"]["stat_changes"]))
        self.assertTrue(
            all(change["recipient"] == "target" for change in result["effect"]["stat_changes"])
        )
        self.assertEqual(self.user.stat_modifiers["attack"], 0)
        self.assertEqual(self.move.pp, 14)

    def test_both_stat_changes_respect_stage_limits_independently(self):
        self.target.stat_modifiers["attack"] = 5
        self.target.stat_modifiers["defense"] = -5

        result = self.move.effect(self.user, self.target)

        self.assertEqual(self.target.stat_modifiers["attack"], 6)
        self.assertEqual(self.target.stat_modifiers["defense"], -6)
        self.assertEqual(
            [change["stages"] for change in result["stat_changes"]],
            [1, -1],
        )

    def test_already_maxed_stats_report_no_change(self):
        self.target.stat_modifiers["attack"] = 6
        self.target.stat_modifiers["defense"] = -6

        result = self.move.effect(self.user, self.target)

        self.assertEqual(
            [change["stages"] for change in result["stat_changes"]],
            [0, 0],
        )
        self.assertFalse(any(change["applied"] for change in result["stat_changes"]))

    def test_miss_does_not_change_target_stats(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.target.stat_modifiers["attack"], 0)
        self.assertEqual(self.target.stat_modifiers["defense"], 0)
        self.assertEqual(self.move.pp, 14)


if __name__ == "__main__":
    unittest.main()
