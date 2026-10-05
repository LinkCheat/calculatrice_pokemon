import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import BranchPoke
from pokemon import Pokemon


class BranchPokeTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = BranchPoke()

        self.assertEqual(move.name, "Branch Poke")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 40)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 40)
        self.assertTrue(move.contact)
        self.assertIsNone(move.effect(None, None))

    def test_successful_hit_deals_damage_and_consumes_one_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = BranchPoke()

        with (
            patch.object(battle_field, "attack_hits", return_value=True),
            patch.object(battle_field, "calculate_damage", return_value=12),
        ):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 12)
        self.assertEqual(defender.current_hp, defender.max_hp - 12)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 39)


if __name__ == "__main__":
    unittest.main()
