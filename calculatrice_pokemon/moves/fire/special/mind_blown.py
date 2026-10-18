try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MindBlown(Moves):
    def __init__(self):
        """Create the Fire-type special move Mind Blown."""
        super().__init__(
            name="Mind Blown",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=150,
            accuracy=100,
            max_pp=5,
        )

    def effect(self, user, target):
        """Mind Blown's user cost is handled with the attack result."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Remove half of the user's maximum HP, rounded up."""
        return self._inflict_user_cost(user)

    def apply_effect_on_failed_use(self, user, target):
        """Remove the user's HP even when the target avoids or blocks the move."""
        return self._inflict_user_cost(user)

    def _inflict_user_cost(self, user):
        cost = min((user.max_hp + 1) // 2, user.current_hp)
        user.current_hp -= cost
        return {
            "name": self.name,
            "recoil": cost,
        }
