try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FlowerTrick(Moves):
    def __init__(self):
        """Create the Grass-type physical move Flower Trick."""
        super().__init__(
            name="Flower Trick",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=70,
            accuracy=101,
            max_pp=10,
        )

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Set the critical-hit stage to four, guaranteeing a critical hit."""
        return 3

    def effect(self, user, target):
        """Flower Trick has no secondary effect."""
        return None
