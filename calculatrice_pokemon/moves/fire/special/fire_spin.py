import random

try:
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class FireSpin(Moves):
    TRAP_MIN_TURNS = 4
    TRAP_MAX_TURNS = 5

    def __init__(self):
        """Create the Fire-type special move Fire Spin."""
        super().__init__(
            name="Fire Spin",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=35,
            accuracy=85,
            max_pp=15,
        )

    def effect(self, user, target):
        """Trap a living, non-Ghost target for four or five turns."""
        target_thawed = target.status_condition is STATUS_CONDITION.FREEZE
        if target_thawed:
            target.status_condition = None

        if target.current_hp <= 0:
            return {
                "name": self.name,
                "condition": "fire_spin",
                "applied": False,
                "reason": "target_fainted",
                "target_thawed": target_thawed,
            }
        if Type.GHOST in target.type:
            return {
                "name": self.name,
                "condition": "fire_spin",
                "applied": False,
                "reason": "ghost_immune",
                "target_thawed": target_thawed,
            }

        duration = random.randint(self.TRAP_MIN_TURNS, self.TRAP_MAX_TURNS)
        target.fire_spin_turns_remaining = duration
        return {
            "name": self.name,
            "condition": "fire_spin",
            "applied": True,
            "turns": duration,
            "target_thawed": target_thawed,
        }
