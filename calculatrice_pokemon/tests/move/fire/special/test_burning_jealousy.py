import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import BurningJealousy, TorchSong
from pokemon import Pokemon


class BurningJealousyTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = BurningJealousy()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Burning Jealousy")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 70)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_burns_target_boosted_by_a_move_this_turn(self):
        with (
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch.object(self.battle_field, "attack_hits", return_value=True),
        ):
            self.battle_field.resolve_move("opponent", TorchSong())
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.defender.stat_modifiers["sp_atk"], 1)
        self.assertTrue(self.defender.stat_boosted_this_turn)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 4)

    def test_does_not_burn_target_without_a_stat_boost_this_turn(self):
        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "no_stat_boost")
        self.assertIsNone(self.defender.status_condition)

    def test_fire_type_target_is_immune_to_burn(self):
        fire_type_target = Pokemon("Charizard")
        fire_type_target.stat_boosted_this_turn = True

        result = self.move.effect(self.attacker, fire_type_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)

    def test_does_not_replace_existing_status(self):
        self.defender.stat_boosted_this_turn = True
        self.defender.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)

    def test_missed_move_does_not_burn_target(self):
        self.defender.stat_boosted_this_turn = True

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)

    def test_stat_boost_flag_is_reset_at_start_of_next_turn(self):
        self.defender.stat_boosted_this_turn = True

        with (
            patch.object(self.battle_field, "determine_attack_order", return_value=[]),
        ):
            self.battle_field.resolve_turn(0, 0)

        self.assertFalse(self.defender.stat_boosted_this_turn)


if __name__ == "__main__":
    unittest.main()
