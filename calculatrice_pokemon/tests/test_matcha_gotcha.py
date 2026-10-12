import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import MatchaGotcha
from pokemon import Pokemon


class MatchaGotchaTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Bulbasaur")
        self.defender = Pokemon("Eevee")
        self.move = MatchaGotcha()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Matcha Gotcha")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_hit_heals_half_actual_damage_and_can_burn(self):
        self.attacker.current_hp -= 50
        self.defender.current_hp = 30

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
            patch("moves.grass.matcha_gotcha.random.random", return_value=0.199999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["healed"], 10)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 40)
        self.assertEqual(self.defender.current_hp, 10)
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.BURN)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["status"], STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 14)

    def test_burn_chance_failure_does_not_affect_target_status(self):
        with patch("moves.grass.matcha_gotcha.random.random", return_value=0.2):
            result = self.move.apply_effect(
                self.attacker,
                self.defender,
                damage_dealt=10,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertIsNone(self.defender.status_condition)

    def test_does_not_replace_existing_status(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        with patch("moves.grass.matcha_gotcha.random.random") as roll:
            result = self.move.apply_effect(
                self.attacker,
                self.defender,
                damage_dealt=10,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)
        roll.assert_not_called()

    def test_fire_type_is_immune_to_burn(self):
        fire_type_target = Pokemon("Charizard")
        result = self.move.apply_effect(
            self.attacker,
            fire_type_target,
            damage_dealt=10,
        )

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)

    def test_knocked_out_target_is_not_burned(self):
        self.defender.current_hp = 10
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
            patch("moves.grass.matcha_gotcha.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.defender.current_hp, 0)
        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "target_fainted")
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()

    def test_miss_does_not_heal_or_attempt_to_burn(self):
        self.attacker.current_hp -= 10
        starting_hp = self.attacker.current_hp

        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.grass.matcha_gotcha.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.current_hp, starting_hp)
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()
