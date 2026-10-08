try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class GigaDrain(Moves):
    def __init__(self):
        """Create the Grass-type special move Giga Drain."""
        super().__init__(
            name="Giga Drain",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=75,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Apply healing using the damage context supplied by the field."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Restore half the actual damage dealt, capped at the user's max HP."""
        healing = min(damage_dealt // 2, user.max_hp - user.current_hp)
        user.current_hp += healing
        return {
            "name": self.name,
            "healed": healing,
        }
