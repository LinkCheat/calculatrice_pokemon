import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.terrain import Terrain
from enums.type import Type
from field import Field
from moves import GravApple
from pokemon import Pokemon


class GravAppleTests(unittest.TestCase):
    def test_move_metadata(self):
        move = GravApple()

        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 80)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 10)

    def test_successful_hit_lowers_target_defense_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = GravApple()

        with patch.object(battle_field, "calculate_damage", return_value=10):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(defender.stat_modifiers["defense"], -1)
        self.assertEqual(result["effect"]["stat"], "defense")
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(move.pp, 9)

    def test_defense_drop_respects_minimum_stage(self):
        target = Pokemon("Eevee")
        target.stat_modifiers["defense"] = -6

        effect = GravApple().effect(None, target)

        self.assertFalse(effect["applied"])
        self.assertEqual(target.stat_modifiers["defense"], -6)

    def test_power_increases_to_120_when_gravity_is_active(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = GravApple()

        self.assertEqual(move.get_power(attacker, defender, battle_field), 80)

        battle_field.gravity_active = True

        self.assertEqual(move.get_power(attacker, defender, battle_field), 120)

    def test_gravity_stacks_with_other_terrain(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        battle_field.terrain = Terrain.GRASSY
        battle_field.gravity_active = True

        self.assertEqual(GravApple().get_power(attacker, defender, battle_field), 120)

    def test_power_remains_80_without_gravity(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        battle_field.terrain = Terrain.GRASSY

        self.assertEqual(GravApple().get_power(attacker, defender, battle_field), 80)

    def test_damage_calculation_uses_gravity_power_bonus(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = GravApple()

        with patch.object(
            battle_field,
            "calculate_damage_modifiers",
            return_value=1.0,
        ):
            normal_damage = battle_field.calculate_damage(attacker, defender, move)
            battle_field.gravity_active = True
            gravity_damage = battle_field.calculate_damage(attacker, defender, move)

        self.assertGreater(gravity_damage, normal_damage)


if __name__ == "__main__":
    unittest.main()
