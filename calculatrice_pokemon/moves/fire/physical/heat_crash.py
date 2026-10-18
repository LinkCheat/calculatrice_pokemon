try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class HeatCrash(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Heat Crash."""
        super().__init__(
            name="Heat Crash",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=0,
            accuracy=100,
            max_pp=10,
            contact=True,
        )

    def get_power(self, user, target, field=None):
        """Return power based on the target's weight relative to the user."""
        target_weight = target.weight
        user_weight = user.weight
        if target_weight * 5 <= user_weight:
            return 120
        if target_weight * 4 <= user_weight:
            return 100
        if target_weight * 3 <= user_weight:
            return 80
        if target_weight * 2 <= user_weight:
            return 60
        return 40

    def effect(self, user, target):
        """Heat Crash has no secondary effect."""
        return None
