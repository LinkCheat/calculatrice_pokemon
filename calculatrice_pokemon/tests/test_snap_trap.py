import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import SnapTrap
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class SnapTrapTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.reserve = Pokemon("Pikachu")
        self.user.add_move(SnapTrap())
        self.user.add_move(Tackle())
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.reserve, "opponent")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)
        self.move = self.user.moves[0]

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Snap Trap")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 35)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_successful_hit_traps_target_for_four_or_five_turns(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.snap_trap.random.randint", return_value=4),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["condition"], "snap_trap")
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["turns"], 4)
        self.assertEqual(self.target.snap_trap_turns_remaining, 4)
        self.assertEqual(self.move.pp, 14)

        with patch("moves.grass.snap_trap.random.randint", return_value=5):
            self.move.effect(self.user, self.target)
        self.assertEqual(self.target.snap_trap_turns_remaining, 5)

    def test_trapped_target_cannot_switch_until_trap_expires(self):
        self.target.snap_trap_turns_remaining = 1

        with self.assertRaisesRegex(ValueError, "piégé"):
            self.battle_field.switch_pokemon("opponent", 0)
        with self.assertRaisesRegex(ValueError, "piégé"):
            self.battle_field.determine_attack_order(1, self.battle_field.SWITCH_INDEX_OFFSET)

        self.target.current_hp = 0
        self.assertIs(self.battle_field.switch_pokemon("opponent", 0), self.reserve)
        self.assertEqual(self.target.snap_trap_turns_remaining, 0)

    def test_residual_damage_ticks_down_and_clears_trap(self):
        self.target.snap_trap_turns_remaining = 2
        expected_damage = max(1, self.target.max_hp // 8)

        first_tick = self.battle_field._apply_snap_trap()
        self.assertEqual(first_tick[0]["result"]["damage"], expected_damage)
        self.assertEqual(first_tick[0]["result"]["turns_remaining"], 1)
        self.assertEqual(self.target.current_hp, self.target.max_hp - expected_damage)

        second_tick = self.battle_field._apply_snap_trap()
        self.assertEqual(second_tick[0]["result"]["turns_remaining"], 0)
        self.assertEqual(self.target.snap_trap_turns_remaining, 0)

        self.battle_field.switch_pokemon("opponent", 0)
        self.assertIs(self.battle_field.opponent_active_pokemon, self.reserve)

    def test_snap_trap_ticks_at_the_end_of_the_turn_it_is_applied(self):
        self.user.stats["speed"] = 200
        self.target.stats["speed"] = 100

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.snap_trap.random.randint", return_value=4),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        self.assertEqual(self.target.snap_trap_turns_remaining, 3)
        residual = next(
            item for item in results
            if item["action"]["type"] == "snap_trap_residual"
        )
        self.assertEqual(
            residual["result"]["damage"],
            max(1, self.target.max_hp // 8),
        )

    def test_fainted_target_is_not_trapped(self):
        self.target.current_hp = 0

        effect = self.move.effect(self.user, self.target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "target_fainted")
        self.assertEqual(self.target.snap_trap_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()
