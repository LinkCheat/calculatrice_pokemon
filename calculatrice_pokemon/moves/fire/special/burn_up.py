try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BurnUp(Moves):
    def __init__(self):
        """Create the Fire-type special move Burn Up."""
        super().__init__(
            name="Burn Up",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=130,
            accuracy=100,
            max_pp=5,
        )

    def fails_before_damage(self, user, target, field):
        """Burn Up fails if its user no longer has the Fire type."""
        return Type.FIRE not in user.type

    def effect(self, user, target):
        """Remove the user's Fire type after Burn Up is used."""
        if Type.FIRE not in user.type:
            return {
                "name": self.name,
                "applied": False,
                "reason": "no_fire_type",
                "failed": True,
            }
        return self._remove_fire_type(user)

    def apply_effect_on_failed_use(self, user, target):
        """Remove the user's Fire type when a use misses or is blocked."""
        return self.effect(user, target)

    def _remove_fire_type(self, user):
        if user.burn_up_original_types is None:
            user.burn_up_original_types = list(user.type)

        user.type.remove(Type.FIRE)
        if not user.type:
            user.type.append(Type.NONE)

        return {
            "name": self.name,
            "condition": "burn_up",
            "applied": True,
            "type": Type.FIRE,
        }
