import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import BlastBurn, Tackle
from pokemon import Pokemon


class BlastBurnTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.reserve = Pokemon("Eevee")
        self.target = Pokemon("Pikachu")
        self.move = BlastBurn()
        self.user.add_move(self.move)
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.reserve, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.user.stats["speed"] = 999
        self.target.stats["speed"] = 1

    def test_move_metadata_and_no_secondary_effect(self):
        self.assertEqual(self.move.name, "Blast Burn")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 150)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)
        self.assertIsNone(self.move.effect(None, None))

    def test_successful_hit_requires_one_recovery_turn_without_extra_pp(self):
        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            first_turn = self.battle_field.resolve_turn(0, 0)
            self.assertIs(self.user.recharging_move, self.move)
            self.assertEqual(self.move.pp, 4)
            self.assertEqual(self.target.current_hp, self.target.max_hp - 20)

            recovery_turn = self.battle_field.resolve_turn(0, 0)

        user_result = next(
            result["result"]
            for result in recovery_turn
            if result["action"]["side"] == "player"
        )
        self.assertEqual(first_turn[0]["result"]["damage"], 20)
        self.assertTrue(user_result["recharging"])
        self.assertTrue(user_result["unable_to_act"])
        self.assertEqual(self.target.current_hp, self.target.max_hp - 20)
        self.assertEqual(self.move.pp, 4)
        self.assertIsNone(self.user.recharging_move)

    def test_miss_does_not_require_a_recovery_turn(self):
        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=False),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.user.recharging_move)
        self.assertEqual(self.move.pp, 4)

    def test_immune_hit_does_not_require_a_recovery_turn(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "is_immune_to_move", return_value=True),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertIsNone(self.user.recharging_move)

    def test_switching_cancels_pending_recovery(self):
        self.user.recharging_move = self.move

        self.battle_field.switch_pokemon("player", 1)

        self.assertIsNone(self.user.recharging_move)


if __name__ == "__main__":
    unittest.main()
