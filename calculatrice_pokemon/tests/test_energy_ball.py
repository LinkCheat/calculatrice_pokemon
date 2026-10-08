import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import EnergyBall
from pokemon import Pokemon


class EnergyBallTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = EnergyBall()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Energy Ball")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 90)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_hit_has_ten_percent_chance_to_lower_special_defense(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.energy_ball.random.random", return_value=0.099999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -1)
        self.assertEqual(result["effect"]["stat"], "sp_def")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 9)

    def test_chance_failure_does_not_lower_special_defense(self):
        with patch("moves.grass.energy_ball.random.random", return_value=0.1):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertEqual(self.defender.stat_modifiers["sp_def"], 0)

    def test_special_defense_drop_respects_negative_six_limit(self):
        self.defender.stat_modifiers["sp_def"] = -6

        with patch("moves.grass.energy_ball.random.random", return_value=0.0):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "stat_limit")
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -6)

    def test_missed_move_does_not_roll_for_secondary_effect(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.grass.energy_ball.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        roll.assert_not_called()
        self.assertEqual(self.defender.stat_modifiers["sp_def"], 0)


if __name__ == "__main__":
    unittest.main()
