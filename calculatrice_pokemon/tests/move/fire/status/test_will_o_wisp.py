import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import WillOWisp
from pokemon import Pokemon


class WillOWispTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.move = WillOWisp()
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Will-O-Wisp")
        self.assertIs(self.move.type, Type.FIRE)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 85)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_successful_use_burns_target_and_consumes_pp(self):
        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(result["effect"]["status"], STATUS_CONDITION.BURN)
        self.assertIs(self.target.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 14)

    def test_fire_type_target_is_immune(self):
        fire_type_target = Pokemon("Charizard")

        result = self.move.effect(self.user, fire_type_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)

    def test_does_not_replace_existing_status(self):
        self.target.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.target.status_condition, STATUS_CONDITION.POISON)

    def test_miss_does_not_burn_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.target.status_condition)
        self.assertEqual(self.move.pp, 14)


if __name__ == "__main__":
    unittest.main()
