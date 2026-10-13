import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import CottonSpore
from pokemon import Pokemon


class CottonSporeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = CottonSpore()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Cotton Spore")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 40)
        self.assertFalse(self.move.contact)

    def test_successful_hit_lowers_speed_by_two_stages(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(self.target.stat_modifiers["speed"], -2)
        self.assertEqual(result["effect"]["stat"], "speed")
        self.assertEqual(result["effect"]["stages"], -2)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 39)

    def test_speed_drop_respects_minimum_stage(self):
        self.target.stat_modifiers["speed"] = -5

        effect = self.move.effect(self.user, self.target)

        self.assertEqual(self.target.stat_modifiers["speed"], -6)
        self.assertEqual(effect["stages"], -1)
        self.assertTrue(effect["applied"])

    def test_already_minimum_speed_stage_is_unchanged(self):
        self.target.stat_modifiers["speed"] = -6

        effect = self.move.effect(self.user, self.target)

        self.assertEqual(self.target.stat_modifiers["speed"], -6)
        self.assertEqual(effect["stages"], 0)
        self.assertFalse(effect["applied"])

    def test_miss_does_not_change_target_speed(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.target.stat_modifiers["speed"], 0)
        self.assertEqual(self.move.pp, 39)


if __name__ == "__main__":
    unittest.main()
