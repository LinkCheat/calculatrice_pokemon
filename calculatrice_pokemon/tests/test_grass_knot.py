import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import GrassKnot
from pokemon import Pokemon


class GrassKnotTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.move = GrassKnot()
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata_and_no_secondary_effect(self):
        self.assertEqual(self.move.name, "Grass Knot")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)
        self.assertIsNone(self.move.effect(None, None))

    def test_power_tiers_at_weight_boundaries(self):
        for weight, expected_power in (
            (10, 20),
            (10.1, 40),
            (25, 40),
            (25.1, 60),
            (50, 60),
            (50.1, 80),
            (100, 80),
            (100.1, 100),
            (200, 100),
            (200.1, 120),
        ):
            with self.subTest(weight=weight):
                self.target.weight = weight
                self.assertEqual(
                    self.move.get_power(self.user, self.target),
                    expected_power,
                )

    def test_damage_calculation_uses_target_weight_power(self):
        self.target.weight = 10

        with patch.object(self.battle_field, "calculate_damage_modifiers", return_value=1.0):
            light_target_damage = self.battle_field.calculate_damage(
                self.user,
                self.target,
                self.move,
            )
            self.target.weight = 200.1
            heavy_target_damage = self.battle_field.calculate_damage(
                self.user,
                self.target,
                self.move,
            )

        self.assertGreater(heavy_target_damage, light_target_damage)

    def test_successful_use_consumes_one_pp(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.move.pp, 19)
        self.assertIsNone(result["effect"])


if __name__ == "__main__":
    unittest.main()
