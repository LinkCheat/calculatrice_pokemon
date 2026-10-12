try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MegaDrain(Moves):
    def __init__(self):
        """Create the Grass-type special move Mega Drain."""
        super().__init__(
            name="Mega Drain",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=40,
            accuracy=100,
            max_pp=15,
        )

    def effect(self, user, target):
        """Apply healing using the actual damage dealt."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Restore half actual damage, except one damage restores one HP."""
        healing = damage_dealt if damage_dealt == 1 else damage_dealt // 2
        healing = min(healing, user.max_hp - user.current_hp)
        user.current_hp += healing
        return {
            "name": self.name,
            "healed": healing,
        }
