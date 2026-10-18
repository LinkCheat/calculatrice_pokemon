try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ShellTrap(Moves):
    def __init__(self):
        """Create the Fire-type special move Shell Trap."""
        super().__init__(
            name="Shell Trap",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=150,
            accuracy=100,
            max_pp=5,
            priority=-3,
        )

    def is_counter_trap(self):
        return True

    def can_use_while_asleep(self):
        return True

    def fails_before_damage(self, user, target, field):
        """Fail if the user was not hit by a physical attack this turn."""
        return not user.shell_trap_triggered

    def effect(self, user, target):
        """Report whether the trap was triggered by a physical attack."""
        if not user.shell_trap_triggered:
            return {
                "name": self.name,
                "applied": False,
                "reason": "not_triggered",
                "failed": True,
            }
        return {
            "name": self.name,
            "applied": True,
            "condition": "shell_trap",
        }
