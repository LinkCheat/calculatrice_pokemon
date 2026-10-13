import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import SleepPowder, Tackle
from pokemon import Pokemon
from tests.helpers.status_assertions import (
    assert_status_applied,
    assert_status_unchanged,
)


class SleepPowderTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = SleepPowder()
        self.user.add_move(self.move)
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Sleep Powder")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 75)
        self.assertEqual(self.move.max_pp, 10)
        self.assertTrue(self.move.powder)
        self.assertFalse(self.move.contact)

    def test_successful_hit_puts_target_to_sleep(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch("moves.move.random.randint", return_value=2),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        assert_status_applied(
            self, self.target, result["effect"], STATUS_CONDITION.SLEEP
        )
        self.assertEqual(self.target.sleep_turns_remaining, 2)
        self.assertEqual(self.move.pp, 9)

    def test_powder_immunity_prevents_sleeping_grass_type(self):
        grass_target = Pokemon("Bulbasaur")
        self.battle_field.add_pokemon(grass_target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertIsNone(grass_target.status_condition)

    def test_does_not_replace_existing_status(self):
        self.target.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.user, self.target)

        assert_status_unchanged(
            self, self.target, result, STATUS_CONDITION.POISON
        )


if __name__ == "__main__":
    unittest.main()
