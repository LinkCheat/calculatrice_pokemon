try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Chloroblast(Moves):
    def __init__(self):
        """Create the Grass-type special move Chloroblast."""
        super().__init__(
            name="Chloroblast",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=150,
            accuracy=95,
            max_pp=5,
        )

    def effect(self, user, target):
        """Apply recoil based on the user's maximum HP after dealing damage."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Remove half the user's maximum HP, fainting them if necessary."""
        recoil = min(user.max_hp // 2, user.current_hp)
        user.current_hp -= recoil
        return {
            "name": self.name,
            "recoil": recoil,
        }
