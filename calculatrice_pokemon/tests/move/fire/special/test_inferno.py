import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import Inferno
from pokemon import Pokemon


class InfernoTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = Inferno()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Inferno")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 100)
        self.assertEqual(self.move.accuracy, 50)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_always_burns_eligible_target(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(result["effect"]["status"], STATUS_CONDITION.BURN)
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 4)

    def test_fire_type_target_is_immune_to_burn(self):
        fire_type_target = Pokemon("Charizard")

        result = self.move.effect(self.attacker, fire_type_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)

    def test_does_not_replace_existing_status(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)

    def test_miss_does_not_burn_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)


if __name__ == "__main__":
    unittest.main()
