import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import FireSpin
from moves.normal.physical.tackle import Tackle
from pokemon import Pokemon


class FireSpinTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.reserve = Pokemon("Pikachu")
        self.move = FireSpin()
        self.defender.add_move(Tackle())
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.battle_field.add_pokemon(self.reserve, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Fire Spin")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 35)
        self.assertEqual(self.move.accuracy, 85)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_successful_hit_traps_target_and_ticks_residual_damage(self):
        self.attacker.add_move(self.move)
        self.attacker.stats["speed"] = 200
        self.defender.stats["speed"] = 100

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.fire.special.fire_spin.random.randint", return_value=4),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        self.assertEqual(self.defender.fire_spin_turns_remaining, 3)
        self.assertEqual(
            self.defender.current_hp,
            self.defender.max_hp - 10 - max(1, self.defender.max_hp // 8),
        )
        effect = next(
            item["result"]["effect"]
            for item in results
            if item["action"]["side"] == "player"
        )
        self.assertTrue(effect["applied"])
        self.assertEqual(effect["turns"], 4)
        with self.assertRaisesRegex(ValueError, "piégé"):
            self.battle_field.switch_pokemon("opponent", 1)

    def test_duration_can_be_four_or_five_turns(self):
        with patch("moves.fire.special.fire_spin.random.randint") as randint:
            randint.side_effect = (4, 5)
            self.move.effect(self.attacker, self.defender)
            self.assertEqual(self.defender.fire_spin_turns_remaining, 4)
            self.move.effect(self.attacker, self.defender)
            self.assertEqual(self.defender.fire_spin_turns_remaining, 5)

    def test_ghost_target_is_not_trapped(self):
        ghost_target = Pokemon("Gengar")

        effect = self.move.effect(self.attacker, ghost_target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "ghost_immune")
        self.assertEqual(ghost_target.fire_spin_turns_remaining, 0)

    def test_fire_spin_thaws_target(self):
        self.defender.status_condition = STATUS_CONDITION.FREEZE

        with patch("moves.fire.special.fire_spin.random.randint", return_value=4):
            effect = self.move.effect(self.attacker, self.defender)

        self.assertTrue(effect["target_thawed"])
        self.assertIsNone(self.defender.status_condition)

    def test_fainted_target_is_not_trapped(self):
        self.defender.current_hp = 0

        effect = self.move.effect(self.attacker, self.defender)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "target_fainted")
        self.assertEqual(self.defender.fire_spin_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()
