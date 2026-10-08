import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import SyrupBomb
from pokemon import Pokemon


class SyrupBombTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.reserve = Pokemon("Pikachu")
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.battle_field.add_pokemon(self.reserve, "opponent")
        self.move = SyrupBomb()

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Syrup Bomb")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 65)
        self.assertEqual(self.move.accuracy, 85)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_hit_starts_three_delayed_speed_drops(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["turns"], 3)
        self.assertEqual(self.target.stat_modifiers["speed"], 0)
        self.assertEqual(self.target.syrupy_turns_remaining, 3)
        self.assertTrue(self.target.syrupy_skip_next_tick)
        self.assertEqual(self.move.pp, 9)

    def test_speed_drops_one_stage_at_end_of_each_of_three_following_turns(self):
        self.move.effect(self.attacker, self.target)

        current_turn_tick = self.battle_field._apply_syrup_bomb()
        self.assertEqual(current_turn_tick, [])
        self.assertEqual(self.target.stat_modifiers["speed"], 0)
        self.assertEqual(self.target.syrupy_turns_remaining, 3)

        for expected_remaining in (2, 1, 0):
            with self.subTest(turns_remaining=expected_remaining):
                residual = self.battle_field._apply_syrup_bomb()
                self.assertEqual(len(residual), 1)
                self.assertEqual(residual[0]["result"]["stages"], -1)
                self.assertEqual(
                    residual[0]["result"]["turns_remaining"],
                    expected_remaining,
                )
                self.assertEqual(
                    self.target.stat_modifiers["speed"],
                    -(3 - expected_remaining),
                )

        self.assertEqual(self.target.syrupy_turns_remaining, 0)

    def test_syrup_effect_is_removed_when_target_switches_out(self):
        self.move.effect(self.attacker, self.target)

        self.battle_field.switch_pokemon("opponent", 1)

        self.assertEqual(self.target.syrupy_turns_remaining, 0)
        self.assertFalse(self.target.syrupy_skip_next_tick)
        self.assertEqual(self.battle_field._apply_syrup_bomb(), [])

    def test_fainted_target_is_not_affected(self):
        self.target.current_hp = 0

        effect = self.move.effect(self.attacker, self.target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "target_fainted")
        self.assertEqual(self.target.syrupy_turns_remaining, 0)

    def test_speed_stage_cannot_drop_below_minus_six(self):
        self.target.stat_modifiers["speed"] = -5
        self.move.effect(self.attacker, self.target)
        self.target.syrupy_skip_next_tick = False

        self.battle_field._apply_syrup_bomb()
        self.battle_field._apply_syrup_bomb()
        self.battle_field._apply_syrup_bomb()

        self.assertEqual(self.target.stat_modifiers["speed"], -6)
        self.assertEqual(self.target.syrupy_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()
