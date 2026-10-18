try:
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FusionFlare(Moves):
    def __init__(self):
        """Create the Fire-type special move Fusion Flare."""
        super().__init__(
            name="Fusion Flare",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=100,
            accuracy=100,
            max_pp=5,
        )

    def get_power(self, user, target, field=None):
        """Double power when Fusion Bolt was the immediately preceding move."""
        if field is not None and field.last_move_used == "Fusion Bolt":
            return self.power * 2
        return self.power

    def effect(self, user, target):
        """Thaw the user and target if either is frozen."""
        user_thawed = user.status_condition is STATUS_CONDITION.FREEZE
        target_thawed = target.status_condition is STATUS_CONDITION.FREEZE
        if user_thawed:
            user.status_condition = None
        if target_thawed:
            target.status_condition = None

        if not user_thawed and not target_thawed:
            return None

        return {
            "name": self.name,
            "user_thawed": user_thawed,
            "target_thawed": target_thawed,
        }
