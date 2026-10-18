import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import BurnUp
from pokemon import Pokemon


class BurnUpTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = BurnUp()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Burn Up")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 130)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_use_removes_fire_type(self):
        original_types = list(self.attacker.type)

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertTrue(result["effect"]["applied"])
        self.assertNotIn(Type.FIRE, self.attacker.type)
        self.assertEqual(
            self.attacker.type,
            [pokemon_type for pokemon_type in original_types if pokemon_type is not Type.FIRE],
        )
        self.assertEqual(self.move.pp, 4)

    def test_single_fire_type_user_becomes_typeless(self):
        fire_type_user = Pokemon("Flareon")

        result = self.move.effect(fire_type_user, self.defender)

        self.assertEqual(fire_type_user.type, [Type.NONE])
        self.assertTrue(result["applied"])

    def test_move_fails_without_fire_type(self):
        self.attacker.type = [Type.FLYING]

        with patch.object(self.battle_field, "calculate_damage") as calculate_damage:
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertTrue(result["failed"])
        self.assertEqual(result["effect"]["reason"], "no_fire_type")
        self.assertEqual(result["damage"], 0)
        self.assertEqual(self.move.pp, 4)
        calculate_damage.assert_not_called()

    def test_miss_still_removes_fire_type(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertTrue(result["effect"]["applied"])
        self.assertNotIn(Type.FIRE, self.attacker.type)

    def test_switching_out_restores_original_type(self):
        reserve = Pokemon("Pikachu")
        self.battle_field.add_pokemon(reserve, "player")
        original_types = list(self.attacker.type)

        self.battle_field.resolve_move("player", self.move)
        self.battle_field.switch_pokemon("player", 1)

        self.assertEqual(self.attacker.type, original_types)
        self.assertIsNone(self.attacker.burn_up_original_types)

    def test_initialize_battle_restores_original_type(self):
        original_types = list(self.attacker.type)
        self.move.effect(self.attacker, self.defender)

        self.battle_field.initialize_battle()

        self.assertEqual(self.attacker.type, original_types)
        self.assertIsNone(self.attacker.burn_up_original_types)


if __name__ == "__main__":
    unittest.main()
