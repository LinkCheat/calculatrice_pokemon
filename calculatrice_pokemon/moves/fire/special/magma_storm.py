import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MagmaStorm(Moves):
    TRAP_MIN_TURNS = 4
    TRAP_MAX_TURNS = 5

    def __init__(self):
        """Create the Fire-type special move Magma Storm."""
        super().__init__(
            name="Magma Storm",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=100,
            accuracy=75,
            max_pp=5,
        )

    def effect(self, user, target):
        """Trap a living, non-Ghost target for four or five turns."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "condition": "magma_storm",
                "applied": False,
                "reason": "target_fainted",
            }
        if Type.GHOST in target.type:
            return {
                "name": self.name,
                "condition": "magma_storm",
                "applied": False,
                "reason": "ghost_immune",
            }

        duration = random.randint(self.TRAP_MIN_TURNS, self.TRAP_MAX_TURNS)
        target.magma_storm_turns_remaining = duration
        target.magma_storm_trapped_by = user
        return {
            "name": self.name,
            "condition": "magma_storm",
            "applied": True,
            "turns": duration,
        }
