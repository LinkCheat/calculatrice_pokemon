import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from enums.status_condition import STATUS_CONDITION
from field import Field
from moves import Tackle
from pokemon import Pokemon


class ParalysisTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.tackle = Tackle()
        self.target.add_move(self.tackle)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_paralysis_reduces_speed_by_half(self):
        self.user.calculateStats()
        unmodified_speed = self.user.stats["speed"]
        self.user.status_condition = STATUS_CONDITION.PARALYSIS

        self.user.calculateStats()

        self.assertEqual(self.user.stats["speed"], unmodified_speed // 2)

    def test_paralysis_has_twenty_five_percent_chance_to_prevent_move(self):
        self.target.status_condition = STATUS_CONDITION.PARALYSIS

        with patch("field.random.random", return_value=0.249999):
            result = self.battle_field.resolve_move("opponent", self.tackle)

        self.assertTrue(result["unable_to_act"])
        self.assertTrue(result["paralyzed"])
        self.assertEqual(self.tackle.pp, 35)

    def test_paralyzed_pokemon_can_act_outside_prevention_chance(self):
        self.target.status_condition = STATUS_CONDITION.PARALYSIS

        with (
            patch("field.random.random", return_value=0.25),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("opponent", self.tackle)

        self.assertTrue(result["hit"])
        self.assertFalse(result.get("unable_to_act", False))
        self.assertEqual(self.tackle.pp, 34)


if __name__ == "__main__":
    unittest.main()
