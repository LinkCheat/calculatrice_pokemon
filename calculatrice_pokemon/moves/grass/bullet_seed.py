import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BulletSeed(Moves):
    def __init__(self):
        """Create the Grass-type physical move Bullet Seed."""
        super().__init__(
            name="Bullet Seed",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=25,
            accuracy=100,
            max_pp=30,
        )

    def get_hit_count(self, user, target):
        """Choose between two and five strikes using Bullet Seed's odds."""
        return random.choices((2, 3, 4, 5), weights=(35, 35, 15, 15), k=1)[0]

    def effect(self, user, target):
        """Bullet Seed has no secondary effect."""
        return None
