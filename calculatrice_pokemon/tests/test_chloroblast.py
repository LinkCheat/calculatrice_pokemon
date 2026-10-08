import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Chloroblast
from pokemon import Pokemon


class ChloroblastTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = Chloroblast()

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Chloroblast")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 150)
        self.assertEqual(self.move.accuracy, 95)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_recoil_is_half_of_users_maximum_hp(self):
        self.attacker.current_hp = self.attacker.max_hp - 10

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        recoil = self.attacker.max_hp // 2
        self.assertEqual(result["effect"]["recoil"], recoil)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 10 - recoil)
        self.assertEqual(self.move.pp, 4)

    def test_recoil_knocks_user_out_when_remaining_hp_is_too_low(self):
        self.attacker.current_hp = 1

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 1)
        self.assertEqual(self.attacker.current_hp, 0)
        self.assertEqual(result["damage"], 20)

    def test_miss_does_not_inflict_recoil(self):
        starting_hp = self.attacker.current_hp

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.current_hp, starting_hp)


if __name__ == "__main__":
    unittest.main()
