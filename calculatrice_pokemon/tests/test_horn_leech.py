import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import HornLeech
from pokemon import Pokemon


class HornLeechTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = HornLeech()

    def test_move_metadata(self):
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 75)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertTrue(self.move.contact)

    def test_restores_half_of_damage_actually_dealt(self):
        self.attacker.current_hp -= 50
        self.defender.current_hp = 15

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["healed"], 7)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 43)
        self.assertEqual(self.defender.current_hp, 0)
        self.assertEqual(self.move.pp, 9)

    def test_healing_does_not_exceed_maximum_hp(self):
        self.attacker.current_hp = self.attacker.max_hp - 3

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], 3)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp)

    def test_full_health_user_does_not_gain_hp(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], 0)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp)


if __name__ == "__main__":
    unittest.main()
