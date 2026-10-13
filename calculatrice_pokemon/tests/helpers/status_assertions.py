def assert_status_applied(test_case, pokemon, effect, expected_status):
    test_case.assertIs(pokemon.status_condition, expected_status)
    test_case.assertIs(effect["status"], expected_status)
    test_case.assertTrue(effect["applied"])


def assert_status_unchanged(test_case, pokemon, effect, expected_status):
    test_case.assertFalse(effect["applied"])
    test_case.assertEqual(effect["reason"], "already_statused")
    test_case.assertIs(pokemon.status_condition, expected_status)
