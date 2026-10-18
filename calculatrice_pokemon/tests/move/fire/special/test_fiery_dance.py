import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import FieryDance
from pokemon import Pokemon


class FieryDanceTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Volcarona")
        self.defender = Pokemon("Eevee")
        self.move = FieryDance()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Fiery Dance")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_hit_can_raise_user_special_attack(self):
        with (
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch(
                "moves.fire.special.fiery_dance.random.random",
                return_value=0.499999,
            ),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["stages"], 1)
        self.assertEqual(result["effect"]["recipient"], "user")
        self.assertEqual(self.move.pp, 9)

    def test_chance_failure_does_not_raise_special_attack(self):
        with patch(
            "moves.fire.special.fiery_dance.random.random",
            return_value=0.5,
        ):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 0)

    def test_boost_respects_maximum_stage(self):
        self.attacker.stat_modifiers["sp_atk"] = 6

        with patch(
            "moves.fire.special.fiery_dance.random.random",
            return_value=0.1,
        ):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "stat_limit")
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 6)

    def test_miss_does_not_attempt_boost(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.fire.special.fiery_dance.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 0)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()
