import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import CottonGuard
from pokemon import Pokemon


class CottonGuardTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = CottonGuard()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Cotton Guard")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_use_raises_user_defense_by_three_stages(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(self.user.stat_modifiers["defense"], 3)
        self.assertEqual(self.opponent.stat_modifiers["defense"], 0)
        self.assertEqual(result["effect"]["stat"], "defense")
        self.assertEqual(result["effect"]["stages"], 3)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["recipient"], "user")
        self.assertEqual(self.move.pp, 9)

    def test_raise_is_limited_by_positive_six_stage_cap(self):
        self.user.stat_modifiers["defense"] = 5

        effect = self.move.effect(self.user, self.opponent)

        self.assertEqual(self.user.stat_modifiers["defense"], 6)
        self.assertEqual(effect["stages"], 1)
        self.assertTrue(effect["applied"])

    def test_defense_cannot_be_raised_past_positive_six(self):
        self.user.stat_modifiers["defense"] = 6

        effect = self.move.effect(self.user, self.opponent)

        self.assertEqual(self.user.stat_modifiers["defense"], 6)
        self.assertEqual(effect["stages"], 0)
        self.assertFalse(effect["applied"])

    def test_move_does_not_raise_defense_when_accuracy_check_fails(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.user.stat_modifiers["defense"], 0)
        self.assertEqual(self.move.pp, 9)


if __name__ == "__main__":
    unittest.main()
