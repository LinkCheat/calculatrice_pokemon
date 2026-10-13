import math
import random

from enums.ability import Ability
from enums.weather import Weather
from enums.terrain import Terrain
from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from enums.type_chart import TypeChart


class Field:
    MAX_TEAM_SIZE = 6
    SWITCH_INDEX_OFFSET = 5
    SWITCH_PRIORITY = 6

    def __init__(self):
        """Create an empty battle field with no active Pokémon or conditions."""
        self._player_team = []
        self._opponent_team = []
        self._player_active_index = None
        self._opponent_active_index = None
        self.player_action_index = None
        self.opponent_action_index = None
        self.turn_number = 0

        self.weather = None
        self.terrain = None
        self.terrain_turns_remaining = 0
        self.gravity_active = False

    @property
    def player_team(self):
        """Return a tuple snapshot of the player's team."""
        return tuple(self._player_team)

    @property
    def opponent_team(self):
        """Return a tuple snapshot of the opponent's team."""
        return tuple(self._opponent_team)

    @property
    def player_active_pokemon(self):
        """Return the player's active Pokémon, or None if the team is empty."""
        return self._get_active_pokemon("player")

    @property
    def opponent_active_pokemon(self):
        """Return the opponent's active Pokémon, or None if the team is empty."""
        return self._get_active_pokemon("opponent")

    def has_living_pokemon(self, side):
        """Return whether the selected side has at least one Pokémon above zero HP."""
        return any(pokemon.current_hp > 0 for pokemon in self._get_team(side))

    def first_living_pokemon_index(self, side):
        """Return the first living team index, or None if the side has none."""
        return next(
            (
                index
                for index, pokemon in enumerate(self._get_team(side))
                if pokemon.current_hp > 0
            ),
            None,
        )

    def add_pokemon(self, pokemon, side):
        """Add a Pokémon to a side and make it active if it is that side's first.

        Raises:
            ValueError: If the team already contains the maximum number of Pokémon.
        """
        team = self._get_team(side)

        if len(team) >= self.MAX_TEAM_SIZE:
            raise ValueError(f"Une équipe ne peut pas contenir plus de {self.MAX_TEAM_SIZE} Pokémon.")

        team.append(pokemon)
        if len(team) == 1:
            self._set_active_index(side, 0)

    def initialize_battle(self):
        """Recalculate every team member's stats and restore each one's HP."""
        for pokemon in self._player_team + self._opponent_team:
            pokemon.calculateStats()
            pokemon.current_hp = pokemon.max_hp
            if pokemon.forest_cursed:
                pokemon.type.remove(Type.GRASS)
                pokemon.forest_cursed = False
            pokemon.charging_move = None
            pokemon.recharging_move = None
            pokemon.protected_this_turn = False
            pokemon.protection_streak = 0
            pokemon.locked_move = None
            pokemon.locked_move_turns_remaining = 0
            pokemon.confusion_turns_remaining = 0
            pokemon.leech_seeded = False
            pokemon.ingrain_active = False
            pokemon.snap_trap_turns_remaining = 0
            pokemon.syrupy_turns_remaining = 0
            pokemon.syrupy_skip_next_tick = False
            pokemon.flinched = False
            pokemon.has_acted_this_turn = False

        self._activate_entry_ability("player")
        self._activate_entry_ability("opponent")

    def switch_pokemon(self, side, team_index):
        """Make a team member active and return it.

        Raises:
            ValueError: If the index is invalid or selects the already-active Pokémon.
        """
        team = self._get_team(side)
        if not isinstance(team_index, int) or not 0 <= team_index < len(team):
            raise ValueError("L'index du Pokémon à sélectionner est invalide.")
        if team[team_index].current_hp <= 0:
            raise ValueError("Impossible de switcher vers un Pokémon K.O.")
        if team_index == self._get_active_index(side):
            raise ValueError("Ce Pokémon est déjà actif.")

        outgoing_pokemon = self._get_active_pokemon(side)
        if outgoing_pokemon is not None:
            if (
                outgoing_pokemon.current_hp > 0
                and outgoing_pokemon.locked_move is not None
            ):
                raise ValueError("Le Pokémon est bloqué sur une capacité et ne peut pas se retirer.")
            if (
                outgoing_pokemon.current_hp > 0
                and outgoing_pokemon.snap_trap_turns_remaining > 0
            ):
                raise ValueError("Le Pokémon actif est piégé et ne peut pas être retiré.")
            if (
                outgoing_pokemon.current_hp > 0
                and outgoing_pokemon.ingrain_active
                and Type.GHOST not in outgoing_pokemon.type
            ):
                raise ValueError("Le Pokémon est enraciné et ne peut pas se retirer.")
            outgoing_pokemon.leech_seeded = False
            outgoing_pokemon.ingrain_active = False
            outgoing_pokemon.snap_trap_turns_remaining = 0
            outgoing_pokemon.syrupy_turns_remaining = 0
            outgoing_pokemon.syrupy_skip_next_tick = False
            outgoing_pokemon.charging_move = None
            outgoing_pokemon.recharging_move = None
            outgoing_pokemon.protected_this_turn = False
            outgoing_pokemon.protection_streak = 0
            outgoing_pokemon.locked_move = None
            outgoing_pokemon.locked_move_turns_remaining = 0
            outgoing_pokemon.confusion_turns_remaining = 0
            if outgoing_pokemon.forest_cursed:
                outgoing_pokemon.type.remove(Type.GRASS)
                outgoing_pokemon.forest_cursed = False
            for stat_name in outgoing_pokemon.stat_modifiers:
                outgoing_pokemon.stat_modifiers[stat_name] = 0
        self._set_active_index(side, team_index)
        self._activate_entry_ability(side)
        return team[team_index]

    def _activate_entry_ability(self, side):
        """Apply the active Pokémon's ability effects that trigger on entry."""
        pokemon = self._get_active_pokemon(side)
        opposing_side = "opponent" if side == "player" else "player"
        opposing_pokemon = self._get_active_pokemon(opposing_side)

        if (
            pokemon is None
            or opposing_pokemon is None
            or opposing_pokemon.current_hp <= 0
        ):
            return

        if pokemon.ability is Ability.INTIMIDATION:
            attack_stage = opposing_pokemon.stat_modifiers["attack"]
            if attack_stage > -6:
                opposing_pokemon.stat_modifiers["attack"] = attack_stage - 1

    def _get_team(self, side):
        """Return the mutable team list for a side; reject unknown side names."""
        if side == "player":
            return self._player_team
        if side == "opponent":
            return self._opponent_team
        raise ValueError("side doit être 'player' ou 'opponent'.")

    def _get_active_index(self, side):
        """Return the active team index for a side; reject unknown side names."""
        if side == "player":
            return self._player_active_index
        if side == "opponent":
            return self._opponent_active_index
        raise ValueError("side doit être 'player' ou 'opponent'.")

    def _set_active_index(self, side, team_index):
        """Update a side's active team index; reject unknown side names."""
        if side == "player":
            self._player_active_index = team_index
        elif side == "opponent":
            self._opponent_active_index = team_index
        else:
            raise ValueError("side doit être 'player' ou 'opponent'.")

    def _get_active_pokemon(self, side):
        """Look up a side's active Pokémon, returning None if none is selected."""
        team = self._get_team(side)
        active_index = self._get_active_index(side)
        if active_index is None:
            return None
        return team[active_index]

    def _resolve_action(self, side, action_index):
        """Convert a player's numeric choice into a validated move or switch action.

        Move choices use indexes 0-3; switch choices encode team indexes starting
        at 5. The returned dictionary also includes the action's priority.
        """
        team = self._get_team(side)
        active_pokemon = self._get_active_pokemon(side)
        if active_pokemon is None:
            raise ValueError(f"L'équipe {side} ne contient aucun Pokémon.")

        if isinstance(action_index, int) and 0 <= action_index < 4:
            if active_pokemon.locked_move is None and action_index >= len(active_pokemon.moves):
                raise ValueError(f"Aucune attaque à l'index {action_index} pour le Pokémon actif.")
            selected_move = (
                active_pokemon.locked_move
                or active_pokemon.charging_move
                or active_pokemon.recharging_move
                or active_pokemon.moves[action_index]
            )
            if (
                active_pokemon.charging_move is None
                and active_pokemon.recharging_move is None
                and active_pokemon.locked_move is None
                and selected_move.pp <= 0
            ):
                raise ValueError(f"{selected_move.name} n'a plus de PP et ne peut pas être sélectionnée.")
            opposing_side = "opponent" if side == "player" else "player"
            target = self._get_active_pokemon(opposing_side)
            return {
                "side": side,
                "type": "move",
                "pokemon": active_pokemon,
                "move": selected_move,
                "priority": selected_move.get_priority(active_pokemon, target, self),
            }

        if isinstance(action_index, int) and action_index > 4:
            team_index = action_index - self.SWITCH_INDEX_OFFSET
            if (
                active_pokemon.current_hp > 0
                and active_pokemon.locked_move is not None
            ):
                raise ValueError("Le Pokémon est bloqué sur une capacité et ne peut pas se retirer.")
            if (
                active_pokemon.current_hp > 0
                and active_pokemon.snap_trap_turns_remaining > 0
            ):
                raise ValueError("Le Pokémon actif est piégé et ne peut pas être retiré.")
            if (
                active_pokemon.current_hp > 0
                and active_pokemon.ingrain_active
                and Type.GHOST not in active_pokemon.type
            ):
                raise ValueError("Le Pokémon est enraciné et ne peut pas se retirer.")
            if not 0 <= team_index < len(team):
                raise ValueError(f"L'index de switch {action_index} ne désigne aucun Pokémon de l'équipe.")
            selected_pokemon = team[team_index]
            if selected_pokemon.current_hp <= 0:
                raise ValueError("Impossible de switcher vers un Pokémon K.O.")
            if team_index == self._get_active_index(side):
                raise ValueError("Impossible de switcher vers le Pokémon déjà actif.")
            return {
                "side": side,
                "type": "switch",
                "pokemon": team[team_index],
                "team_index": team_index,
                "move": None,
                "priority": self.SWITCH_PRIORITY,
            }

        raise ValueError("L'index d'action doit être entre 0 et 3 pour une attaque, ou entre 5 et 10 pour un switch.")

    def determine_attack_order(self, player_action_index, opponent_action_index):
        """Validate both choices and order actions by priority, speed, then a tie-break.

        Returns the two resolved action dictionaries in execution order. A speed
        tie is decided randomly.
        """
        self.player_action_index = player_action_index
        self.opponent_action_index = opponent_action_index

        actions = {
            "player": self._resolve_action("player", player_action_index),
            "opponent": self._resolve_action("opponent", opponent_action_index),
        }
        player_pokemon = self.player_active_pokemon
        opponent_pokemon = self.opponent_active_pokemon
        player_pokemon.calculateStats()
        opponent_pokemon.calculateStats()

        player_priority = actions["player"]["priority"]
        opponent_priority = actions["opponent"]["priority"]

        if player_priority != opponent_priority:
            first_side = "player" if player_priority > opponent_priority else "opponent"
        elif player_pokemon.stats["speed"] != opponent_pokemon.stats["speed"]:
            first_side = "player" if player_pokemon.stats["speed"] > opponent_pokemon.stats["speed"] else "opponent"
        else:
            first_side = random.choice(("player", "opponent"))

        second_side = "opponent" if first_side == "player" else "player"
        return [actions[first_side], actions[second_side]]

    def resolve_turn(self, player_action_index, opponent_action_index):
        """Resolve both sides' actions in order, then advance the turn counter."""
        for pokemon in self._player_team + self._opponent_team:
            pokemon.has_acted_this_turn = False
            pokemon.protected_this_turn = False

        resolved_actions = self.determine_attack_order(
            player_action_index,
            opponent_action_index,
        )
        turn_results = []
        for action in resolved_actions:
            if not self.has_living_pokemon("player") or not self.has_living_pokemon("opponent"):
                break

            if action["type"] == "switch":
                self.switch_pokemon(action["side"], action["team_index"])
                result = None
            elif action["pokemon"].current_hp <= 0:
                result = {
                    "hit": False,
                    "immune": False,
                    "damage": 0,
                    "effect": None,
                    "fainted": True,
                }
            else:
                result = self.resolve_move(action["side"], action["move"])

            turn_results.append({"action": action, "result": result})
            if (
                action["type"] == "move"
                and result is not None
                and (
                    not result.get("unable_to_act")
                    or result.get("confusion_self_hit")
                )
            ):
                lock_effect = self._advance_move_lock(action["pokemon"])
                if lock_effect is not None:
                    result["lock_effect"] = lock_effect
            for pokemon in self._get_team(action["side"]):
                pokemon.has_acted_this_turn = True

        for pokemon in self._player_team + self._opponent_team:
            pokemon.flinched = False
            pokemon.has_acted_this_turn = False
        if len(turn_results) == 2:
            self.turn_number += 1
            turn_results.extend(self._apply_leech_seed())
            turn_results.extend(self._apply_snap_trap())
            turn_results.extend(self._apply_syrup_bomb())
            turn_results.extend(self._apply_ingrain())
            turn_results.extend(self._apply_grassy_terrain())
        return turn_results

    def _apply_syrup_bomb(self):
        """Lower active targets' Speed and count down Syrup Bomb effects."""
        residual_results = []
        for side in ("player", "opponent"):
            target = self._get_active_pokemon(side)
            if (
                target is None
                or target.current_hp <= 0
                or target.syrupy_turns_remaining <= 0
            ):
                continue

            if target.syrupy_skip_next_tick:
                target.syrupy_skip_next_tick = False
                continue

            applied = target.stat_modifiers["speed"] > -6
            if applied:
                target.stat_modifiers["speed"] -= 1

            target.syrupy_turns_remaining -= 1
            residual_results.append({
                "action": {
                    "type": "syrup_bomb_residual",
                    "side": side,
                    "pokemon": target,
                },
                "result": {
                    "stat": "speed",
                    "stages": -1 if applied else 0,
                    "applied": applied,
                    "turns_remaining": target.syrupy_turns_remaining,
                },
            })
        return residual_results

    def _apply_ingrain(self):
        """Restore one sixteenth of max HP to each active rooted Pokémon."""
        residual_results = []
        for side in ("player", "opponent"):
            pokemon = self._get_active_pokemon(side)
            if (
                pokemon is None
                or pokemon.current_hp <= 0
                or not pokemon.ingrain_active
            ):
                continue

            healing = min(
                max(1, pokemon.max_hp // 16),
                pokemon.max_hp - pokemon.current_hp,
            )
            if healing <= 0:
                continue

            pokemon.current_hp += healing
            residual_results.append({
                "action": {
                    "type": "ingrain_residual",
                    "side": side,
                    "pokemon": pokemon,
                },
                "result": {"healed": healing},
            })
        return residual_results

    def _apply_grassy_terrain(self):
        """Heal active grounded Pokémon, then count down Grassy Terrain."""
        if (
            self.terrain is not Terrain.GRASSY
            or self.terrain_turns_remaining <= 0
        ):
            return []

        residual_results = []
        for side in ("player", "opponent"):
            pokemon = self._get_active_pokemon(side)
            if (
                pokemon is None
                or pokemon.current_hp <= 0
                or not self._is_grounded(pokemon)
            ):
                continue

            healing = min(
                max(1, pokemon.max_hp // 16),
                pokemon.max_hp - pokemon.current_hp,
            )
            if healing <= 0:
                continue

            pokemon.current_hp += healing
            residual_results.append({
                "action": {
                    "type": "grassy_terrain_residual",
                    "side": side,
                    "pokemon": pokemon,
                },
                "result": {
                    "healed": healing,
                    "turns_remaining": self.terrain_turns_remaining - 1,
                },
            })

        self.terrain_turns_remaining -= 1
        if self.terrain_turns_remaining <= 0:
            self.terrain_turns_remaining = 0
            self.terrain = None
        return residual_results

    def _advance_move_lock(self, pokemon):
        """Count a completed locked turn and apply its end-of-lock effect."""
        if pokemon.locked_move is None:
            return
        if pokemon.current_hp <= 0:
            pokemon.locked_move = None
            pokemon.locked_move_turns_remaining = 0
            return

        pokemon.locked_move_turns_remaining -= 1
        if pokemon.locked_move_turns_remaining > 0:
            return

        move = pokemon.locked_move
        pokemon.locked_move = None
        pokemon.locked_move_turns_remaining = 0
        if move.confuses_user_after_lock():
            pokemon.confusion_turns_remaining = random.randint(1, 4)
            return {
                "condition": "confusion",
                "applied": True,
                "turns": pokemon.confusion_turns_remaining,
            }
        return None

    def _apply_snap_trap(self):
        """Damage and count down active Snap Trap effects at turn end."""
        residual_results = []
        for side in ("player", "opponent"):
            trapped_pokemon = self._get_active_pokemon(side)
            if (
                trapped_pokemon is None
                or trapped_pokemon.current_hp <= 0
                or trapped_pokemon.snap_trap_turns_remaining <= 0
            ):
                continue

            damage = min(
                max(1, trapped_pokemon.max_hp // 8),
                trapped_pokemon.current_hp,
            )
            trapped_pokemon.current_hp -= damage
            trapped_pokemon.snap_trap_turns_remaining -= 1
            turns_remaining = trapped_pokemon.snap_trap_turns_remaining
            if turns_remaining == 0:
                trapped_pokemon.snap_trap_turns_remaining = 0

            residual_results.append({
                "action": {
                    "type": "snap_trap_residual",
                    "side": side,
                    "pokemon": trapped_pokemon,
                },
                "result": {
                    "damage": damage,
                    "turns_remaining": turns_remaining,
                },
            })
        return residual_results

    def _apply_leech_seed(self):
        """Drain seeded active Pokémon and heal the active Pokémon on the other side."""
        residual_results = []
        for target_side in ("player", "opponent"):
            target = self._get_active_pokemon(target_side)
            if target is None or not target.leech_seeded or target.current_hp <= 0:
                continue

            drain_amount = max(1, target.max_hp // 8)
            drained = min(drain_amount, target.current_hp)
            target.current_hp -= drained

            recipient_side = "opponent" if target_side == "player" else "player"
            recipient = self._get_active_pokemon(recipient_side)
            healed = 0
            if recipient is not None and recipient.current_hp > 0:
                healed = min(drained, recipient.max_hp - recipient.current_hp)
                recipient.current_hp += healed

            residual_results.append({
                "action": {
                    "type": "leech_seed_residual",
                    "side": target_side,
                    "pokemon": target,
                },
                "result": {
                    "drained": drained,
                    "healed": healed,
                    "recipient_name": recipient.name if recipient is not None else None,
                },
            })
        return residual_results

    @staticmethod
    def _stage_multiplier(stage):
        """Convert an accuracy or evasion stage into its battle multiplier."""
        if stage >= 0:
            return 1 + stage / 3
        return 1 / (1 + abs(stage) / 3)

    def attack_hits(self, attacker, defender, move):
        """Roll the move's accuracy against the combatants' accuracy stages."""
        if move.accuracy >= 101:
            return True

        accuracy_multiplier = self._stage_multiplier(attacker.stat_modifiers["accuracy"])
        evasion_multiplier = self._stage_multiplier(defender.stat_modifiers["evasion"])
        hit_chance = move.accuracy * accuracy_multiplier / evasion_multiplier
        if hit_chance >= 100:
            return True
        return random.random() * 100 < max(0, hit_chance)

    def calculate_move_effectiveness(self, move, defender, attacker=None):
        """Multiply type effectiveness across all of the defender's types."""
        move_type = move.get_type(attacker, defender, self)
        effectiveness = 1.0
        for defending_type in defender.type:
            if (
                defending_type is Type.FLYING
                and move_type is Type.GROUND
                and self._is_grounded(defender)
            ):
                continue
            effectiveness *= self.calculate_type_effectiveness(move_type, defending_type)
        return effectiveness

    def is_immune_to_move(self, move, defender, attacker=None):
        """Return whether type matchup or powder immunity prevents a move."""
        if move.powder and Type.GRASS in defender.type:
            return True
        if move.electric_type_immune and Type.ELECTRIC in defender.type:
            return True
        if move.grass_type_immune and Type.GRASS in defender.type:
            return True
        return self.calculate_move_effectiveness(move, defender, attacker) == 0

    def calculate_stab_multiplier(self, attacker, move):
        """Return the same-type attack bonus multiplier for this attacker and move."""
        return 1.5 if move.get_type(attacker, field=self) in attacker.type else 1.0

    def calculate_critical_hit_multiplier(self, attacker, defender, move):
        """Roll for a critical hit and return its damage multiplier.

        Critical-hit stage starts at 1 and is adjusted by the attacker's
        ``critical_hit`` stat modifier. Stages below 1 use the stage-1 chance;
        stages 4 and above always crit. Critical hits deal 1.5x damage and
        ignore attack drops and defense boosts for the stat pair used by the
        move, by reversing those stat-stage multipliers.
        """
        critical_stage = max(
            1,
            1
            + attacker.stat_modifiers["critical_hit"]
            + move.get_critical_hit_stage_bonus(attacker, defender, self),
        )
        if critical_stage == 1:
            critical_chance = 1 / 24
        elif critical_stage == 2:
            critical_chance = 1 / 8
        elif critical_stage == 3:
            critical_chance = 1 / 2
        else:
            critical_chance = 1.0

        if random.random() >= critical_chance:
            return 1.0

        if move.category is MoveCategory.PHYSICAL:
            attack_stat_name = "attack"
            defense_stat_name = "defense"
        elif move.category is MoveCategory.SPECIAL:
            attack_stat_name = "sp_atk"
            defense_stat_name = "sp_def"
        else:
            return 1.0

        multiplier = 1.5
        attack_stage = attacker.stat_modifiers[attack_stat_name]
        defense_stage = defender.stat_modifiers[defense_stat_name]

        if attack_stage < 0:
            multiplier *= 1 + 0.5 * abs(attack_stage)
        if defense_stage > 0:
            multiplier *= 1 + 0.5 * defense_stage

        return multiplier

    def calculate_damage_modifiers(self, attacker, defender, move):
        """Combine type effectiveness, STAB, and the critical-hit multiplier."""
        modifiers = (
            self.calculate_move_effectiveness(move, defender, attacker)
            * self.calculate_stab_multiplier(attacker, move)
            * self.calculate_critical_hit_multiplier(attacker, defender, move)
        )
        if (
            self.terrain is Terrain.GRASSY
            and self._is_grounded(attacker)
            and move.get_type(attacker, defender, self) is Type.GRASS
        ):
            modifiers *= 1.3
        return modifiers

    def _is_grounded(self, pokemon):
        """Return whether a Pokémon is grounded for terrain interactions."""
        return (
            self.gravity_active
            or pokemon.ingrain_active
            or Type.FLYING not in pokemon.type
        )

    def calculate_damage(self, attacker, defender, move):
        """Calculate damage from battle stats, move power, type, and move effects.

        Status moves deal no damage. Physical and special moves use their
        corresponding attacking and defending stats.
        """
        if move.category is MoveCategory.STATUS:
            return 0

        if move.category is MoveCategory.PHYSICAL:
            attack_stat = attacker.stats["attack"]
            defense_stat = defender.stats["defense"]
        elif move.category is MoveCategory.SPECIAL:
            attack_stat = attacker.stats["sp_atk"]
            defense_stat = defender.stats["sp_def"]
        else:
            raise ValueError(f"Catégorie d'attaque inconnue : {move.category}")

        power = move.get_power(attacker, defender, self)
        base_damage = math.floor(attacker.level * 0.4 + 2)
        base_damage = math.floor(base_damage * attack_stat * power / defense_stat)
        base_damage = math.floor(base_damage / 50) + 2

        modifiers = self.calculate_damage_modifiers(attacker, defender, move)
        standard_damage = math.floor(base_damage * modifiers)
        return move.calculate_damage(attacker, defender, standard_damage)

    def resolve_move(self, side, move):
        """Spend PP, resolve accuracy and immunity, then apply damage and effects.

        Returns a result dictionary with ``hit``, ``immune``, ``damage``, and
        ``effect`` fields. The move's PP is consumed even when it misses or the
        target is immune.
        """
        attacker = self._get_active_pokemon(side)
        opponent_side = "opponent" if side == "player" else "player"
        defender = self._get_active_pokemon(opponent_side)
        if attacker is None or defender is None:
            raise ValueError("Chaque camp doit avoir un Pokémon actif pour résoudre une attaque.")
        is_protection_move = move.is_protection_move()
        if not is_protection_move:
            attacker.protection_streak = 0

        def fail_protection_streak():
            if is_protection_move:
                attacker.protection_streak = 0

        if attacker.recharging_move is not None:
            fail_protection_streak()
            attacker.recharging_move = None
            return {
                "hit": False,
                "immune": False,
                "damage": 0,
                "effect": None,
                "hits": 0,
                "unable_to_act": True,
                "recharging": True,
            }
        if attacker.flinched:
            fail_protection_streak()
            attacker.flinched = False
            return {
                "hit": False,
                "immune": False,
                "damage": 0,
                "effect": None,
                "hits": 0,
                "unable_to_act": True,
                "flinched": True,
            }
        if attacker.status_condition is STATUS_CONDITION.SLEEP:
            fail_protection_streak()
            if attacker.charging_move is move:
                attacker.charging_move = None
            attacker.sleep_turns_remaining -= 1
            if attacker.sleep_turns_remaining <= 0:
                attacker.sleep_turns_remaining = 0
                attacker.status_condition = None
            return {
                "hit": False,
                "immune": False,
                "damage": 0,
                "effect": None,
                "unable_to_act": True,
            }
        if (
            attacker.status_condition is STATUS_CONDITION.PARALYSIS
            and random.random() < 0.25
        ):
            fail_protection_streak()
            return {
                "hit": False,
                "immune": False,
                "damage": 0,
                "effect": None,
                "hits": 0,
                "unable_to_act": True,
                "paralyzed": True,
            }
        is_releasing_charge = attacker.charging_move is move
        is_releasing_lock = attacker.locked_move is move

        if attacker.confusion_turns_remaining > 0:
            attacker.calculateStats()
            confusion_self_hit = random.random() < 0.33
            attacker.confusion_turns_remaining -= 1
            confusion_turns_remaining = attacker.confusion_turns_remaining
            if confusion_turns_remaining == 0:
                attacker.confusion_turns_remaining = 0
            if confusion_self_hit:
                fail_protection_streak()
                damage = self.calculate_confusion_damage(attacker)
                attacker.current_hp = max(0, attacker.current_hp - damage)
                return {
                    "hit": False,
                    "immune": False,
                    "damage": damage,
                    "effect": None,
                    "hits": 0,
                    "unable_to_act": True,
                    "confusion_self_hit": True,
                    "confusion_turns_remaining": confusion_turns_remaining,
                }

        if not is_releasing_charge and not is_releasing_lock and move.pp <= 0:
            raise ValueError(f"{move.name} n'a plus de PP et ne peut pas être utilisée.")

        if is_releasing_charge:
            attacker.charging_move = None
        elif not is_releasing_lock:
            move.consume_pp()

        if is_protection_move:
            success_chance = 1 / (2 ** attacker.protection_streak)
            if success_chance < 1 and random.random() >= success_chance:
                attacker.protection_streak = 0
                return {
                    "hit": False,
                    "immune": False,
                    "damage": 0,
                    "effect": None,
                    "hits": 0,
                    "protection_failed": True,
                }
            attacker.protection_streak += 1
            attacker.protected_this_turn = True
            effect = move.effect(attacker, defender)
            if effect is None:
                effect = {"condition": "protection", "applied": True}
            return {
                "hit": True,
                "immune": False,
                "damage": 0,
                "effect": effect,
                "hits": 0,
                "protected": True,
            }

        if defender.protected_this_turn:
            contact_recoil = 0
            if move.contact:
                contact_recoil = min(
                    max(1, attacker.max_hp // 8),
                    attacker.current_hp,
                )
                attacker.current_hp -= contact_recoil
            return {
                "hit": False,
                "immune": False,
                "damage": 0,
                "effect": None,
                "hits": 0,
                "blocked_by_protection": True,
                "contact_recoil": contact_recoil,
            }

        if (
            not is_releasing_lock
            and not is_releasing_charge
            and move.requires_charge(self)
        ):
            attacker.charging_move = move
            return {
                "hit": True,
                "immune": False,
                "damage": 0,
                "effect": None,
                "charging": True,
            }

        if not is_releasing_lock and not is_releasing_charge:
            lock_turn_count = move.get_lock_turn_count(attacker, defender)
            if lock_turn_count > 1:
                attacker.locked_move = move
                attacker.locked_move_turns_remaining = lock_turn_count

        if not self.attack_hits(attacker, defender, move):
            return {"hit": False, "immune": False, "damage": 0, "effect": None, "hits": 0}

        if (
            not move.targets_user_team()
            and not move.applies_field_effect()
            and self.is_immune_to_move(move, defender, attacker)
        ):
            return {"hit": True, "immune": True, "damage": 0, "effect": None, "hits": 0}

        attacker.calculateStats()
        defender.calculateStats()
        damage = 0
        damage_dealt = 0
        hits = 0
        for _ in range(move.get_hit_count(attacker, defender)):
            if defender.current_hp <= 0:
                break
            hit_damage = self.calculate_damage(attacker, defender, move)
            damage += hit_damage
            damage_dealt += min(hit_damage, defender.current_hp)
            defender.current_hp = max(0, defender.current_hp - hit_damage)
            hits += 1

        if move.applies_field_effect():
            effect = move.apply_field_effect(attacker, self)
        elif move.targets_user_team():
            effect = move.apply_team_effect(attacker, self._get_team(side))
        else:
            effect = move.apply_effect_with_field(
                attacker,
                defender,
                damage_dealt,
                self,
            )
        if move.requires_recharge_after_use():
            attacker.recharging_move = move
        return {
            "hit": True,
            "immune": False,
            "damage": damage,
            "effect": effect,
            "hits": hits,
        }

    def calculate_confusion_damage(self, pokemon):
        """Calculate physical typeless self-damage without a critical hit."""
        attack = pokemon.stats["attack"]
        defense = pokemon.stats["defense"]
        base_damage = math.floor(pokemon.level * 0.4 + 2)
        base_damage = math.floor(base_damage * 40 * attack / defense)
        return math.floor(base_damage / 50) + 2

    @staticmethod
    def calculate_type_effectiveness(attack_type: Type, defending_type: Type) -> float:
        """Return the single-type matchup multiplier, defaulting to neutral.

        Raises:
            ValueError: If the attacking type is NONE or the defender is not a Type.
        """
        if attack_type is Type.NONE:
            raise ValueError("Le type d'une attaque ne peut pas être Type.NONE.")
        if not isinstance(defending_type, Type):
            raise ValueError("defending_type doit être une valeur de Type.")
        if defending_type is Type.NONE:
            return 1.0
        return TypeChart[attack_type.name].value.get(defending_type, 1.0)
