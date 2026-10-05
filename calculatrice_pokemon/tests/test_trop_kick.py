import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves.grass.trop_kick import TropKick
from pokemon import Pokemon


class TropKickTests(unittest.TestCase):
    def test_move_metadata(self):
        move = TropKick()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 70)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 15)
        self.assertTrue(move.contact)

    def test_successful_hit_lowers_target_attack_and_consumes_one_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = TropKick()

        with patch.object(battle_field, "calculate_damage", return_value=10):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(defender.stat_modifiers["attack"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(move.pp, 14)

    def test_attack_drop_respects_minimum_stage(self):
        target = Pokemon("Eevee")
        target.stat_modifiers["attack"] = -6

        effect = TropKick().effect(None, target)

        self.assertFalse(effect["applied"])
        self.assertEqual(target.stat_modifiers["attack"], -6)


if __name__ == "__main__":
    unittest.main()
