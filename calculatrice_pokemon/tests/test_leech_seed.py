import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import LeechSeed
from pokemon import Pokemon
from moves.normal.tackle import Tackle


class LeechSeedTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.user_bench = Pokemon("Pikachu")
        self.target = Pokemon("Eevee")
        self.target_bench = Pokemon("Charizard")
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.user_bench, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.battle_field.add_pokemon(self.target_bench, "opponent")
        self.move = LeechSeed()

    def test_move_metadata(self):
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 90)
        self.assertEqual(self.move.max_pp, 10)

    def test_successful_hit_seeds_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertTrue(result["effect"]["applied"])
        self.assertTrue(self.target.leech_seeded)
        self.assertEqual(self.target.current_hp, self.target.max_hp)
        self.assertEqual(self.move.pp, 9)

    def test_grass_type_is_immune(self):
        grass_target = Pokemon("Bulbasaur")
        self.battle_field.add_pokemon(grass_target, "opponent")
        self.battle_field.switch_pokemon("opponent", 2)

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["immune"])
        self.assertFalse(grass_target.leech_seeded)

    def test_seed_drain_heals_current_active_on_seeders_side(self):
        self.target.leech_seeded = True
        self.target.current_hp = 80
        self.user.current_hp = self.user.max_hp - 30
        self.battle_field.switch_pokemon("player", 1)
        self.user_bench.current_hp = self.user_bench.max_hp - 2

        residual = self.battle_field._apply_leech_seed()

        drained = self.target.max_hp // 8
        self.assertEqual(self.target.current_hp, 80 - drained)
        self.assertEqual(self.user.current_hp, self.user.max_hp - 30)
        self.assertEqual(self.user_bench.current_hp, self.user_bench.max_hp)
        self.assertEqual(residual[0]["result"]["healed"], 2)

    def test_drain_is_at_least_one_and_heal_is_capped_at_max_hp(self):
        self.target.stats["hp"] = 15
        self.target.current_hp = 5
        self.user.current_hp = self.user.max_hp - 1
        self.target.leech_seeded = True

        residual = self.battle_field._apply_leech_seed()

        self.assertEqual(residual[0]["result"]["drained"], 1)
        self.assertEqual(self.target.current_hp, 4)
        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(residual[0]["result"]["healed"], 1)

    def test_switching_seeded_target_removes_effect(self):
        self.target.leech_seeded = True

        self.battle_field.switch_pokemon("opponent", 1)
        residual = self.battle_field._apply_leech_seed()

        self.assertFalse(self.target.leech_seeded)
        self.assertEqual(residual, [])

    def test_residual_is_applied_at_the_end_of_a_resolved_turn(self):
        self.user.add_move(Tackle())
        self.target.add_move(Tackle())
        self.target.leech_seeded = True
        drain = self.target.max_hp // 8

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=1),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        self.assertEqual(self.target.current_hp, self.target.max_hp - 1 - drain)
        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(results[-1]["action"]["type"], "leech_seed_residual")
        self.assertEqual(results[-1]["result"]["drained"], drain)


if __name__ == "__main__":
    unittest.main()
