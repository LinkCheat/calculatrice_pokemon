try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Incinerate(Moves):
    def __init__(self):
        """Create the Fire-type special move Incinerate."""
        super().__init__(
            name="Incinerate",
            move_type=Type.FIRE,
            category=MoveCategory.SPECIAL,
            power=60,
            accuracy=100,
            max_pp=15,
        )

    def effect(self, user, target):
        """Destroy the target's held Berry or Gem, if it has one."""
        held_item = target.item
        item_name = self._get_item_name(held_item)
        normalized_name = item_name.replace("_", " ").replace("-", " ").lower()
        item_destroyed = (
            held_item is not None
            and ("berry" in normalized_name or "gem" in normalized_name)
        )
        if item_destroyed:
            target.item = None

        return {
            "name": self.name,
            "item_destroyed": held_item if item_destroyed else None,
            "applied": item_destroyed,
        }

    @staticmethod
    def _get_item_name(item):
        """Get a readable item name from strings, enums, or item objects."""
        if isinstance(item, str):
            return item
        return str(
            getattr(item, "name", getattr(item, "value", item))
        )
