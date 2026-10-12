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


class GrassyTerrain(Moves):
    DURATION = 5

    def __init__(self):
        """Create the Grass-type status move Grassy Terrain."""
        super().__init__(
            name="Grassy Terrain",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
        )

    def effect(self, user, target):
        """Grassy Terrain is applied to the field by the battle resolver."""
        return None

    def applies_field_effect(self):
        return True

    def apply_field_effect(self, user, field):
        """Set or refresh Grassy Terrain for five end-of-turn ticks."""
        field.terrain = Terrain.GRASSY
        field.terrain_turns_remaining = self.DURATION
        return {
            "condition": "grassy_terrain",
            "applied": True,
            "turns": self.DURATION,
        }
