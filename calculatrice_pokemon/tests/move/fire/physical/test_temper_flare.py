import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import TemperFlare
from pokemon import Pokemon


class TemperFlareTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Flareon")
        self.defender = Pokemon("Eevee")
        self.move = TemperFlare()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Temper Flare")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 75)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertTrue(self.move.contact)

    def test_power_doubles_after_a_failed_move(self):
        self.attacker.last_move_failed = True

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender),
            self.move.power * 2,
        )

    def test_power_is_normal_when_previous_move_succeeded(self):
        self.attacker.last_move_failed = False

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender),
            self.move.power,
        )

    def test_missed_move_sets_failure_flag_for_next_move(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertTrue(self.attacker.last_move_failed)

    def test_successful_move_clears_previous_failure_flag(self):
        self.attacker.last_move_failed = True

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertFalse(self.attacker.last_move_failed)

    def test_move_has_no_secondary_effect(self):
        self.assertIsNone(self.move.effect(None, None))


if __name__ == "__main__":
    unittest.main()
