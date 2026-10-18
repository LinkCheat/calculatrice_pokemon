import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import FlareBlitz
from pokemon import Pokemon


class FlareBlitzTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Cinderace")
        self.defender = Pokemon("Eevee")
        self.move = FlareBlitz()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Flare Blitz")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_successful_hit_causes_recoil_burn_and_thaws_user(self):
        self.attacker.current_hp -= 30
        self.attacker.status_condition = STATUS_CONDITION.FREEZE

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
            patch("moves.fire.physical.flare_blitz.random.random", return_value=0.099999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["recoil"], 6)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 36)
        self.assertIsNone(self.attacker.status_condition)
        self.assertTrue(result["effect"]["user_thawed"])
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.BURN)
        self.assertEqual(self.move.pp, 14)

    def test_recoil_uses_damage_actually_dealt_when_target_faints(self):
        self.defender.current_hp = 10

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=30),
            patch("moves.fire.physical.flare_blitz.random.random", return_value=0.5),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 30)
        self.assertEqual(result["effect"]["recoil"], 3)
        self.assertEqual(self.defender.current_hp, 0)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 3)

    def test_recoil_cannot_reduce_user_below_zero_hp(self):
        self.attacker.current_hp = 2

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=30),
            patch("moves.fire.physical.flare_blitz.random.random", return_value=0.5),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 2)
        self.assertEqual(self.attacker.current_hp, 0)

    def test_burn_chance_failure_does_not_affect_target_status(self):
        with patch("moves.fire.physical.flare_blitz.random.random", return_value=0.1):
            result = self.move.apply_effect(self.attacker, self.defender, damage_dealt=10)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertIsNone(self.defender.status_condition)

    def test_fire_type_target_is_immune_to_burn(self):
        fire_type_target = Pokemon("Charizard")

        with patch("moves.fire.physical.flare_blitz.random.random") as roll:
            result = self.move.apply_effect(
                self.attacker,
                fire_type_target,
                damage_dealt=10,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(fire_type_target.status_condition)
        roll.assert_not_called()

    def test_does_not_replace_existing_status(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        with patch("moves.fire.physical.flare_blitz.random.random") as roll:
            result = self.move.apply_effect(
                self.attacker,
                self.defender,
                damage_dealt=10,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)
        roll.assert_not_called()

    def test_miss_does_not_inflict_recoil_or_thaw_user(self):
        self.attacker.status_condition = STATUS_CONDITION.FREEZE
        starting_hp = self.attacker.current_hp

        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.fire.physical.flare_blitz.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.current_hp, starting_hp)
        self.assertIs(self.attacker.status_condition, STATUS_CONDITION.FREEZE)
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()
