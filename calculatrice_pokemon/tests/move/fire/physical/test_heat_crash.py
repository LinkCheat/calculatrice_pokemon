import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import HeatCrash
from pokemon import Pokemon


class HeatCrashTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Emboar")
        self.defender = Pokemon("Eevee")
        self.move = HeatCrash()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata_and_no_secondary_effect(self):
        self.assertEqual(self.move.name, "Heat Crash")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertTrue(self.move.contact)
        self.assertIsNone(self.move.effect(None, None))

    def test_power_tiers_at_relative_weight_boundaries(self):
        self.attacker.weight = 100
        for target_weight, expected_power in (
            (20, 120),
            (20.1, 100),
            (25, 100),
            (25.1, 80),
            (100 / 3, 80),
            (33.34, 60),
            (50, 60),
            (50.1, 40),
        ):
            with self.subTest(target_weight=target_weight):
                self.defender.weight = target_weight
                self.assertEqual(
                    self.move.get_power(self.attacker, self.defender),
                    expected_power,
                )

    def test_damage_calculation_uses_relative_weight_power(self):
        self.attacker.weight = 100
        self.defender.weight = 10

        with patch.object(
            self.battle_field,
            "calculate_damage_modifiers",
            return_value=1.0,
        ):
            high_power_damage = self.battle_field.calculate_damage(
                self.attacker,
                self.defender,
                self.move,
            )
            self.defender.weight = 60
            low_power_damage = self.battle_field.calculate_damage(
                self.attacker,
                self.defender,
                self.move,
            )

        self.assertGreater(high_power_damage, low_power_damage)

    def test_successful_use_consumes_one_pp(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.move.pp, 9)
        self.assertIsNone(result["effect"])


if __name__ == "__main__":
    unittest.main()
