import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import SeedFlare
from pokemon import Pokemon


class SeedFlareTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = SeedFlare()
        self.attacker.add_move(self.move)
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Seed Flare")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 85)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_effect_lowers_special_defense_by_two_stages(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch("moves.grass.seed_flare.random.random", return_value=0.399999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -2)
        self.assertEqual(result["effect"]["stat"], "sp_def")
        self.assertEqual(result["effect"]["stages"], -2)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 4)

    def test_chance_failure_does_not_lower_special_defense(self):
        with patch("moves.grass.seed_flare.random.random", return_value=0.4):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertEqual(self.defender.stat_modifiers["sp_def"], 0)

    def test_special_defense_drop_is_capped_at_negative_six(self):
        self.defender.stat_modifiers["sp_def"] = -5

        with patch("moves.grass.seed_flare.random.random", return_value=0.0):
            result = self.move.effect(self.attacker, self.defender)

        self.assertTrue(result["applied"])
        self.assertEqual(result["stages"], -1)
        self.assertEqual(self.defender.stat_modifiers["sp_def"], -6)


if __name__ == "__main__":
    unittest.main()
