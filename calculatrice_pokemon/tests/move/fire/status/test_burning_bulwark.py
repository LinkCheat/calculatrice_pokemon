import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import BurningBulwark, Tackle
from pokemon import Pokemon


class BurningBulwarkTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.attacker = Pokemon("Eevee")
        self.move = BurningBulwark()
        self.user.add_move(self.move)
        self.attacker.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.attacker, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Burning Bulwark")
        self.assertIs(self.move.type, Type.FIRE)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertEqual(self.move.priority, 4)
        self.assertFalse(self.move.contact)

    def test_use_guarantees_protection(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["protected"])
        self.assertTrue(self.user.protected_this_turn)
        self.assertIs(self.user.protected_by_move, self.move)
        self.assertEqual(self.user.protection_streak, 1)
        self.assertEqual(self.move.pp, 9)

    def test_blocked_contact_move_burns_attacker_without_recoil(self):
        self.user.protected_this_turn = True
        self.user.protected_by_move = self.move
        starting_hp = self.attacker.current_hp

        result = self.battle_field.resolve_move("opponent", self.attacker.moves[0])

        self.assertTrue(result["blocked_by_protection"])
        self.assertEqual(result["contact_recoil"], 0)
        self.assertEqual(self.attacker.current_hp, starting_hp)
        self.assertIs(self.attacker.status_condition, STATUS_CONDITION.BURN)
        self.assertTrue(result["effect"]["applied"])

    def test_blocked_non_contact_move_does_not_burn_attacker(self):
        class NonContactAttack(Tackle):
            def __init__(self):
                super().__init__()
                self.contact = False

        non_contact = NonContactAttack()
        self.user.protected_this_turn = True
        self.user.protected_by_move = self.move

        result = self.battle_field.resolve_move("opponent", non_contact)

        self.assertTrue(result["blocked_by_protection"])
        self.assertIsNone(self.attacker.status_condition)

    def test_fire_type_attacker_is_immune_to_burn(self):
        fire_attacker = Pokemon("Charizard")
        fire_attacker.add_move(Tackle())
        self.battle_field.add_pokemon(fire_attacker, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)
        self.user.protected_this_turn = True
        self.user.protected_by_move = self.move

        result = self.battle_field.resolve_move("opponent", fire_attacker.moves[0])

        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "type_immune")
        self.assertIsNone(fire_attacker.status_condition)

    def test_existing_status_is_not_overwritten(self):
        self.attacker.status_condition = STATUS_CONDITION.POISON
        self.user.protected_this_turn = True
        self.user.protected_by_move = self.move

        result = self.battle_field.resolve_move("opponent", self.attacker.moves[0])

        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "already_statused")
        self.assertIs(self.attacker.status_condition, STATUS_CONDITION.POISON)

    def test_success_chance_is_divided_by_three(self):
        self.assertEqual(self.move.get_protection_success_chance(0), 1)
        self.assertEqual(self.move.get_protection_success_chance(1), 1 / 3)
        self.assertEqual(self.move.get_protection_success_chance(2), 1 / 9)

    def test_success_chance_has_one_over_729_floor(self):
        self.assertEqual(
            self.move.get_protection_success_chance(10),
            1 / 729,
        )

    def test_second_consecutive_use_fails_at_one_third_threshold(self):
        self.battle_field.resolve_move("player", self.move)
        self.user.protected_this_turn = False
        self.user.protected_by_move = None

        with patch("field.random.random", return_value=0.34):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["protection_failed"])
        self.assertFalse(self.user.protected_this_turn)
        self.assertEqual(self.user.protection_streak, 0)


if __name__ == "__main__":
    unittest.main()
