try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Aromatherapy(Moves):
    def __init__(self):
        """Create the Grass-type status move Aromatherapy."""
        super().__init__(
            name="Aromatherapy",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=5,
        )

    def effect(self, user, target):
        """Aromatherapy is applied to the user's full team by the field."""
        return None

    def targets_user_team(self):
        return True

    def apply_team_effect(self, user, team):
        """Cure major status conditions for every Pokémon on the user's team."""
        cured = []
        for pokemon in team:
            if pokemon.status_condition is not None:
                pokemon.status_condition = None
                pokemon.sleep_turns_remaining = 0
                cured.append(pokemon.name)

        return {
            "condition": "aromatherapy",
            "cured": cured,
        }
