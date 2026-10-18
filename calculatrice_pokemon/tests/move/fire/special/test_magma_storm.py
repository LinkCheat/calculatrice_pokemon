import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import MagmaStorm, Tackle
from pokemon import Pokemon


class MagmaStormTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Heatran")
        self.reserve = Pokemon("Eevee")
        self.target = Pokemon("Pikachu")
        self.target_reserve = Pokemon("Bulbasaur")
        self.move = MagmaStorm()
        self.user.add_move(self.move)
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.reserve, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.battle_field.add_pokemon(self.target_reserve, "opponent")
        self.user.stats["speed"] = 999
        self.target.stats["speed"] = 1

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Magma Storm")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 100)
        self.assertEqual(self.move.accuracy, 75)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_traps_target_and_deals_residual_damage(self):
        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch(
                "moves.fire.special.magma_storm.random.randint",
                return_value=4,
            ),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        self.assertEqual(self.target.magma_storm_turns_remaining, 3)
        self.assertIs(self.target.magma_storm_trapped_by, self.user)
        self.assertEqual(
            self.target.current_hp,
            self.target.max_hp - 10 - max(1, self.target.max_hp // 8),
        )
        effect = next(
            item["result"]["effect"]
            for item in results
            if item["action"]["side"] == "player"
        )
        self.assertTrue(effect["applied"])
        self.assertEqual(effect["turns"], 4)
        residual = next(
            item["result"]
            for item in results
            if item["action"]["type"] == "magma_storm_residual"
        )
        self.assertEqual(
            residual["damage"],
            max(1, self.target.max_hp // 8),
        )
        with self.assertRaisesRegex(ValueError, "piégé"):
            self.battle_field.switch_pokemon("opponent", 1)

    def test_duration_can_be_four_or_five_turns(self):
        with patch(
            "moves.fire.special.magma_storm.random.randint",
            side_effect=(4, 5),
        ):
            self.move.effect(self.user, self.target)
            self.assertEqual(self.target.magma_storm_turns_remaining, 4)
            self.move.effect(self.user, self.target)
            self.assertEqual(self.target.magma_storm_turns_remaining, 5)

    def test_ghost_target_is_not_trapped(self):
        ghost_target = Pokemon("Gengar")

        effect = self.move.effect(self.user, ghost_target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "ghost_immune")
        self.assertEqual(ghost_target.magma_storm_turns_remaining, 0)

    def test_fainted_target_is_not_trapped(self):
        self.target.current_hp = 0

        effect = self.move.effect(self.user, self.target)

        self.assertFalse(effect["applied"])
        self.assertEqual(effect["reason"], "target_fainted")
        self.assertEqual(self.target.magma_storm_turns_remaining, 0)

    def test_switching_out_as_trap_source_releases_target(self):
        self.target.magma_storm_turns_remaining = 3
        self.target.magma_storm_trapped_by = self.user

        self.battle_field.switch_pokemon("player", 1)

        self.assertEqual(self.target.magma_storm_turns_remaining, 0)
        self.assertIsNone(self.target.magma_storm_trapped_by)

    def test_trap_ends_after_four_turns(self):
        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "calculate_damage", return_value=1),
            patch(
                "moves.fire.special.magma_storm.random.randint",
                return_value=4,
            ),
        ):
            self.move.effect(self.user, self.target)
            for _ in range(4):
                self.battle_field._apply_magma_storm()

        self.assertEqual(self.target.magma_storm_turns_remaining, 0)
        self.assertIsNone(self.target.magma_storm_trapped_by)


if __name__ == "__main__":
    unittest.main()
