try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class IvyCudgel(Moves):
    MASK_TYPES = {
        "Wellspring Mask": Type.WATER,
        "Hearthflame Mask": Type.FIRE,
        "Cornerstone Mask": Type.ROCK,
    }

    def __init__(self):
        """Create the Grass-type physical move Ivy Cudgel."""
        super().__init__(
            name="Ivy Cudgel",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=100,
            accuracy=100,
            max_pp=10,
        )

    def get_type(self, user, target=None, field=None):
        """Use the Ogerpon mask form to determine Ivy Cudgel's type."""
        if user is None:
            return self.type
        return self.MASK_TYPES.get(user.form, self.type)

    def get_critical_hit_stage_bonus(self, user, target, field=None):
        """Raise the critical-hit stage by one for its high critical rate."""
        return 1

    def effect(self, user, target):
        """Ivy Cudgel has no secondary effect."""
        return None
