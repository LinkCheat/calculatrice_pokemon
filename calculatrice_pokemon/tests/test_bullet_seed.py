import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves.grass.bullet_seed import BulletSeed
from pokemon import Pokemon


class BulletSeedTests(unittest.TestCase):
    def test_move_metadata_and_hit_count_odds(self):
        move = BulletSeed()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 25)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 30)
        with patch("moves.grass.bullet_seed.random.choices", return_value=[4]) as choices:
            self.assertEqual(move.get_hit_count(None, None), 4)

        choices.assert_called_once_with(
            (2, 3, 4, 5),
            weights=(35, 35, 15, 15),
            k=1,
        )

    def test_move_applies_each_hit_until_target_faints(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = BulletSeed()
        defender.current_hp = 25

        with (
            patch.object(move, "get_hit_count", return_value=5),
            patch.object(battle_field, "calculate_damage", return_value=10),
        ):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["hits"], 3)
        self.assertEqual(result["damage"], 30)
        self.assertEqual(defender.current_hp, 0)
        self.assertEqual(move.pp, 29)
        self.assertIsNone(result["effect"])


if __name__ == "__main__":
    unittest.main()
