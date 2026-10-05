import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import DrumBeating
from pokemon import Pokemon


class DrumBeatingTests(unittest.TestCase):
    def test_move_metadata(self):
        move = DrumBeating()

        self.assertEqual(move.name, "Drum Beating")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 80)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 10)
        self.assertFalse(move.contact)

    def test_successful_hit_lowers_target_speed_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = DrumBeating()

        with patch.object(battle_field, "calculate_damage", return_value=10):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(defender.stat_modifiers["speed"], -1)
        self.assertEqual(result["effect"]["stat"], "speed")
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(move.pp, 9)

    def test_speed_drop_respects_minimum_stage(self):
        target = Pokemon("Eevee")
        target.stat_modifiers["speed"] = -6

        effect = DrumBeating().effect(None, target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["stages"], 0)
        self.assertEqual(target.stat_modifiers["speed"], -6)


if __name__ == "__main__":
    unittest.main()
