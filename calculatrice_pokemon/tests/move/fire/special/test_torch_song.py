import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import TorchSong
from pokemon import Pokemon


class TorchSongTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Skeledirge")
        self.defender = Pokemon("Eevee")
        self.move = TorchSong()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Torch Song")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)
        self.assertTrue(self.move.sound)

    def test_successful_hit_raises_user_special_attack(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 1)
        self.assertEqual(self.defender.stat_modifiers["sp_atk"], 0)
        self.assertEqual(result["effect"]["stat"], "sp_atk")
        self.assertEqual(result["effect"]["stages"], 1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["recipient"], "user")
        self.assertEqual(self.move.pp, 9)

    def test_special_attack_boost_respects_maximum_stage(self):
        self.attacker.stat_modifiers["sp_atk"] = 6

        effect = self.move.effect(self.attacker, self.defender)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["stages"], 0)
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 6)

    def test_miss_does_not_raise_user_special_attack(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.stat_modifiers["sp_atk"], 0)


if __name__ == "__main__":
    unittest.main()
