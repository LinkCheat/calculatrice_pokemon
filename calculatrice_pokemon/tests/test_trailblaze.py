import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Trailblaze
from pokemon import Pokemon


class TrailblazeTests(unittest.TestCase):
    def test_move_metadata(self):
        move = Trailblaze()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 50)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 20)
        self.assertTrue(move.contact)

    def test_successful_hit_raises_user_attack_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = Trailblaze()

        with patch.object(battle_field, "calculate_damage", return_value=10):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(attacker.stat_modifiers["attack"], 1)
        self.assertEqual(defender.stat_modifiers["attack"], 0)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["stages"], 1)
        self.assertEqual(move.pp, 19)

    def test_attack_boost_respects_maximum_stage(self):
        user = Pokemon("Charizard")
        user.stat_modifiers["attack"] = 6

        effect = Trailblaze().effect(user, None)

        self.assertFalse(effect["applied"])
        self.assertEqual(user.stat_modifiers["attack"], 6)


if __name__ == "__main__":
    unittest.main()
