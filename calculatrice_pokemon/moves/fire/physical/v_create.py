try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class VCreate(Moves):
    STATS_TO_LOWER = ("defense", "sp_def", "speed")

    def __init__(self):
        """Create the Fire-type physical contact move V-create."""
        super().__init__(
            name="V-create",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=180,
            accuracy=95,
            max_pp=5,
            contact=True,
        )

    def effect(self, user, target):
        """Lower the user's Defense, Special Defense, and Speed by one stage."""
        stat_changes = []
        for stat in self.STATS_TO_LOWER:
            current_stage = user.stat_modifiers[stat]
            applied_stages = -min(1, current_stage + 6)
            user.stat_modifiers[stat] = current_stage + applied_stages
            stat_changes.append(
                {
                    "stat": stat,
                    "stages": applied_stages,
                    "applied": applied_stages != 0,
                    "recipient": "user",
                }
            )

        return {
            "name": self.name,
            "stat_changes": stat_changes,
        }
