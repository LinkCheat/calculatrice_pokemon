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


class BurningBulwark(Moves):
    MINIMUM_PROTECTION_CHANCE = 1 / 729

    def __init__(self):
        """Create the Fire-type status move Burning Bulwark."""
        super().__init__(
            name="Burning Bulwark",
            move_type=Type.FIRE,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
            priority=4,
        )

    def is_protection_move(self):
        return True

    def get_protection_success_chance(self, protection_streak):
        """Divide successive success chances by three, with a 1/729 floor."""
        return max(
            1 / (3 ** protection_streak),
            self.MINIMUM_PROTECTION_CHANCE,
        )

    def apply_protection_contact_effect(self, attacker, protected_user, move):
        """Burn an eligible attacker whose direct move is blocked."""
        if Type.FIRE in attacker.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        if attacker.status_condition is not None:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "already_statused",
            }

        attacker.status_condition = STATUS_CONDITION.BURN
        return {
            "name": self.name,
            "status": STATUS_CONDITION.BURN,
            "applied": True,
        }

    def prevents_contact_recoil_on_protection(self):
        return True

    def effect(self, user, target):
        """Report that Burning Bulwark protected its user."""
        return {
            "name": self.name,
            "condition": "burning_bulwark",
            "applied": True,
        }
