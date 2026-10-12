import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import ForestCurse
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class ForestCurseTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = ForestCurse()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Forest's Curse")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_successful_use_adds_grass_as_a_type(self):
        original_types = list(self.target.type)
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(self.target.type, original_types + [Type.GRASS])
        self.assertTrue(self.target.forest_cursed)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 19)

    def test_grass_type_is_used_in_effectiveness_calculations(self):
        self.battle_field.resolve_move("player", self.move)

        self.assertEqual(
            self.battle_field.calculate_move_effectiveness(
                Tackle(), self.target, self.user
            ),
            1.0,
        )
        self.assertEqual(
            self.battle_field.calculate_move_effectiveness(
                ForestCurse(), self.target, self.user
            ),
            0.5,
        )

    def test_already_grass_type_target_does_not_receive_duplicate_type(self):
        target = Pokemon("Bulbasaur")
        self.battle_field.add_pokemon(target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)

        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(target.type.count(Type.GRASS), 1)
        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "already_grass_type")

    def test_added_type_is_removed_when_target_switches_out(self):
        reserve = Pokemon("Pikachu")
        self.battle_field.add_pokemon(reserve, "opponent")
        original_types = list(self.target.type)

        self.battle_field.resolve_move("player", self.move)
        self.battle_field.switch_pokemon("opponent", 1)

        self.assertEqual(self.target.type, original_types)
        self.assertFalse(self.target.forest_cursed)

    def test_miss_does_not_change_target_types(self):
        original_types = list(self.target.type)
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.target.type, original_types)
        self.assertFalse(self.target.forest_cursed)


if __name__ == "__main__":
    unittest.main()
