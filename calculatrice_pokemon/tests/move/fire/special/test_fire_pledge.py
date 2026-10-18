import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import FirePledge
from pokemon import Pokemon


class FirePledgeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = FirePledge()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata_and_no_individual_secondary_effect(self):
        self.assertEqual(self.move.name, "Fire Pledge")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 80)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)
        self.assertIsNone(self.move.effect(None, None))

    def test_successful_hit_deals_damage_and_consumes_one_pp(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 20)
        self.assertIsNone(result["effect"])
        self.assertEqual(self.move.pp, 9)

    def test_miss_does_not_deal_damage(self):
        starting_hp = self.defender.current_hp

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.defender.current_hp, starting_hp)


if __name__ == "__main__":
    unittest.main()
