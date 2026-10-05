import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import FlowerTrick
from pokemon import Pokemon


class FlowerTrickTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = FlowerTrick()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 70)
        self.assertEqual(move.accuracy, 101)
        self.assertEqual(move.max_pp, 10)
        self.assertFalse(move.contact)
        self.assertEqual(move.get_critical_hit_stage_bonus(None, None), 3)
        self.assertIsNone(move.effect(None, None))

    def test_critical_hit_is_guaranteed_even_on_maximum_random_roll(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")

        with patch("field.random.random", return_value=0.999999):
            critical_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                FlowerTrick(),
            )

        self.assertEqual(critical_multiplier, 1.5)

    def test_accuracy_101_always_hits(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        move = FlowerTrick()
        attacker.stat_modifiers["accuracy"] = -6
        defender.stat_modifiers["evasion"] = 6

        with patch("field.random.random", side_effect=AssertionError("accuracy roll should be skipped")):
            self.assertTrue(battle_field.attack_hits(attacker, defender, move))


if __name__ == "__main__":
    unittest.main()
