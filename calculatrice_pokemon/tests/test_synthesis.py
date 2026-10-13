import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.move_category import MoveCategory
from enums.type import Type
from enums.weather import Weather
from field import Field
from moves import Synthesis
from pokemon import Pokemon


class SynthesisTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.target = Pokemon("Eevee")
        self.move = Synthesis()
        self.user.add_move(self.move)
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.target, "opponent")
        self.user.current_hp -= self.user.max_hp

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Synthesis")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_restores_half_max_hp_without_weather(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], self.user.max_hp // 2)
        self.assertEqual(self.user.current_hp, self.user.max_hp // 2)
        self.assertEqual(self.move.pp, 4)

    def test_sunny_weather_restores_two_thirds_max_hp(self):
        for weather in (Weather.SUNNY, Weather.DESOLATE_LAND):
            with self.subTest(weather=weather):
                self.user.current_hp = 0
                self.battle_field.weather = weather

                result = self.battle_field.resolve_move("player", self.move)

                expected_healing = self.user.max_hp * 2 // 3
                self.assertEqual(result["effect"]["healed"], expected_healing)
                self.assertEqual(self.user.current_hp, expected_healing)

    def test_other_weather_restores_one_quarter_max_hp(self):
        for weather in (
            Weather.RAINY,
            Weather.SANDSTORM,
            Weather.SNOW,
            Weather.PRIMORDIAL_SEA,
            Weather.DELTA_STREAM,
        ):
            with self.subTest(weather=weather):
                self.user.current_hp = 0
                self.battle_field.weather = weather

                result = self.battle_field.resolve_move("player", self.move)

                expected_healing = self.user.max_hp // 4
                self.assertEqual(result["effect"]["healed"], expected_healing)
                self.assertEqual(self.user.current_hp, expected_healing)

    def test_healing_is_capped_at_missing_hp(self):
        self.user.current_hp = self.user.max_hp - 1

        result = self.move.effect(self.user, self.target)

        self.assertEqual(result["healed"], 1)
        self.assertEqual(self.user.current_hp, self.user.max_hp)


if __name__ == "__main__":
    unittest.main()
