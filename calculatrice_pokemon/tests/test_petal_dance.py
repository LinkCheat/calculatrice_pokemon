import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import PetalDance, Tackle
from pokemon import Pokemon


class PetalDanceTests(unittest.TestCase):
    def make_battle(self):
        battle_field = Field()
        user = Pokemon("Bulbasaur")
        reserve = Pokemon("Eevee")
        target = Pokemon("Charizard")
        user.add_move(PetalDance())
        target.add_move(Tackle())
        target.status_condition = STATUS_CONDITION.SLEEP
        target.sleep_turns_remaining = 20
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(reserve, "player")
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
        return battle_field, user, reserve, target

    def test_move_metadata_and_no_secondary_target_effect(self):
        move = PetalDance()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.SPECIAL)
        self.assertEqual(move.power, 120)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 10)
        self.assertFalse(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_locks_for_two_attacks_spends_pp_once_and_confuses_afterward(self):
        battle_field, user, _, _ = self.make_battle()

        with patch("moves.grass.petal_dance.random.randint", return_value=2):
            battle_field.resolve_turn(0, 0)
            self.assertIsNotNone(user.locked_move)
            self.assertEqual(user.locked_move_turns_remaining, 1)
            self.assertEqual(user.moves[0].pp, 9)

            with self.assertRaisesRegex(ValueError, "bloqué"):
                battle_field.switch_pokemon("player", 1)
            with self.assertRaisesRegex(ValueError, "bloqué"):
                battle_field._resolve_action("player", 6)

            results = battle_field.resolve_turn(0, 0)

        self.assertIsNone(user.locked_move)
        self.assertEqual(user.confusion_turns_remaining, 2)
        self.assertEqual(user.moves[0].pp, 9)
        player_result = next(
            result["result"]
            for result in results
            if result["action"]["side"] == "player"
        )
        self.assertEqual(
            player_result["lock_effect"],
            {"condition": "confusion", "applied": True, "turns": 2},
        )

    def test_lock_waits_for_attack_attempts_when_user_cannot_act(self):
        battle_field, user, _, _ = self.make_battle()

        with patch("moves.grass.petal_dance.random.randint", return_value=3):
            battle_field.resolve_turn(0, 0)
            self.assertEqual(user.locked_move_turns_remaining, 2)

            user.flinched = True
            battle_field.resolve_turn(0, 0)
            self.assertEqual(user.locked_move_turns_remaining, 2)

            user.status_condition = STATUS_CONDITION.SLEEP
            user.sleep_turns_remaining = 2
            battle_field.resolve_turn(0, 0)
            self.assertEqual(user.locked_move_turns_remaining, 2)

            battle_field.resolve_turn(0, 0)
            self.assertEqual(user.locked_move_turns_remaining, 2)

            battle_field.resolve_turn(0, 0)
            self.assertEqual(user.locked_move_turns_remaining, 1)

            results = battle_field.resolve_turn(0, 0)

        self.assertIsNone(user.locked_move)
        self.assertEqual(user.confusion_turns_remaining, 3)
        self.assertEqual(user.moves[0].pp, 9)
        player_result = next(
            result["result"]
            for result in results
            if result["action"]["side"] == "player"
        )
        self.assertEqual(
            player_result["lock_effect"],
            {"condition": "confusion", "applied": True, "turns": 3},
        )

    def test_confusion_self_hit_is_typeless_and_does_not_consume_pp(self):
        battle_field = Field()
        user = Pokemon("Bulbasaur")
        target = Pokemon("Charizard")
        move = Tackle()
        user.add_move(move)
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(target, "opponent")
        user.confusion_turns_remaining = 1
        expected_damage = (
            math.floor(
                math.floor(user.level * 0.4 + 2)
                * 40
                * user.stats["attack"]
                / user.stats["defense"]
                / 50
            )
            + 2
        )
        target_hp = target.current_hp

        with patch("field.random.random", return_value=0.0):
            result = battle_field.resolve_move("player", move)

        self.assertTrue(result["confusion_self_hit"])
        self.assertEqual(result["damage"], expected_damage)
        self.assertEqual(user.current_hp, user.max_hp - expected_damage)
        self.assertEqual(target.current_hp, target_hp)
        self.assertEqual(move.pp, move.max_pp)
        self.assertEqual(user.confusion_turns_remaining, 0)

    def test_confusion_duration_does_not_decrease_when_asleep_or_flinched(self):
        battle_field = Field()
        user = Pokemon("Bulbasaur")
        target = Pokemon("Charizard")
        move = Tackle()
        user.add_move(move)
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(target, "opponent")
        user.confusion_turns_remaining = 3
        user.flinched = True

        result = battle_field.resolve_move("player", move)
        self.assertTrue(result["flinched"])
        self.assertEqual(user.confusion_turns_remaining, 3)

        user.flinched = False
        user.status_condition = STATUS_CONDITION.SLEEP
        user.sleep_turns_remaining = 1
        result = battle_field.resolve_move("player", move)
        self.assertTrue(result["unable_to_act"])
        self.assertEqual(user.confusion_turns_remaining, 3)


if __name__ == "__main__":
    unittest.main()
