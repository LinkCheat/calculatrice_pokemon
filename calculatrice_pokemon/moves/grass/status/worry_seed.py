try:
    from enums.ability import Ability
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.ability import Ability
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class WorrySeed(Moves):
    def __init__(self):
        """Create the Grass-type status move Worry Seed."""
        super().__init__(
            name="Worry Seed",
            move_type=Type.GRASS,
            category=MoveCategory.STATUS,
            accuracy=100,
            max_pp=10,
        )

    def effect(self, user, target):
        """Temporarily give the target Insomnia and wake it if it is asleep."""
        applied = target.set_temporary_ability(Ability.INSOMNIA)
        woke_up = target.status_condition is STATUS_CONDITION.SLEEP
        if woke_up:
            target.status_condition = None
            target.sleep_turns_remaining = 0

        return {
            "name": self.name,
            "ability": Ability.INSOMNIA,
            "applied": applied,
            "woke_up": woke_up,
        }
