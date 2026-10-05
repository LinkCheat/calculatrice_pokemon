import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import PowerWhip
from pokemon import Pokemon


class PowerWhipTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = PowerWhip()

        self.assertEqual(move.name, "Power Whip")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 120)
        self.assertEqual(move.accuracy, 85)
        self.assertEqual(move.max_pp, 10)
        self.assertTrue(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_successful_hit_deals_damage_and_consumes_one_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = PowerWhip()

        with (
            patch.object(battle_field, "attack_hits", return_value=True),
            patch.object(battle_field, "calculate_damage", return_value=20),
        ):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(defender.current_hp, defender.max_hp - 20)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 9)

    def test_miss_consumes_one_pp_without_dealing_damage(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = PowerWhip()

        with patch.object(battle_field, "attack_hits", return_value=False):
            result = battle_field.resolve_move("player", move)

        self.assertFalse(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(defender.current_hp, defender.max_hp)
        self.assertEqual(move.pp, 9)


if __name__ == "__main__":
    unittest.main()
