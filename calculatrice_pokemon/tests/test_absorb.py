import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Absorb
from pokemon import Pokemon


class AbsorbTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = Absorb()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Absorb")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 20)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 25)
        self.assertFalse(self.move.contact)

    def test_restores_half_of_actual_damage_rounded_down(self):
        self.attacker.current_hp -= 10

        with patch.object(self.battle_field, "calculate_damage", return_value=7):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], 3)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 7)
        self.assertEqual(self.move.pp, 24)

    def test_healing_does_not_exceed_maximum_hp(self):
        self.attacker.current_hp = self.attacker.max_hp - 2

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], 2)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp)

    def test_miss_does_not_heal(self):
        self.attacker.current_hp -= 10

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 10)


if __name__ == "__main__":
    unittest.main()
