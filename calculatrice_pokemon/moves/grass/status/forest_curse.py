try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ForestCurse(Moves):
    def __init__(self):
        """Create the Grass-type status move Forest's Curse."""
        super().__init__(
            name="Forest's Curse",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=20,
        )

    def effect(self, user, target):
        """Add the Grass type to the target until it leaves the field."""
        if Type.GRASS in target.type:
            return {
                "name": self.name,
                "condition": "forest_curse",
                "applied": False,
                "reason": "already_grass_type",
            }

        target.type.append(Type.GRASS)
        target.forest_cursed = True
        return {
            "name": self.name,
            "condition": "forest_curse",
            "applied": True,
            "type": Type.GRASS,
        }
