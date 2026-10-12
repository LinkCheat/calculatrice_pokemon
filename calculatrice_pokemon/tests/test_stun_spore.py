import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import StunSpore, Tackle
from pokemon import Pokemon


class StunSporeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = StunSpore()
        self.user.add_move(self.move)
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Stun Spore")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 75)
        self.assertEqual(self.move.max_pp, 30)
        self.assertTrue(self.move.powder)
        self.assertFalse(self.move.contact)

    def test_successful_hit_paralyzes_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertIs(self.target.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertIs(result["effect"]["status"], STATUS_CONDITION.PARALYSIS)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.move.pp, 29)

    def test_electric_type_is_immune(self):
        electric_target = Pokemon("Pikachu")
        self.battle_field.add_pokemon(electric_target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertIsNone(electric_target.status_condition)
        self.assertEqual(self.move.pp, 29)

    def test_grass_type_is_immune_to_powder_move(self):
        grass_target = Pokemon("Bulbasaur")
        self.battle_field.add_pokemon(grass_target, "opponent")
        self.battle_field.switch_pokemon("opponent", 1)

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertIsNone(grass_target.status_condition)

    def test_does_not_replace_existing_status(self):
        self.target.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.user, self.target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.target.status_condition, STATUS_CONDITION.POISON)

    def test_paralysis_reduces_speed_by_half(self):
        self.user.calculateStats()
        unmodified_speed = self.user.stats["speed"]
        self.user.status_condition = STATUS_CONDITION.PARALYSIS

        self.user.calculateStats()

        self.assertEqual(self.user.stats["speed"], unmodified_speed // 2)

    def test_paralysis_has_twenty_five_percent_chance_to_prevent_move(self):
        self.target.status_condition = STATUS_CONDITION.PARALYSIS

        with patch("field.random.random", return_value=0.249999):
            result = self.battle_field.resolve_move("opponent", self.target.moves[0])

        self.assertTrue(result["unable_to_act"])
        self.assertTrue(result["paralyzed"])
        self.assertEqual(self.target.moves[0].pp, 35)

    def test_paralyzed_pokemon_can_act_when_roll_is_not_in_quarter_chance(self):
        self.target.status_condition = STATUS_CONDITION.PARALYSIS

        with (
            patch("field.random.random", return_value=0.25),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("opponent", self.target.moves[0])

        self.assertTrue(result["hit"])
        self.assertFalse(result.get("unable_to_act", False))
        self.assertEqual(self.target.moves[0].pp, 34)


if __name__ == "__main__":
    unittest.main()
