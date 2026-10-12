try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class JungleHealing(Moves):
    def __init__(self):
        """Create the Grass-type status move Jungle Healing."""
        super().__init__(
            name="Jungle Healing",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
        )

    def effect(self, user, target):
        """Restore one quarter max HP and cure the user's major status."""
        healing = min(user.max_hp // 4, user.max_hp - user.current_hp)
        user.current_hp += healing

        cured_status = user.status_condition
        if cured_status is not None:
            user.status_condition = None
            user.sleep_turns_remaining = 0

        return {
            "condition": "jungle_healing",
            "healed": healing,
            "cured": cured_status is not None,
            "status": cured_status,
        }
