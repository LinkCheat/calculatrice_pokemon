import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from enums.weather import Weather
from field import Field
from moves import SunnyDay, Tackle
from pokemon import Pokemon


class SunnyDayTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Charizard")
        self.target = Pokemon("Eevee")
        self.move = SunnyDay()
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Sunny Day")
        self.assertIs(self.move.type, Type.FIRE)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_move_sets_sunny_weather_and_consumes_pp(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(result["effect"]["condition"], "sunny_day")
        self.assertIs(self.battle_field.weather, Weather.SUNNY)
        self.assertEqual(self.battle_field.weather_turns_remaining, 5)
        self.assertEqual(self.move.pp, 4)

    def test_sunny_day_replaces_other_weather(self):
        self.battle_field.weather = Weather.RAINY
        self.battle_field.weather_turns_remaining = 2

        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["turns"], 5)
        self.assertIs(self.battle_field.weather, Weather.SUNNY)
        self.assertEqual(self.battle_field.weather_turns_remaining, 5)

    def test_sunny_day_refreshes_existing_sunny_weather(self):
        self.battle_field.weather = Weather.SUNNY
        self.battle_field.weather_turns_remaining = 1

        self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.battle_field.weather_turns_remaining, 5)

    def test_sunny_weather_increases_fire_damage_and_reduces_water_damage(self):
        self.battle_field.weather = Weather.SUNNY
        neutral_user = Pokemon("Eevee")
        water_attack = Tackle()
        water_attack.type = Type.WATER
        fire_attack = Tackle()
        fire_attack.type = Type.FIRE

        fire_multiplier = self.battle_field.calculate_damage_modifiers(
            neutral_user,
            self.target,
            fire_attack,
        )
        water_multiplier = self.battle_field.calculate_damage_modifiers(
            neutral_user,
            self.target,
            water_attack,
        )

        self.assertEqual(fire_multiplier, 1.5)
        self.assertEqual(water_multiplier, 0.5)

    def test_temporary_weather_expires_after_five_end_of_turn_ticks(self):
        self.battle_field.weather = Weather.SUNNY
        self.battle_field.weather_turns_remaining = SunnyDay.DURATION

        for remaining in (4, 3, 2, 1, 0):
            results = self.battle_field._apply_weather()
            if remaining:
                self.assertIs(self.battle_field.weather, Weather.SUNNY)
                self.assertEqual(self.battle_field.weather_turns_remaining, remaining)
            else:
                self.assertIsNone(self.battle_field.weather)
                self.assertEqual(self.battle_field.weather_turns_remaining, 0)
                self.assertTrue(results[0]["result"]["ended"])

    def test_weather_is_unchanged_when_sunny_day_misses(self):
        self.battle_field.weather = Weather.RAINY
        self.battle_field.weather_turns_remaining = 3

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIs(self.battle_field.weather, Weather.RAINY)
        self.assertEqual(self.battle_field.weather_turns_remaining, 3)


if __name__ == "__main__":
    unittest.main()
