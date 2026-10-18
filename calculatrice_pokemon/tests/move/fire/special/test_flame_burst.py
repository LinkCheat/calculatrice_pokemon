import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import FlameBurst
from pokemon import Pokemon


class FlameBurstTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Victini")
        self.target = Pokemon("Eevee")
        self.move = FlameBurst()
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Flame Burst")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 70)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_successful_hit_deals_damage_and_consumes_pp(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(self.target.current_hp, self.target.max_hp - 20)
        self.assertIsNone(result["effect"])
        self.assertEqual(self.move.pp, 14)

    def test_miss_does_not_damage_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.target.current_hp, self.target.max_hp)

    def test_no_secondary_effect_in_single_battle(self):
        self.assertIsNone(self.move.effect(self.user, self.target))


if __name__ == "__main__":
    unittest.main()
