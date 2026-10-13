import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import LeafTornado
from pokemon import Pokemon


class LeafTornadoTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = LeafTornado()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Leaf Tornado")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 65)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_hit_lowers_target_accuracy_with_fifty_percent_chance(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.special.leaf_tornado.random.random", return_value=0.499999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["accuracy"], -1)
        self.assertEqual(result["effect"]["stat"], "accuracy")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 9)

    def test_chance_failure_does_not_lower_accuracy(self):
        with patch("moves.grass.special.leaf_tornado.random.random", return_value=0.5):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertEqual(self.defender.stat_modifiers["accuracy"], 0)

    def test_accuracy_drop_respects_negative_six_limit(self):
        self.defender.stat_modifiers["accuracy"] = -6

        with patch("moves.grass.special.leaf_tornado.random.random", return_value=0.0):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "stat_limit")
        self.assertEqual(self.defender.stat_modifiers["accuracy"], -6)

    def test_miss_does_not_roll_for_accuracy_drop(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.grass.special.leaf_tornado.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        roll.assert_not_called()
        self.assertEqual(self.defender.stat_modifiers["accuracy"], 0)


if __name__ == "__main__":
    unittest.main()
