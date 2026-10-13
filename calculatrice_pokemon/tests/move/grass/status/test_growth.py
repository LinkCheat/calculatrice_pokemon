import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from enums.weather import Weather
from field import Field
from moves import Growth
from pokemon import Pokemon


class GrowthTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = Growth()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Growth")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_raises_attack_and_special_attack_one_stage_without_sun(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(self.user.stat_modifiers["attack"], 1)
        self.assertEqual(self.user.stat_modifiers["sp_atk"], 1)
        self.assertEqual(
            [change["stages"] for change in result["effect"]["stat_changes"]],
            [1, 1],
        )
        self.assertTrue(all(change["applied"] for change in result["effect"]["stat_changes"]))
        self.assertEqual(self.opponent.stat_modifiers["attack"], 0)
        self.assertEqual(self.move.pp, 19)

    def test_raises_both_stats_two_stages_in_sunny_weather(self):
        self.battle_field.weather = Weather.SUNNY

        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.user.stat_modifiers["attack"], 2)
        self.assertEqual(self.user.stat_modifiers["sp_atk"], 2)
        self.assertEqual(
            [change["stages"] for change in result["effect"]["stat_changes"]],
            [2, 2],
        )

    def test_desolate_land_counts_as_sunny_weather(self):
        self.battle_field.weather = Weather.DESOLATE_LAND

        self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.user.stat_modifiers["attack"], 2)
        self.assertEqual(self.user.stat_modifiers["sp_atk"], 2)

    def test_stat_increases_are_capped_independently(self):
        self.user.stat_modifiers["attack"] = 5
        self.user.stat_modifiers["sp_atk"] = 6
        self.battle_field.weather = Weather.SUNNY

        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.user.stat_modifiers["attack"], 6)
        self.assertEqual(self.user.stat_modifiers["sp_atk"], 6)
        self.assertEqual(
            [change["stages"] for change in result["effect"]["stat_changes"]],
            [1, 0],
        )
        self.assertEqual(
            [change["applied"] for change in result["effect"]["stat_changes"]],
            [True, False],
        )

    def test_miss_does_not_raise_stats(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.user.stat_modifiers["attack"], 0)
        self.assertEqual(self.user.stat_modifiers["sp_atk"], 0)
        self.assertEqual(self.move.pp, 19)


if __name__ == "__main__":
    unittest.main()
