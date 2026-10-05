import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import VineWhip
from pokemon import Pokemon


class VineWhipTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = VineWhip()

        self.assertEqual(move.name, "Vine Whip")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 45)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 25)
        self.assertTrue(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_successful_hit_deals_damage_without_secondary_effect(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = VineWhip()

        with patch.object(battle_field, "calculate_damage", return_value=15):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 15)
        self.assertEqual(defender.current_hp, defender.max_hp - 15)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 24)


if __name__ == "__main__":
    unittest.main()
