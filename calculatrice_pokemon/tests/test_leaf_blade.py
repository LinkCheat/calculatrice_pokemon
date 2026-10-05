import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import LeafBlade
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class LeafBladeTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = LeafBlade()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 90)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 15)
        self.assertTrue(move.contact)
        self.assertEqual(move.get_critical_hit_stage_bonus(None, None), 1)
        self.assertIsNone(move.effect(None, None))

    def test_high_critical_hit_rate_increases_critical_stage_by_one(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        move = LeafBlade()

        with patch("field.random.random", return_value=0.05):
            normal_move_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                Tackle(),
            )
            leaf_blade_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                move,
            )

        self.assertEqual(normal_move_multiplier, 1.0)
        self.assertEqual(leaf_blade_multiplier, 1.5)

    def test_successful_hit_deals_damage_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = LeafBlade()

        with patch.object(battle_field, "calculate_damage", return_value=25):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 25)
        self.assertEqual(defender.current_hp, defender.max_hp - 25)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 14)


if __name__ == "__main__":
    unittest.main()
