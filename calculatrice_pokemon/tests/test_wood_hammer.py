import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import WoodHammer
from pokemon import Pokemon


class WoodHammerTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = WoodHammer()

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Wood Hammer")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertTrue(self.move.contact)

    def test_recoil_is_one_third_of_damage_dealt(self):
        self.attacker.current_hp -= 30

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["recoil"], 6)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 36)
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 20)
        self.assertEqual(self.move.pp, 4)

    def test_recoil_uses_damage_actually_dealt_when_target_faints(self):
        self.defender.current_hp = 10

        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 30)
        self.assertEqual(result["effect"]["recoil"], 3)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 3)
        self.assertEqual(self.defender.current_hp, 0)

    def test_recoil_cannot_reduce_user_below_zero_hp(self):
        self.attacker.current_hp = 2

        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 2)
        self.assertEqual(self.attacker.current_hp, 0)


if __name__ == "__main__":
    unittest.main()
