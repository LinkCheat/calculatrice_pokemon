try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class WoodHammer(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Wood Hammer."""
        super().__init__(
            name="Wood Hammer",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=100,
            max_pp=5,
            contact=True,
        )

    def effect(self, user, target):
        """Wood Hammer's recoil is applied using the actual damage dealt."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Inflict recoil equal to one third of the damage actually dealt."""
        recoil = min(damage_dealt // 3, user.current_hp)
        user.current_hp -= recoil
        return {
            "name": self.name,
            "recoil": recoil,
        }
