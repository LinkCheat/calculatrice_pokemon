import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.terrain import Terrain
from enums.type import Type
from field import Field
from moves import Ingrain, Tackle
from moves.move import Moves
from pokemon import Pokemon


class GroundAttack(Moves):
    def __init__(self):
        super().__init__(
            name="Ground Attack",
            move_type=Type.GROUND,
            category=MoveCategory.PHYSICAL,
            power=50,
        )

    def effect(self, user, target):
        return None


class IngrainTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = Ingrain()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Ingrain")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_move_roots_user_and_consumes_pp(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["effect"]["condition"], "ingrain")
        self.assertTrue(self.user.ingrain_active)
        self.assertEqual(self.move.pp, 19)

    def test_ingrain_restores_one_sixteenth_max_hp_at_end_of_turn(self):
        self.user.ingrain_active = True
        self.user.current_hp -= self.user.max_hp // 4
        expected_healing = max(1, self.user.max_hp // 16)

        results = self.battle_field._apply_ingrain()

        self.assertEqual(
            self.user.current_hp,
            self.user.max_hp - self.user.max_hp // 4 + expected_healing,
        )
        self.assertEqual(results[0]["result"]["healed"], expected_healing)

    def test_ingrain_healing_is_capped_at_max_hp(self):
        self.user.ingrain_active = True
        self.user.current_hp = self.user.max_hp - 1

        results = self.battle_field._apply_ingrain()

        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(results[0]["result"]["healed"], 1)

    def test_turn_resolution_applies_ingrain_healing_after_the_move(self):
        self.opponent.add_move(Tackle())
        self.user.current_hp -= 32
        expected_healing = max(1, self.user.max_hp // 16)

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=0),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        residual = next(
            result
            for result in results
            if result["action"]["type"] == "ingrain_residual"
        )
        self.assertEqual(residual["result"]["healed"], expected_healing)
        self.assertEqual(self.user.current_hp, self.user.max_hp - 32 + expected_healing)

    def test_rooted_non_ghost_cannot_switch(self):
        reserve = Pokemon("Pikachu")
        self.battle_field.add_pokemon(reserve, "player")
        self.user.ingrain_active = True

        with self.assertRaisesRegex(ValueError, "enraciné"):
            self.battle_field.switch_pokemon("player", 1)
        with self.assertRaisesRegex(ValueError, "enraciné"):
            self.battle_field.determine_attack_order(
                self.battle_field.SWITCH_INDEX_OFFSET + 1,
                0,
            )

    def test_ghost_type_can_switch_while_rooted(self):
        ghost = Pokemon("Gengar")
        reserve = Pokemon("Pikachu")
        battle_field = Field()
        battle_field.add_pokemon(ghost, "player")
        battle_field.add_pokemon(reserve, "player")
        ghost.ingrain_active = True

        self.assertIn(Type.GHOST, ghost.type)
        self.assertIs(battle_field.switch_pokemon("player", 1), reserve)
        self.assertFalse(ghost.ingrain_active)

    def test_ingrain_grounds_flying_user_for_terrain_and_ground_attacks(self):
        flying_pokemon = Pokemon("Charizard")
        target = Pokemon("Eevee")
        battle_field = Field()
        battle_field.add_pokemon(flying_pokemon, "player")
        battle_field.add_pokemon(target, "opponent")
        ground_attack = GroundAttack()
        flying_pokemon.current_hp -= 32

        self.assertFalse(battle_field._is_grounded(flying_pokemon))
        self.assertEqual(
            battle_field.calculate_move_effectiveness(ground_attack, flying_pokemon),
            0,
        )

        flying_pokemon.ingrain_active = True
        self.assertTrue(battle_field._is_grounded(flying_pokemon))
        self.assertEqual(
            battle_field.calculate_move_effectiveness(ground_attack, flying_pokemon),
            2.0,
        )

        battle_field.terrain = Terrain.GRASSY
        battle_field.terrain_turns_remaining = 5
        battle_field._apply_grassy_terrain()
        self.assertGreater(flying_pokemon.current_hp, flying_pokemon.max_hp - 32)


if __name__ == "__main__":
    unittest.main()
