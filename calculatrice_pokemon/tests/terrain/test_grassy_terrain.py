import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from enums.terrain import Terrain
from field import Field
from moves import GrassyGlide, Tackle
from pokemon import Pokemon
from tests.helpers.terrain_assertions import assert_grassy_terrain_active


class GrassyTerrainMechanicsTests(unittest.TestCase):
    def test_end_of_turn_heals_grounded_active_pokemon_and_expires_after_five_turns(self):
        battle_field = Field()
        user = Pokemon("Bulbasaur")
        opponent = Pokemon("Eevee")
        user.add_move(Tackle())
        opponent.add_move(Tackle())
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(opponent, "opponent")
        battle_field.terrain = Terrain.GRASSY
        battle_field.terrain_turns_remaining = 5
        user.current_hp -= 32
        opponent.current_hp -= 32

        with (
            patch.object(battle_field, "attack_hits", return_value=True),
            patch.object(battle_field, "calculate_damage", return_value=0),
        ):
            for remaining in range(4, -1, -1):
                battle_field.resolve_turn(0, 0)
                if remaining:
                    assert_grassy_terrain_active(self, battle_field, remaining)

        self.assertIsNone(battle_field.terrain)
        self.assertEqual(battle_field.terrain_turns_remaining, 0)
        self.assertEqual(user.current_hp, user.max_hp)
        self.assertEqual(opponent.current_hp, opponent.max_hp)

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
        battle_field = Field()
        user = Pokemon("Bulbasaur")
        opponent = Pokemon("Eevee")
        grass_move = GrassyGlide()
        battle_field.add_pokemon(user, "player")
        battle_field.add_pokemon(opponent, "opponent")
        battle_field.terrain = Terrain.GRASSY

        with patch.object(
            battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            terrain_modifiers = battle_field.calculate_damage_modifiers(
                user, opponent, grass_move
            )
            battle_field.terrain = None
            baseline_modifiers = battle_field.calculate_damage_modifiers(
                user, opponent, grass_move
            )

        self.assertAlmostEqual(terrain_modifiers / baseline_modifiers, 1.3)

    def test_grassy_terrain_does_not_boost_flying_attacker_without_gravity(self):
        battle_field = Field()
        flying_user = Pokemon("Charizard")
        opponent = Pokemon("Eevee")
        battle_field.add_pokemon(flying_user, "player")
        battle_field.add_pokemon(opponent, "opponent")
        battle_field.terrain = Terrain.GRASSY
        grass_move = GrassyGlide()

        with patch.object(
            battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            terrain_modifiers = battle_field.calculate_damage_modifiers(
                flying_user, opponent, grass_move
            )
            battle_field.terrain = None
            baseline_modifiers = battle_field.calculate_damage_modifiers(
                flying_user, opponent, grass_move
            )

        self.assertAlmostEqual(terrain_modifiers, baseline_modifiers)


if __name__ == "__main__":
    unittest.main()
