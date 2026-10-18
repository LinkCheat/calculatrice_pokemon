import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import VCreate
from pokemon import Pokemon


class VCreateTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Victini")
        self.defender = Pokemon("Eevee")
        self.move = VCreate()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "V-create")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 180)
        self.assertEqual(self.move.accuracy, 95)
        self.assertEqual(self.move.max_pp, 5)
        self.assertTrue(self.move.contact)

    def test_successful_hit_lowers_users_defenses_and_speed(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        for stat in ("defense", "sp_def", "speed"):
            self.assertEqual(self.attacker.stat_modifiers[stat], -1)
        self.assertEqual(
            result["effect"]["stat_changes"],
            [
                {
                    "stat": "defense",
                    "stages": -1,
                    "applied": True,
                    "recipient": "user",
                },
                {
                    "stat": "sp_def",
                    "stages": -1,
                    "applied": True,
                    "recipient": "user",
                },
                {
                    "stat": "speed",
                    "stages": -1,
                    "applied": True,
                    "recipient": "user",
                },
            ],
        )
        self.assertEqual(self.move.pp, 4)

    def test_stat_drops_respect_minimum_stage(self):
        self.attacker.stat_modifiers["defense"] = -6
        self.attacker.stat_modifiers["sp_def"] = -5
        self.attacker.stat_modifiers["speed"] = 0

        effect = self.move.effect(self.attacker, self.defender)

        self.assertEqual(self.attacker.stat_modifiers["defense"], -6)
        self.assertEqual(self.attacker.stat_modifiers["sp_def"], -6)
        self.assertEqual(self.attacker.stat_modifiers["speed"], -1)
        self.assertEqual(
            [change["stages"] for change in effect["stat_changes"]],
            [0, -1, -1],
        )
        self.assertEqual(
            [change["applied"] for change in effect["stat_changes"]],
            [False, True, True],
        )

    def test_miss_does_not_lower_users_stats(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        for stat in ("defense", "sp_def", "speed"):
            self.assertEqual(self.attacker.stat_modifiers[stat], 0)


if __name__ == "__main__":
    unittest.main()
