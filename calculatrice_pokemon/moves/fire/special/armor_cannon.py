try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ArmorCannon(Moves):
    STATS_TO_LOWER = ("defense", "sp_def")

    def __init__(self):
        """Create the Fire-type special move Armor Cannon."""
        super().__init__(
            name="Armor Cannon",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=120,
            accuracy=100,
            max_pp=5,
        )

    def effect(self, user, target):
        """Lower the user's Defense and Special Defense by one stage."""
        changes = []
        for stat in self.STATS_TO_LOWER:
            current_stage = user.stat_modifiers[stat]
            applied_stages = -min(1, current_stage + 6)
            user.stat_modifiers[stat] += applied_stages
            changes.append(
                {
                    "stat": stat,
                    "stages": applied_stages,
                    "applied": applied_stages != 0,
                    "recipient": "user",
                }
            )

        return {
            "name": self.name,
            "stat_changes": changes,
        }
