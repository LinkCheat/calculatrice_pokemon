import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import ShellTrap, Tackle
from pokemon import Pokemon


class ShellTrapTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Turtonator")
        self.attacker = Pokemon("Eevee")
        self.move = ShellTrap()
        self.user.add_move(self.move)
        self.attacker.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.attacker, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Shell Trap")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 150)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertEqual(self.move.priority, -3)
        self.assertFalse(self.move.contact)
        self.assertTrue(self.move.is_counter_trap())
        self.assertTrue(self.move.can_use_while_asleep())

    def test_physical_attack_triggers_shell_trap_and_it_strikes_last(self):
        self.user.stats["speed"] = 999
        self.attacker.stats["speed"] = 1

        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            results = self.battle_field.resolve_turn(0, 0)

        self.assertEqual(
            [item["action"]["side"] for item in results],
            ["opponent", "player"],
        )
        user_result = next(
            item["result"] for item in results if item["action"]["side"] == "player"
        )
        self.assertEqual(user_result["damage"], 10)
        self.assertTrue(user_result["effect"]["applied"])
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 10)
        self.assertEqual(self.move.pp, 4)
        self.assertFalse(self.user.shell_trap_armed)

    def test_shell_trap_fails_if_no_physical_attack_hits_user(self):
        self.attacker.moves[0] = ShellTrap()
        self.attacker.moves[0].pp = 5

        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            results = self.battle_field.resolve_turn(0, 0)

        user_result = next(
            item["result"] for item in results if item["action"]["side"] == "player"
        )
        self.assertTrue(user_result["failed"])
        self.assertEqual(user_result["effect"]["reason"], "not_triggered")
        self.assertEqual(user_result["damage"], 0)

    def test_shell_trap_can_be_used_while_asleep(self):
        self.user.status_condition = STATUS_CONDITION.SLEEP
        self.user.sleep_turns_remaining = 2
        self.attacker.moves[0] = ShellTrap()
        self.attacker.moves[0].pp = 5

        results = self.battle_field.resolve_turn(0, 0)

        user_result = next(
            item["result"] for item in results if item["action"]["side"] == "player"
        )
        self.assertTrue(user_result["failed"])
        self.assertEqual(self.user.sleep_turns_remaining, 2)
        self.assertIs(self.user.status_condition, STATUS_CONDITION.SLEEP)

    def test_special_attack_does_not_trigger_shell_trap(self):
        class SpecialAttack(Tackle):
            def __init__(self):
                super().__init__()
                self.category = MoveCategory.SPECIAL

        self.attacker.moves[0] = SpecialAttack()
        self.user.stats["speed"] = 999
        self.attacker.stats["speed"] = 1

        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            results = self.battle_field.resolve_turn(0, 0)

        user_result = next(
            item["result"] for item in results if item["action"]["side"] == "player"
        )
        self.assertTrue(user_result["failed"])
        self.assertEqual(user_result["effect"]["reason"], "not_triggered")


if __name__ == "__main__":
    unittest.main()
