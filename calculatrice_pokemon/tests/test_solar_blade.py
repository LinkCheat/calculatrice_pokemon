import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.weather import Weather
from enums.type import Type
from field import Field
from moves import SolarBlade
from moves.normal.tackle import Tackle
from pokemon import Pokemon


class SolarBladeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.move = SolarBlade()

    def test_move_metadata(self):
        self.assertEqual(self.move.type, Type.GRASS)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 125)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_normal_weather_charges_then_forces_solar_blade_next_turn(self):
        self.user.add_move(self.move)
        self.user.add_move(Tackle())
        self.target.add_move(Tackle())
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

            second_turn = self.battle_field.resolve_turn(1, 0)

        solar_result = next(
            item["result"]
            for item in second_turn
            if item["action"]["side"] == "player"
        )
        self.assertEqual(solar_result["damage"], 10)
        self.assertFalse(solar_result.get("charging", False))
        self.assertEqual(self.target.current_hp, self.target.max_hp - 10)
        self.assertEqual(self.move.pp, 9)
        self.assertIsNone(self.user.charging_move)

    def test_sunny_and_extremely_sunny_weather_skip_charge(self):
        for weather in (Weather.SUNNY, Weather.DESOLATE_LAND):
            with self.subTest(weather=weather):
                self.battle_field.weather = weather
                with (
                    patch.object(self.battle_field, "calculate_damage", return_value=10),
                    patch.object(self.battle_field, "attack_hits", return_value=True),
                ):
                    result = self.battle_field.resolve_move("player", self.move)

                self.assertEqual(result["damage"], 10)
                self.assertFalse(result.get("charging", False))
                self.assertEqual(self.move.pp, 9)
                self.assertIsNone(self.user.charging_move)
                self.move.pp = self.move.max_pp

    def test_switching_cancels_charge(self):
        self.user.add_move(self.move)
        reserve = Pokemon("Pikachu")
        self.battle_field.add_pokemon(reserve, "player")

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)
        self.assertTrue(result["charging"])

        self.battle_field.switch_pokemon("player", 1)

        self.assertIsNone(self.user.charging_move)


if __name__ == "__main__":
    unittest.main()
