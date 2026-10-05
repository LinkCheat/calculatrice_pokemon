import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import NeedleArm
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class NeedleArmTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.attacker.add_move(NeedleArm())
        self.defender.add_move(Tackle())
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = self.attacker.moves[0]

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Needle Arm")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 60)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_faster_needle_arm_can_flinch_target_before_its_action(self):
        self.attacker.stats["speed"] = 200
        self.defender.stats["speed"] = 100

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.needle_arm.random.random", return_value=0.1),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        player_result = next(item["result"] for item in results if item["action"]["side"] == "player")
        opponent_result = next(item["result"] for item in results if item["action"]["side"] == "opponent")
        self.assertTrue(player_result["effect"]["flinched"])
        self.assertTrue(opponent_result["unable_to_act"])
        self.assertTrue(opponent_result["flinched"])
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 10)
        self.assertFalse(self.defender.flinched)

    def test_needle_arm_cannot_flinch_target_that_already_acted(self):
        self.attacker.stats["speed"] = 100
        self.defender.stats["speed"] = 200

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.needle_arm.random.random", return_value=0.1) as roll,
        ):
            results = self.battle_field.resolve_turn(0, 0)

        player_result = next(item["result"] for item in results if item["action"]["side"] == "player")
        opponent_result = next(item["result"] for item in results if item["action"]["side"] == "opponent")
        self.assertEqual(opponent_result["damage"], 10)
        self.assertFalse(player_result["effect"]["applied"])
        self.assertEqual(player_result["effect"]["reason"], "target_already_acted")
        roll.assert_not_called()

    def test_chance_failure_does_not_flinch(self):
        with patch("moves.grass.needle_arm.random.random", return_value=0.3):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertFalse(self.defender.flinched)


if __name__ == "__main__":
    unittest.main()
