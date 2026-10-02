try:
    from move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.move import Moves

try:
    from enums.type import Type
    from enums.move_category import MoveCategory
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.enums.move_category import MoveCategory


class Tackle(Moves):
    def __init__(self):
        """Create the Normal-type physical move Tackle (French name: Charge)."""
        super().__init__(
            name="Charge",
            move_type=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            max_pp=35,
        )

    def effect(self, user, target):
        """Return the move's effect metadata for the battle result."""
        return {
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "power": self.power,
            "target": target.name,
        }
