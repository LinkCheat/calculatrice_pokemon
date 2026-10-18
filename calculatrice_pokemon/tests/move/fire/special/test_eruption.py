import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Eruption
from pokemon import Pokemon


class EruptionTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = Eruption()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Eruption")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 150)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_power_is_150_at_full_hp(self):
        self.assertEqual(
            self.move.get_power(self.attacker, self.defender),
            150,
        )

    def test_power_scales_with_current_hp_and_rounds_down(self):
        self.attacker.current_hp = self.attacker.max_hp * 2 // 3

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender),
            100,
        )

    def test_power_has_minimum_of_one(self):
        self.attacker.current_hp = 1

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender),
            1,
        )

    def test_damage_calculation_uses_power_scaled_by_current_hp(self):
        self.attacker.current_hp = self.attacker.max_hp // 2

        with patch.object(self.battle_field, "calculate_damage_modifiers", return_value=1.0):
            damage = self.battle_field.calculate_damage(
                self.attacker,
                self.defender,
                self.move,
            )

        self.assertGreater(damage, 0)

    def test_successful_hit_consumes_pp_without_secondary_effect(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=15),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 15)
        self.assertIsNone(result["effect"])
        self.assertEqual(self.move.pp, 4)


if __name__ == "__main__":
    unittest.main()
