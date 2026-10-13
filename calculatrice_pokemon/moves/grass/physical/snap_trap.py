import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SnapTrap(Moves):
    def __init__(self):
        """Create the Grass-type physical contact move Snap Trap."""
        super().__init__(
            name="Snap Trap",
            move_type=Type.GRASS,
            category=MoveCategory.PHYSICAL,
            power=35,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Trap the target for four or five turns unless it has fainted."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "condition": "snap_trap",
                "applied": False,
                "reason": "target_fainted",
            }

        duration = random.randint(4, 5)
        target.snap_trap_turns_remaining = duration
        return {
            "name": self.name,
            "condition": "snap_trap",
            "applied": True,
            "turns": duration,
        }
