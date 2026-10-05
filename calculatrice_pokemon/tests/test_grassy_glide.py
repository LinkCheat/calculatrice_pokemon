import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.terrain import Terrain
from enums.type import Type
from field import Field
from moves import GrassyGlide
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class GrassyGlideTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = GrassyGlide()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 55)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 20)
        self.assertEqual(move.priority, 0)
        self.assertFalse(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_priority_increases_by_one_on_grassy_terrain(self):
        field = Field()
        move = GrassyGlide()

        self.assertEqual(move.get_priority(None, None, field), 0)
        field.terrain = Terrain.GRASSY
        self.assertEqual(move.get_priority(None, None, field), 1)

    def test_grassy_terrain_bonus_changes_actual_attack_order(self):
        field = Field()
        player = Pokemon("Charizard")
        opponent = Pokemon("Eevee")
        field.add_pokemon(player, "player")
        field.add_pokemon(opponent, "opponent")
        player.add_move(GrassyGlide())
        opponent.add_move(Tackle())
        player.stats["speed"] = 1
        opponent.stats["speed"] = 999

        with patch.object(Pokemon, "calculateStats"):
            field.terrain = Terrain.GRASSY
            grassy_order = field.determine_attack_order(0, 0)
            field.terrain = None
            normal_order = field.determine_attack_order(0, 0)

        self.assertIs(grassy_order[0]["pokemon"], player)
        self.assertEqual(grassy_order[0]["priority"], 1)
        self.assertIs(normal_order[0]["pokemon"], opponent)
        self.assertEqual(normal_order[0]["priority"], 0)


if __name__ == "__main__":
    unittest.main()
