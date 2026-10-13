import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import Aromatherapy
from pokemon import Pokemon


class AromatherapyTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.bench_pokemon = Pokemon("Pikachu")
        self.opponent = Pokemon("Eevee")
        self.move = Aromatherapy()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.bench_pokemon, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Aromatherapy")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_cures_status_conditions_for_active_and_bench_pokemon(self):
        self.user.status_condition = STATUS_CONDITION.POISON
        self.bench_pokemon.status_condition = STATUS_CONDITION.SLEEP
        self.bench_pokemon.sleep_turns_remaining = 2
        self.opponent.status_condition = STATUS_CONDITION.BURN

        with patch.object(self.battle_field, "attack_hits", wraps=self.battle_field.attack_hits) as hit_check:
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertFalse(result["immune"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(result["effect"]["cured"], ["Bulbasaur", "Pikachu"])
        self.assertIsNone(self.user.status_condition)
        self.assertIsNone(self.bench_pokemon.status_condition)
        self.assertEqual(self.bench_pokemon.sleep_turns_remaining, 0)
        self.assertIs(self.opponent.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 4)
        hit_check.assert_called_once()

    def test_no_statuses_returns_empty_cure_list_and_leaves_confusion(self):
        self.user.confusion_turns_remaining = 2

        with patch("field.random.random", return_value=0.99):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["cured"], [])
        self.assertEqual(self.user.confusion_turns_remaining, 1)
        self.assertEqual(self.move.pp, 4)


if __name__ == "__main__":
    unittest.main()
