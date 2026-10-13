import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from enums.ability import Ability
from enums.status_condition import STATUS_CONDITION
from field import Field
from moves import GrassWhistle, SleepPowder, Spore, Tackle
from pokemon import Pokemon


class InsomniaTests(unittest.TestCase):
    def setUp(self):
        self.target = Pokemon("Eevee")
        self.target.ability = Ability.INSOMNIA
        self.user = Pokemon("Bulbasaur")

    def test_sleep_powder_cannot_put_target_to_sleep(self):
        result = SleepPowder().effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "ability_immune")
        self.assertIsNone(self.target.status_condition)

    def test_grass_whistle_cannot_put_target_to_sleep(self):
        result = GrassWhistle().effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "ability_immune")
        self.assertIsNone(self.target.status_condition)

    def test_spore_cannot_put_target_to_sleep(self):
        result = Spore().effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "ability_immune")
        self.assertIsNone(self.target.status_condition)

    def test_insomnia_holder_recovers_and_can_act_if_sleep_is_already_set(self):
        battle_field = Field()
        self.target.add_move(Tackle())
        battle_field.add_pokemon(self.user, "player")
        battle_field.add_pokemon(self.target, "opponent")
        self.target.status_condition = STATUS_CONDITION.SLEEP
        self.target.sleep_turns_remaining = 2

        with patch.object(battle_field, "calculate_damage", return_value=0):
            result = battle_field.resolve_move("opponent", self.target.moves[0])

        self.assertTrue(result["hit"])
        self.assertIsNone(self.target.status_condition)
        self.assertEqual(self.target.sleep_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()
