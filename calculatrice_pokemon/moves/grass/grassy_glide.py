try:
    from enums.move_category import MoveCategory
    from enums.terrain import Terrain
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.terrain import Terrain
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class GrassyGlide(Moves):
    def __init__(self):
        """Create the Grass-type physical move Grassy Glide."""
        super().__init__(
            name="Grassy Glide",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=55,
            accuracy=100,
            max_pp=20,
            contact=True,
        )

    def get_priority(self, user, target, field=None):
        """Raise priority by one while Grassy Terrain is active."""
        priority = super().get_priority(user, target, field)
        if field is not None and field.terrain is Terrain.GRASSY:
            return priority + 1
        return priority

    def effect(self, user, target):
        """Grassy Glide has no secondary effect."""
        return None
