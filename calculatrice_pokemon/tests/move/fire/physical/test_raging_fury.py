import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import RagingFury, Tackle
from pokemon import Pokemon


class RagingFuryTests(unittest.TestCase):
    def make_battle(self):
        battle_field = Field()
        user = Pokemon("Arcanine")
        target = Pokemon("Eevee")
        user.add_move(RagingFury())
        target.add_move(Tackle())
        target.status_condition = STATUS_CONDITION.SLEEP
        target.sleep_turns_remaining = 20
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(target, "opponent")
        battle_field.initialize_battle()
        battle_field.determine_attack_order = lambda player_action, opponent_action: [
            battle_field._resolve_action("player", player_action),
            battle_field._resolve_action("opponent", opponent_action),
        ]
        battle_field.attack_hits = lambda _attacker, _defender, _move: True
        battle_field.calculate_critical_hit_multiplier = (
            lambda _attacker, _defender, _move: 1
        )
        return battle_field, user, target

    def test_move_metadata(self):
        move = RagingFury()

        self.assertEqual(move.name, "Raging Fury")
        self.assertEqual(move.type, Type.FIRE)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 120)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 10)
        self.assertTrue(move.contact)

    def test_locks_for_two_turns_spends_pp_once_and_confuses_afterward(self):
        battle_field, user, _ = self.make_battle()

        with (
            patch("moves.fire.physical.raging_fury.random.randint", return_value=2),
            patch.object(battle_field, "calculate_damage", return_value=10),
        ):
            battle_field.resolve_turn(0, 0)
            self.assertIs(user.locked_move, user.moves[0])
            self.assertEqual(user.locked_move_turns_remaining, 1)
            self.assertEqual(user.moves[0].pp, 9)

            result = battle_field.resolve_turn(0, 0)

        player_result = next(
            item["result"] for item in result if item["action"]["side"] == "player"
        )
        self.assertIsNone(user.locked_move)
        self.assertEqual(user.confusion_turns_remaining, 2)
        self.assertEqual(user.moves[0].pp, 9)
        self.assertEqual(
            player_result["lock_effect"],
            {"condition": "confusion", "applied": True, "turns": 2},
        )

    def test_lock_duration_is_two_or_three_turns(self):
        move = RagingFury()

        with patch("moves.fire.physical.raging_fury.random.randint") as randint:
            randint.side_effect = (2, 3)
            self.assertEqual(move.get_lock_turn_count(None, None), 2)
            self.assertEqual(move.get_lock_turn_count(None, None), 3)

        self.assertTrue(move.confuses_user_after_lock())

    def test_raging_fury_has_no_additional_target_effect(self):
        self.assertIsNone(RagingFury().effect(None, None))


if __name__ == "__main__":
    unittest.main()
