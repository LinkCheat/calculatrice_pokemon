import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import MagicalLeaf
from pokemon import Pokemon


class MagicalLeafTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = MagicalLeaf()

        self.assertEqual(move.name, "Magical Leaf")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.SPECIAL)
        self.assertEqual(move.power, 60)
        self.assertEqual(move.accuracy, 101)
        self.assertEqual(move.max_pp, 20)
        self.assertFalse(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_accuracy_101_always_hits_with_accuracy_and_evasion_stages(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        move = MagicalLeaf()
        attacker.stat_modifiers["accuracy"] = -6
        defender.stat_modifiers["evasion"] = 6

        with patch("field.random.random", side_effect=AssertionError("accuracy roll should be skipped")):
            self.assertTrue(battle_field.attack_hits(attacker, defender, move))

    def test_successful_hit_deals_damage_and_consumes_one_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = MagicalLeaf()

        with patch.object(battle_field, "calculate_damage", return_value=20):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(defender.current_hp, defender.max_hp - 20)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 19)


if __name__ == "__main__":
    unittest.main()
