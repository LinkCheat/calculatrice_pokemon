import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import ArmorCannon
from pokemon import Pokemon


class ArmorCannonTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Armarouge")
        self.defender = Pokemon("Eevee")
        self.move = ArmorCannon()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Armor Cannon")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_lowers_users_defenses_and_consumes_pp(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(self.attacker.stat_modifiers["defense"], -1)
        self.assertEqual(self.attacker.stat_modifiers["sp_def"], -1)
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
            ],
        )
        self.assertEqual(self.move.pp, 4)

    def test_stat_drops_respect_minimum_stage(self):
        self.attacker.stat_modifiers["defense"] = -6
        self.attacker.stat_modifiers["sp_def"] = -5

        effect = self.move.effect(self.attacker, self.defender)

        self.assertEqual(self.attacker.stat_modifiers["defense"], -6)
        self.assertEqual(self.attacker.stat_modifiers["sp_def"], -6)
        self.assertEqual(
            [change["stages"] for change in effect["stat_changes"]],
            [0, -1],
        )
        self.assertEqual(
            [change["applied"] for change in effect["stat_changes"]],
            [False, True],
        )

    def test_miss_does_not_lower_users_defenses(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.stat_modifiers["defense"], 0)
        self.assertEqual(self.attacker.stat_modifiers["sp_def"], 0)


if __name__ == "__main__":
    unittest.main()
