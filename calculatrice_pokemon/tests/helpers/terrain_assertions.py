from enums.terrain import Terrain


def assert_grassy_terrain_active(test_case, battle_field, turns_remaining=5):
    test_case.assertIs(battle_field.terrain, Terrain.GRASSY)
    test_case.assertEqual(battle_field.terrain_turns_remaining, turns_remaining)
