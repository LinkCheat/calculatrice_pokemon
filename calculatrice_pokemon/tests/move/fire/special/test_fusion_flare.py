import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import FusionFlare
from moves.move import Moves
from pokemon import Pokemon


class FusionBolt(Moves):
    def __init__(self):
        super().__init__(
            name="Fusion Bolt",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=100,
            accuracy=100,
            max_pp=5,
        )

    def effect(self, user, target):
        return None


class FusionFlareTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Reshiram")
        self.defender = Pokemon("Eevee")
        self.move = FusionFlare()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Fusion Flare")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 100)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_power_doubles_after_fusion_bolt(self):
        self.assertEqual(
            self.move.get_power(self.attacker, self.defender, self.battle_field),
            100,
        )
        self.battle_field.last_move_used = "Fusion Bolt"

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender, self.battle_field),
            200,
        )

    def test_power_does_not_double_after_another_move(self):
        self.battle_field.last_move_used = "Thunderbolt"

        self.assertEqual(
            self.move.get_power(self.attacker, self.defender, self.battle_field),
            100,
        )

    def test_resolving_fusion_bolt_sets_power_boost_for_next_move(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            self.battle_field.resolve_move("opponent", FusionBolt())

        self.assertEqual(self.battle_field.last_move_used, "Fusion Bolt")
        self.assertEqual(
            self.move.get_power(self.attacker, self.defender, self.battle_field),
            200,
        )

    def test_fusion_flare_thaws_user_and_target(self):
        self.attacker.status_condition = STATUS_CONDITION.FREEZE
        self.defender.status_condition = STATUS_CONDITION.FREEZE

        with patch.object(self.battle_field, "calculate_damage", return_value=10):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["user_thawed"], True)
        self.assertEqual(result["effect"]["target_thawed"], True)
        self.assertIsNone(self.attacker.status_condition)
        self.assertIsNone(self.defender.status_condition)

    def test_fusion_flare_has_no_effect_when_pokemon_are_not_frozen(self):
        self.assertIsNone(self.move.effect(self.attacker, self.defender))

    def test_start_of_turn_clears_previous_move(self):
        self.battle_field.last_move_used = "Fusion Bolt"
        with patch.object(self.battle_field, "determine_attack_order", return_value=[]):
            self.battle_field.resolve_turn(0, 0)

        self.assertIsNone(self.battle_field.last_move_used)


if __name__ == "__main__":
    unittest.main()
