import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import SappySeed
from pokemon import Pokemon


class SappySeedTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.move = SappySeed()

    def test_move_metadata(self):
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 90)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)

    def test_successful_hit_deals_damage_and_seeds_target(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 30)
        self.assertEqual(self.target.current_hp, self.target.max_hp - 30)
        self.assertTrue(self.target.leech_seeded)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 14)

    def test_grass_type_is_immune(self):
        grass_target = Pokemon("Bulbasaur")
        self.battle_field.add_pokemon(grass_target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)

        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertEqual(result["damage"], 0)
        self.assertFalse(grass_target.leech_seeded)

    def test_already_seeded_target_still_takes_damage(self):
        self.target.leech_seeded = True
        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 30)
        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "already_seeded")

    def test_knocked_out_target_is_not_seeded(self):
        self.target.current_hp = 10
        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.target.current_hp, 0)
        self.assertFalse(self.target.leech_seeded)
        self.assertEqual(result["effect"]["reason"], "target_fainted")


if __name__ == "__main__":
    unittest.main()
