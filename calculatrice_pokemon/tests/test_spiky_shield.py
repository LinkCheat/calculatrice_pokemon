import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Aromatherapy, SpikyShield, Tackle
from pokemon import Pokemon


class SpikyShieldTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.attacker = Pokemon("Charizard")
        self.move = SpikyShield()
        self.user.add_move(self.move)
        self.attacker.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.attacker, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Spiky Shield")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertEqual(self.move.priority, 4)
        self.assertFalse(self.move.contact)

    def test_first_use_guarantees_protection(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["protected"])
        self.assertTrue(self.user.protected_this_turn)
        self.assertEqual(self.user.protection_streak, 1)
        self.assertEqual(self.move.pp, 9)

    def test_protection_blocks_non_contact_move_without_recoil(self):
        self.user.protected_this_turn = True
        non_contact_move = Aromatherapy()
        self.attacker.add_move(non_contact_move)
        starting_hp = self.attacker.current_hp

        result = self.battle_field.resolve_move("opponent", non_contact_move)

        self.assertTrue(result["blocked_by_protection"])
        self.assertEqual(result["contact_recoil"], 0)
        self.assertEqual(self.attacker.current_hp, starting_hp)
        self.assertEqual(non_contact_move.pp, 4)

    def test_contact_move_is_blocked_and_attacker_loses_one_eighth_max_hp(self):
        self.user.protected_this_turn = True
        starting_hp = self.attacker.current_hp
        expected_recoil = max(1, self.attacker.max_hp // 8)

        result = self.battle_field.resolve_move("opponent", self.attacker.moves[0])

        self.assertTrue(result["blocked_by_protection"])
        self.assertEqual(result["contact_recoil"], expected_recoil)
        self.assertEqual(self.attacker.current_hp, starting_hp - expected_recoil)
        self.assertEqual(self.user.current_hp, self.user.max_hp)

    def test_successive_success_chance_is_halved_each_time(self):
        self.battle_field.resolve_move("player", self.move)
        self.user.protected_this_turn = False
        with patch("field.random.random", return_value=0.49):
            second = self.battle_field.resolve_move("player", self.move)
        self.user.protected_this_turn = False
        with patch("field.random.random", return_value=0.24):
            third = self.battle_field.resolve_move("player", self.move)
        self.user.protected_this_turn = False
        with patch("field.random.random", return_value=0.2):
            fourth = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(second["protected"])
        self.assertTrue(third["protected"])
        self.assertEqual(self.user.protection_streak, 0)
        self.assertTrue(fourth["protection_failed"])
        self.assertFalse(self.user.protected_this_turn)
        self.assertEqual(self.move.pp, 6)

    def test_using_another_move_resets_successive_protection_streak(self):
        self.user.add_move(Tackle())
        self.battle_field.resolve_move("player", self.move)
        self.battle_field.resolve_move("player", self.user.moves[1])

        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["protected"])
        self.assertEqual(self.user.protection_streak, 1)

    def test_protection_has_priority_over_normal_attacks(self):
        self.user.add_move(Tackle())
        self.attacker.stats["speed"] = 999
        self.user.stats["speed"] = 1

        order = self.battle_field.determine_attack_order(0, 0)

        self.assertIs(order[0]["pokemon"], self.user)
        self.assertEqual(order[0]["priority"], 4)


if __name__ == "__main__":
    unittest.main()
