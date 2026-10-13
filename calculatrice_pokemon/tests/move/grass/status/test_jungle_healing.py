import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import JungleHealing, Tackle
from pokemon import Pokemon


class JungleHealingTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.user = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.move = JungleHealing()
        self.user.add_move(self.move)
        self.opponent.add_move(Tackle())
        self.battle_field.add_pokemon(self.user, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Jungle Healing")
        self.assertIs(self.move.type, Type.GRASS)
        self.assertIs(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_heals_quarter_max_hp_and_cures_status(self):
        self.user.current_hp -= self.user.max_hp // 2
        self.user.status_condition = STATUS_CONDITION.POISON

        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertFalse(result["immune"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(result["effect"]["healed"], self.user.max_hp // 4)
        self.assertTrue(result["effect"]["cured"])
        self.assertIs(result["effect"]["status"], STATUS_CONDITION.POISON)
        self.assertIsNone(self.user.status_condition)
        self.assertEqual(self.move.pp, 9)

    def test_effect_cures_sleep_and_resets_sleep_counter(self):
        self.user.status_condition = STATUS_CONDITION.SLEEP
        self.user.sleep_turns_remaining = 2

        result = self.move.effect(self.user, self.opponent)

        self.assertTrue(result["cured"])
        self.assertIs(result["status"], STATUS_CONDITION.SLEEP)
        self.assertIsNone(self.user.status_condition)
        self.assertEqual(self.user.sleep_turns_remaining, 0)

    def test_healing_is_capped_at_max_hp_and_still_cures_status(self):
        self.user.current_hp = self.user.max_hp - 1
        self.user.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.user, self.opponent)

        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(result["healed"], 1)
        self.assertTrue(result["cured"])
        self.assertIsNone(self.user.status_condition)

    def test_full_health_user_still_has_status_cured(self):
        self.user.status_condition = STATUS_CONDITION.BURN

        result = self.move.effect(self.user, self.opponent)

        self.assertEqual(self.user.current_hp, self.user.max_hp)
        self.assertEqual(result["healed"], 0)
        self.assertTrue(result["cured"])
        self.assertIsNone(self.user.status_condition)

    def test_move_heals_without_status_condition(self):
        self.user.current_hp -= 20

        result = self.move.effect(self.user, self.opponent)

        self.assertEqual(result["healed"], 20)
        self.assertFalse(result["cured"])
        self.assertIsNone(result["status"])
        self.assertIsNone(self.user.status_condition)


if __name__ == "__main__":
    unittest.main()
