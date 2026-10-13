import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from enums.status_condition import STATUS_CONDITION
from field import Field
from moves import Tackle
from pokemon import Pokemon


class SleepTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.tackle = Tackle()
        self.target.add_move(self.tackle)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_sleep_prevents_target_from_using_its_move(self):
        self.target.status_condition = STATUS_CONDITION.SLEEP
        self.target.sleep_turns_remaining = 2

        with patch("moves.move.random.randint", return_value=2):
            result = self.battle_field.resolve_move("opponent", self.tackle)

        self.assertTrue(result["unable_to_act"])
        self.assertIs(self.target.status_condition, STATUS_CONDITION.SLEEP)
        self.assertEqual(self.target.sleep_turns_remaining, 1)
        self.assertEqual(self.tackle.pp, 35)


if __name__ == "__main__":
    unittest.main()
