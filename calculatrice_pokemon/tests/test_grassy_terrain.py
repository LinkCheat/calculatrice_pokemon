import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.terrain import Terrain
from enums.type import Type
from field import Field
from moves import GrassyTerrain, GrassyGlide
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class GrassyTerrainTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = GrassyTerrain()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Grassy Terrain")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_move_sets_grassy_terrain_and_consumes_pp(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(result["effect"]["condition"], "grassy_terrain")
        self.assertIs(self.battle_field.terrain, Terrain.GRASSY)
        self.assertEqual(self.battle_field.terrain_turns_remaining, 5)
        self.assertEqual(self.move.pp, 9)

    def test_end_of_turn_heals_grounded_active_pokemon_and_expires_after_five_turns(self):
        self.battle_field.terrain = Terrain.GRASSY
        self.battle_field.terrain_turns_remaining = 5
        self.user.current_hp -= 32
        self.opponent.current_hp -= 32
        self.user.add_move(Tackle())
        self.opponent.add_move(Tackle())

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=0),
        ):
            for remaining in range(4, -1, -1):
                self.battle_field.resolve_turn(1, 0)
                self.assertEqual(self.battle_field.terrain_turns_remaining, remaining)
                if remaining:
                    self.assertIs(self.battle_field.terrain, Terrain.GRASSY)

        self.assertIsNone(self.battle_field.terrain)
        self.assertEqual(self.battle_field.terrain_turns_remaining, 0)
        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(self.opponent.current_hp, self.opponent.max_hp)

    def test_flying_pokemon_is_not_healed_unless_gravity_is_active(self):
        flying_pokemon = Pokemon("Charizard")
        grounded_pokemon = Pokemon("Pikachu")
        battle_field = Field()
        battle_field.add_pokemon(flying_pokemon, "player")
        battle_field.add_pokemon(grounded_pokemon, "opponent")
        battle_field.terrain = Terrain.GRASSY
        battle_field.terrain_turns_remaining = 5
        flying_pokemon.current_hp -= 32
        grounded_pokemon.current_hp -= 32

        battle_field._apply_grassy_terrain()
        self.assertEqual(flying_pokemon.current_hp, flying_pokemon.max_hp - 32)
        self.assertGreater(grounded_pokemon.current_hp, grounded_pokemon.max_hp - 32)

        battle_field.gravity_active = True
        battle_field._apply_grassy_terrain()
        self.assertGreater(flying_pokemon.current_hp, flying_pokemon.max_hp - 32)

    def test_grassy_terrain_boosts_grass_damage_for_grounded_attacker(self):
        self.battle_field.terrain = Terrain.GRASSY
        self.battle_field.terrain_turns_remaining = 5
        grass_move = GrassyGlide()

        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            normal_modifiers = self.battle_field.calculate_damage_modifiers(
                self.user, self.opponent, grass_move
            )
            self.battle_field.terrain = None
            baseline_modifiers = self.battle_field.calculate_damage_modifiers(
                self.user, self.opponent, grass_move
            )

        self.assertAlmostEqual(normal_modifiers / baseline_modifiers, 1.3)

    def test_grassy_terrain_does_not_boost_flying_attacker_without_gravity(self):
        flying_user = Pokemon("Charizard")
        self.battle_field.terrain = Terrain.GRASSY
        grass_move = GrassyGlide()

        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            terrain_modifiers = self.battle_field.calculate_damage_modifiers(
                flying_user, self.opponent, grass_move
            )
            self.battle_field.terrain = None
            baseline_modifiers = self.battle_field.calculate_damage_modifiers(
                flying_user, self.opponent, grass_move
            )

        self.assertAlmostEqual(terrain_modifiers, baseline_modifiers)


if __name__ == "__main__":
    unittest.main()
