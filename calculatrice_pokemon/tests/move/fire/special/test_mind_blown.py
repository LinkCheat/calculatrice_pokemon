import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import MindBlown
from pokemon import Pokemon


class MindBlownTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Blacephalon")
        self.defender = Pokemon("Eevee")
        self.move = MindBlown()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Mind Blown")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 150)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_costs_half_maximum_hp_rounding_up(self):
        self.attacker.current_hp = 100

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        expected_cost = (self.attacker.max_hp + 1) // 2
        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["recoil"], expected_cost)
        self.assertEqual(self.attacker.current_hp, 100 - expected_cost)
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 20)
        self.assertEqual(self.move.pp, 4)

    def test_miss_still_costs_half_maximum_hp(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        cost = (self.attacker.max_hp + 1) // 2
        self.assertFalse(result["hit"])
        self.assertEqual(result["effect"]["recoil"], cost)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - cost)

    def test_protection_still_costs_half_maximum_hp(self):
        self.defender.protected_this_turn = True

        result = self.battle_field.resolve_move("player", self.move)

        cost = (self.attacker.max_hp + 1) // 2
        self.assertTrue(result["blocked_by_protection"])
        self.assertEqual(result["effect"]["recoil"], cost)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - cost)

    def test_cost_can_knock_user_out(self):
        self.attacker.current_hp = 1

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.attacker.current_hp, 0)
        self.assertEqual(result["effect"]["recoil"], 1)


if __name__ == "__main__":
    unittest.main()
