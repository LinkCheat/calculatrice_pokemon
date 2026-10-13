try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class SyrupBomb(Moves):
    def __init__(self):
        """Create the Grass-type special move Syrup Bomb."""
        super().__init__(
            name="Syrup Bomb",
            move_type=Type.GRASS,
            category=MoveCategory.SPECIAL,
            power=65,
            accuracy=85,
            max_pp=10,
        )

    def effect(self, user, target):
        """Make a living target lose one Speed stage for each of three turns."""
        if target.current_hp <= 0:
            return {
                "name": self.name,
                "condition": "syrupy",
                "applied": False,
                "reason": "target_fainted",
            }

        target.syrupy_turns_remaining = 3
        target.syrupy_skip_next_tick = True
        return {
            "name": self.name,
            "condition": "syrupy",
            "applied": True,
            "turns": 3,
        }
