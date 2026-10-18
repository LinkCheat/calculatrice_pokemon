try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BitterBlade(Moves):
    def __init__(self):
        """Create the Fire-type physical contact move Bitter Blade."""
        super().__init__(
            name="Bitter Blade",
            move_type=Type.FIRE,
            category=MoveCategory.PHYSICAL,
            power=90,
            accuracy=100,
            max_pp=10,
            contact=True,
        )

    def effect(self, user, target):
        """Bitter Blade's healing effect uses its actual damage context."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Restore half the actual damage dealt, capped at the user's max HP."""
        healing = min(damage_dealt // 2, user.max_hp - user.current_hp)
        user.current_hp += healing
        return {
            "name": self.name,
            "healed": healing,
        }
