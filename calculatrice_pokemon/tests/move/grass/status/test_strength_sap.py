import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import StrengthSap
from pokemon import Pokemon


class StrengthSapTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = StrengthSap()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Strength Sap")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)
        self.assertTrue(self.move.IGNORE_TARGET_ITEM_AND_ABILITY)

    def test_lowers_attack_and_heals_using_the_pre_drop_effective_attack(self):
        self.target.stat_modifiers["attack"] = -1
        self.target.calculateStats()
        attack_before_drop = self.target.stats["attack"]
        self.user.current_hp = 0

        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertFalse(result.get("failed", False))
        self.assertEqual(self.target.stat_modifiers["attack"], -2)
        self.assertEqual(self.user.current_hp, attack_before_drop)
        self.assertEqual(result["effect"]["healed"], attack_before_drop)
        self.assertEqual(result["effect"]["stat_changes"][0]["stages"], -1)
        self.assertTrue(result["effect"]["stat_changes"][0]["applied"])
        self.assertEqual(self.move.pp, 9)

    def test_attack_drop_occurs_when_user_is_at_full_health(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(self.target.stat_modifiers["attack"], -1)
        self.assertEqual(result["effect"]["healed"], 0)

    def test_healing_is_capped_at_missing_hp_but_attack_still_drops(self):
        self.user.current_hp = self.user.max_hp - 1

        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(result["effect"]["healed"], 1)
        self.assertEqual(self.target.stat_modifiers["attack"], -1)

    def test_fails_without_healing_or_stat_change_at_minus_six_attack(self):
        self.target.stat_modifiers["attack"] = -6
        self.user.current_hp -= 20

        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertTrue(result["failed"])
        self.assertTrue(result["effect"]["failed"])
        self.assertEqual(result["effect"]["healed"], 0)
        self.assertEqual(self.target.stat_modifiers["attack"], -6)
        self.assertEqual(self.user.current_hp, self.user.max_hp - 20)
        self.assertEqual(self.move.pp, 9)

    def test_minimum_reached_by_drop_still_heals_using_attack_before_drop(self):
        self.target.stat_modifiers["attack"] = -5
        self.target.calculateStats()
        attack_before_drop = self.target.stats["attack"]
        self.user.current_hp = self.user.max_hp - 1

        result = self.move.effect(self.user, self.target)

        self.assertEqual(self.target.stat_modifiers["attack"], -6)
        self.assertEqual(result["stat_changes"][0]["stages"], -1)
        self.assertEqual(result["healed"], 1)
        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertGreater(attack_before_drop, 0)

    def test_miss_does_not_heal_or_lower_attack(self):
        self.user.current_hp -= 20
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.user.current_hp, self.user.max_hp - 20)
        self.assertEqual(self.target.stat_modifiers["attack"], 0)
        self.assertEqual(self.move.pp, 9)


if __name__ == "__main__":
    unittest.main()
