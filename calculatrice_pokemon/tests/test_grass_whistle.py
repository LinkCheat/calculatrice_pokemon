import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import GrassWhistle, Tackle
from pokemon import Pokemon


class GrassWhistleTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = GrassWhistle()
        self.user.add_move(self.move)
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Grass Whistle")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 55)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.sound)
        self.assertFalse(self.move.powder)

    def test_successful_hit_puts_target_to_sleep(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch("moves.move.random.randint", return_value=2),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertIs(self.target.status_condition, STATUS_CONDITION.SLEEP)
        self.assertEqual(self.target.sleep_turns_remaining, 2)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 14)

    def test_failed_accuracy_does_not_put_target_to_sleep(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.target.status_condition)
        self.assertEqual(self.move.pp, 14)

    def test_does_not_replace_existing_status(self):
        self.target.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.target.status_condition, STATUS_CONDITION.POISON)


if __name__ == "__main__":
    unittest.main()
