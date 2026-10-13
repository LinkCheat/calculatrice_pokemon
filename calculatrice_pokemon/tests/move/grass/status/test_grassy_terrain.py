import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import GrassyTerrain
from pokemon import Pokemon
from tests.helpers.terrain_assertions import assert_grassy_terrain_active


class GrassyTerrainTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = GrassyTerrain()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Grassy Terrain")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_move_sets_grassy_terrain_and_consumes_pp(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(result["effect"]["condition"], "grassy_terrain")
        assert_grassy_terrain_active(self, self.battle_field)
        self.assertEqual(self.move.pp, 9)


if __name__ == "__main__":
    unittest.main()
