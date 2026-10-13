try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class RazorLeaf(Moves):
    def __init__(self):
        """Create the Grass-type physical move Razor Leaf."""
        super().__init__(
            name="Razor Leaf",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=55,
            accuracy=95,
            max_pp=25,
        )

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Raise the critical-hit stage by one for its high critical rate."""
        return 1

    def effect(self, user, target):
        """Razor Leaf has no secondary effect."""
        return None
