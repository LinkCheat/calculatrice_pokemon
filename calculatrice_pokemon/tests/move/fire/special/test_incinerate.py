import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Incinerate
from pokemon import Pokemon


class IncinerateTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = Incinerate()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Incinerate")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 60)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_successful_hit_destroys_held_berry(self):
        self.defender.item = "Sitrus Berry"

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=12),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 12)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["item_destroyed"], "Sitrus Berry")
        self.assertIsNone(self.defender.item)
        self.assertEqual(self.move.pp, 14)

    def test_successful_hit_destroys_held_gem(self):
        self.defender.item = "Fire Gem"

        result = self.move.effect(self.attacker, self.defender)

        self.assertTrue(result["applied"])
        self.assertEqual(result["item_destroyed"], "Fire Gem")
        self.assertIsNone(self.defender.item)

    def test_other_held_items_are_not_destroyed(self):
        self.defender.item = "Charcoal"

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertIsNone(result["item_destroyed"])
        self.assertEqual(self.defender.item, "Charcoal")

    def test_no_item_is_reported_as_no_effect(self):
        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertIsNone(result["item_destroyed"])

    def test_miss_does_not_destroy_item(self):
        self.defender.item = "Sitrus Berry"

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.defender.item, "Sitrus Berry")


if __name__ == "__main__":
    unittest.main()
