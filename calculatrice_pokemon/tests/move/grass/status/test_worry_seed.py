import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.ability import Ability
from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import Tackle, WorrySeed
from pokemon import Pokemon


class WorrySeedTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.reserve = Pokemon("Pikachu")
        self.move = WorrySeed()
        self.user.add_move(self.move)
        self.user.add_move(Tackle())
        self.target.ability = Ability.INTIMIDATION
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.battle_field.add_pokemon(self.reserve, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Worry Seed")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_hit_temporarily_replaces_ability_and_consumes_pp(self):
        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertIs(self.target.ability, Ability.INSOMNIA)
        self.assertIs(result["effect"]["ability"], Ability.INSOMNIA)
        self.assertTrue(result["effect"]["applied"])
        self.assertFalse(result["effect"]["woke_up"])
        self.assertEqual(self.move.pp, 9)

    def test_replaced_ability_is_restored_when_target_switches_out(self):
        self.move.effect(self.user, self.target)
        self.battle_field.switch_pokemon("opponent", 1)

        self.assertIs(self.target.ability, Ability.INTIMIDATION)
        self.assertIs(self.battle_field.opponent_active_pokemon, self.reserve)

    def test_worry_seed_immediately_wakes_a_sleeping_target(self):
        self.target.status_condition = STATUS_CONDITION.SLEEP
        self.target.sleep_turns_remaining = 3

        result = self.move.effect(self.user, self.target)

        self.assertIs(self.target.ability, Ability.INSOMNIA)
        self.assertIsNone(self.target.status_condition)
        self.assertEqual(self.target.sleep_turns_remaining, 0)
        self.assertTrue(result["woke_up"])

    def test_missed_move_does_not_change_target_ability(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIs(self.target.ability, Ability.INTIMIDATION)
        self.assertEqual(self.move.pp, 9)


if __name__ == "__main__":
    unittest.main()
