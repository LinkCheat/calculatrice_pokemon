import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import RazorLeaf
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class RazorLeafTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = RazorLeaf()

        self.assertEqual(move.name, "Razor Leaf")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 55)
        self.assertEqual(move.accuracy, 95)
        self.assertEqual(move.max_pp, 25)
        self.assertFalse(move.contact)
        self.assertEqual(move.get_critical_hit_stage_bonus(None, None), 1)
        self.assertIsNone(move.effect(None, None))

    def test_high_critical_hit_rate_increases_critical_stage_by_one(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        move = RazorLeaf()

        with patch("field.random.random", return_value=0.05):
            normal_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                Tackle(),
            )
            razor_leaf_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                move,
            )

        self.assertEqual(normal_multiplier, 1.0)
        self.assertEqual(razor_leaf_multiplier, 1.5)

    def test_successful_hit_deals_damage_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = RazorLeaf()

        with (
            patch.object(battle_field, "attack_hits", return_value=True),
            patch.object(battle_field, "calculate_damage", return_value=20),
        ):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(defender.current_hp, defender.max_hp - 20)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 24)


if __name__ == "__main__":
    unittest.main()
