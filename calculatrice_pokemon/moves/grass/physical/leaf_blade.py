try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class LeafBlade(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Leaf Blade."""
        super().__init__(
            name="Leaf Blade",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=90,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Raise the critical-hit stage by one."""
        return 1

    def effect(self, user, target):
        """Leaf Blade has no secondary effect."""
        return None
