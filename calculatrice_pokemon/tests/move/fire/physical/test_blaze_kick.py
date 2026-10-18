import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import BlazeKick
from pokemon import Pokemon


class BlazeKickTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Blaziken")
        self.defender = Pokemon("Eevee")
        self.move = BlazeKick()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata_and_critical_stage_bonus(self):
        self.assertEqual(self.move.name, "Blaze Kick")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 85)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 10)
        self.assertTrue(self.move.contact)
        self.assertEqual(self.move.get_critical_hit_stage_bonus(None, None), 1)

    def test_successful_hit_can_burn_and_consumes_pp(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=12),
            patch(
                "moves.fire.physical.blaze_kick.random.random",
                return_value=0.099999,
            ),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 12)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 9)

    def test_burn_chance_failure_does_not_affect_target(self):
        with patch(
            "moves.fire.physical.blaze_kick.random.random",
            return_value=0.1,
        ):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertIsNone(self.defender.status_condition)

    def test_fire_type_target_is_immune_to_burn(self):
        fire_type_target = Pokemon("Charizard")

        with patch("moves.fire.physical.blaze_kick.random.random") as roll:
            result = self.move.effect(self.attacker, fire_type_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)
        roll.assert_not_called()

    def test_does_not_replace_existing_status(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        with patch("moves.fire.physical.blaze_kick.random.random") as roll:
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)
        roll.assert_not_called()

    def test_miss_does_not_attempt_to_burn(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.fire.physical.blaze_kick.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()
