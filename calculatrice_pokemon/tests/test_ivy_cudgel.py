import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import IvyCudgel
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class IvyCudgelTests(unittest.TestCase):
    def test_move_metadata_and_no_secondary_effect(self):
        move = IvyCudgel()

        self.assertEqual(move.name, "Ivy Cudgel")
        self.assertEqual(move.type, Type.GRASS)
        self.assertEqual(move.category, MoveCategory.PHYSICAL)
        self.assertEqual(move.power, 100)
        self.assertEqual(move.accuracy, 100)
        self.assertEqual(move.max_pp, 10)
        self.assertFalse(move.contact)
        self.assertEqual(move.get_critical_hit_stage_bonus(None, None), 1)
        self.assertIsNone(move.effect(None, None))

    def test_high_critical_hit_rate_increases_critical_stage_by_one(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")

        with patch("field.random.random", return_value=0.05):
            normal_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                Tackle(),
            )
            ivy_cudgel_multiplier = battle_field.calculate_critical_hit_multiplier(
                attacker,
                defender,
                IvyCudgel(),
            )

        self.assertEqual(normal_multiplier, 1.0)
        self.assertEqual(ivy_cudgel_multiplier, 1.5)

    def test_type_changes_with_ogerpon_mask_form(self):
        move = IvyCudgel()
        form_types = (
            ("Wellspring Mask", Type.WATER),
            ("Hearthflame Mask", Type.FIRE),
            ("Cornerstone Mask", Type.ROCK),
        )

        for form, expected_type in form_types:
            with self.subTest(form=form):
                ogerpon = Pokemon("Ogerpon", form)
                self.assertEqual(move.get_type(ogerpon), expected_type)

        self.assertEqual(move.get_type(Pokemon("Charizard")), Type.GRASS)
        self.assertEqual(move.type, Type.GRASS)

    def test_mask_type_is_used_for_effectiveness_and_stab(self):
        battle_field = Field()
        ogerpon = Pokemon("Ogerpon", "Wellspring Mask")
        charizard = Pokemon("Charizard")
        move = IvyCudgel()

        self.assertEqual(
            battle_field.calculate_move_effectiveness(move, charizard, ogerpon),
            2.0,
        )
        self.assertEqual(battle_field.calculate_stab_multiplier(ogerpon, move), 1.5)

    def test_successful_hit_deals_damage_and_consumes_pp(self):
        battle_field = Field()
        attacker = Pokemon("Charizard")
        defender = Pokemon("Eevee")
        battle_field.add_pokemon(attacker, "player")
        battle_field.add_pokemon(defender, "opponent")
        move = IvyCudgel()

        with patch.object(battle_field, "calculate_damage", return_value=25):
            result = battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 25)
        self.assertEqual(defender.current_hp, defender.max_hp - 25)
        self.assertIsNone(result["effect"])
        self.assertEqual(move.pp, 9)


if __name__ == "__main__":
    unittest.main()
