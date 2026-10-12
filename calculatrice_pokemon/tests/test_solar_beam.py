import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.weather import Weather
from enums.type import Type
from field import Field
from moves import SolarBeam, Tackle
from pokemon import Pokemon


class SolarBeamTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.user.add_move(SolarBeam())
        self.target.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.move = self.user.moves[0]

    def test_move_metadata_and_no_secondary_effect(self):
        self.assertEqual(self.move.name, "Solar Beam")
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)
        self.assertIsNone(self.move.effect(None, None))

    def test_sunny_weather_skips_charge_and_deals_full_power_damage(self):
        self.battle_field.weather = Weather.SUNNY

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result.get("charging", False))
        self.assertEqual(result["damage"], 20)
        self.assertEqual(self.move.pp, 9)
        self.assertIsNone(self.user.charging_move)

    def test_extremely_sunny_weather_skips_charge(self):
        self.battle_field.weather = Weather.DESOLATE_LAND

        self.assertFalse(self.move.requires_charge(self.battle_field))
        self.assertEqual(
            self.move.get_power(self.user, self.target, self.battle_field),
            120,
        )

    def test_rain_sandstorm_and_snow_halve_power_but_still_require_charge(self):
        for weather in (Weather.RAINY, Weather.SANDSTORM, Weather.SNOW):
            with self.subTest(weather=weather):
                self.battle_field.weather = weather
                self.assertTrue(self.move.requires_charge(self.battle_field))
                self.assertEqual(
                    self.move.get_power(self.user, self.target, self.battle_field),
                    60,
                )

    def test_normal_weather_charges_then_attacks_and_consumes_pp_once(self):
        self.user.stats["speed"] = 999
        self.target.stats["speed"] = 1

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch.object(self.battle_field, "attack_hits", return_value=True),
        ):
            first_turn = self.battle_field.resolve_turn(0, 0)
            self.assertTrue(self.user.charging_move is self.move)
            self.assertEqual(self.target.current_hp, self.target.max_hp)
            self.assertEqual(self.move.pp, 9)

            second_turn = self.battle_field.resolve_turn(0, 0)

        solar_result = next(
            result["result"]
            for result in second_turn
            if result["action"]["side"] == "player"
        )
        self.assertTrue(first_turn[0]["result"]["charging"])
        self.assertEqual(solar_result["damage"], 10)
        self.assertEqual(self.target.current_hp, self.target.max_hp - 10)
        self.assertEqual(self.move.pp, 9)
        self.assertIsNone(self.user.charging_move)

    def test_solar_beam_power_is_halved_in_adverse_weather_after_charge(self):
        self.battle_field.weather = Weather.RAINY
        self.assertEqual(
            self.move.get_power(self.user, self.target, self.battle_field),
            60,
        )

    def test_adverse_weather_reduces_damage_after_charge(self):
        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            full_power_damage = self.battle_field.calculate_damage(
                self.user,
                self.target,
                self.move,
            )
            self.battle_field.weather = Weather.RAINY
            reduced_power_damage = self.battle_field.calculate_damage(
                self.user,
                self.target,
                self.move,
            )

        self.assertLess(reduced_power_damage, full_power_damage)

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(
                self.battle_field,
                "calculate_critical_hit_multiplier",
                return_value=1.0,
            ),
        ):
            charge_result = self.battle_field.resolve_move("player", self.move)
            damage_result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(charge_result["charging"])
        self.assertEqual(damage_result["damage"], reduced_power_damage)
        self.assertEqual(self.move.pp, 9)


if __name__ == "__main__":
    unittest.main()
