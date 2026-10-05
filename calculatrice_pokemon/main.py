
try:
    from enums.nature import Nature
    from enums.type import Type
    from moves import *
    import field
    import pokemon
    import moves.move as move
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.nature import Nature
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves import *
    import calculatrice_pokemon.field as field
    import calculatrice_pokemon.pokemon as pokemon
    import calculatrice_pokemon.moves.move as move


def input_player_action(battle_field, forced_switch=False):
    """Display available player actions and return a valid selected index.

    Unusable moves and the currently active Pokémon are displayed but cannot be
    selected. The prompt repeats until the input matches an available action.
    """
    active_pokemon = battle_field.player_active_pokemon
    valid_indexes = set()

    print(f"Actions disponibles pour {active_pokemon.name} :")
    if not forced_switch:
        if active_pokemon.charging_move is not None:
            move_index = active_pokemon.moves.index(active_pokemon.charging_move)
            valid_indexes.add(move_index)
            print(
                f"{move_index}: Attaque {active_pokemon.charging_move.name} "
                "(tour de frappe)"
            )
        else:
            for move_index, selected_move in enumerate(active_pokemon.moves):
                if move_index >= pokemon.Pokemon.MAX_MOVES:
                    break

                if selected_move.pp > 0:
                    valid_indexes.add(move_index)
                    availability = ""
                else:
                    availability = " - inutilisable (0 PP)"
                print(
                    f"{move_index}: Attaque {selected_move.name} "
                    f"({selected_move.pp}/{selected_move.max_pp} PP){availability}"
                )

    for team_index in range(battle_field.MAX_TEAM_SIZE):
        action_index = battle_field.SWITCH_INDEX_OFFSET + team_index
        if team_index >= len(battle_field.player_team):
            continue

        selected_pokemon = battle_field.player_team[team_index]
        if selected_pokemon is active_pokemon:
            availability = " - déjà actif"
        elif selected_pokemon.current_hp <= 0:
            availability = " - K.O."
        else:
            valid_indexes.add(action_index)
            availability = ""
        print(f"{action_index}: Switch vers {selected_pokemon.name}{availability}")

    if not valid_indexes:
        if forced_switch:
            raise ValueError("Aucun Pokémon vivant ne peut remplacer le Pokémon K.O.")
        raise ValueError("Aucune action utilisable n'est disponible pour le Pokémon actif.")

    while True:
        user_input = input("Choisissez l'index de votre action (q pour quitter) : ")
        if user_input.strip().lower() == "q" and not forced_switch:
            return None

        try:
            action_index = int(user_input)
        except ValueError:
            print("Veuillez saisir un nombre entier.")
            continue

        if action_index in valid_indexes:
            return action_index
        print("Cet index ne correspond pas à une action disponible.")


def _display_action_result(battle_field, action, result):
    """Print one switch, successful move, miss, or sleep outcome."""
    if result is None:
        print(f"{action['side']} switch vers {action['pokemon'].name}")
        return

    if action["type"] == "leech_seed_residual":
        print(
            f"Vampigraine retire {result['drained']} PV à "
            f"{action['pokemon'].name}."
        )
        if result["healed"]:
            print(
                f"{result['recipient_name']} récupère "
                f"{result['healed']} PV."
            )
        return

    if result.get("charging"):
        print(f"{action['pokemon'].name} concentre la lumière pour {action['move'].name}.")
        return

    target_side = "opponent" if action["side"] == "player" else "player"
    target_pokemon = (
        battle_field.opponent_active_pokemon
        if target_side == "opponent"
        else battle_field.player_active_pokemon
    )
    if result.get("unable_to_act"):
        if result.get("flinched"):
            print(f"{action['pokemon'].name} est apeuré et ne peut pas agir.")
        else:
            print(f"{action['pokemon'].name} est endormi et ne peut pas agir.")
    elif result.get("fainted"):
        print(f"{action['pokemon'].name} est K.O. et ne peut pas agir.")
    elif not result["hit"]:
        print(f"{action['pokemon'].name} rate {action['move'].name}.")
    elif result["immune"]:
        print(f"{target_pokemon.name} est immunisé à {action['move'].name}.")
    else:
        effect = result["effect"]
        if effect and "status" in effect:
            if effect["applied"]:
                sleep_turns = effect["sleep_turns"]
                duration_label = "tour" if sleep_turns == 1 else "tours"
                print(
                    f"{target_pokemon.name} s'endort pour "
                    f"{sleep_turns} {duration_label}."
                )
            else:
                print(f"{target_pokemon.name} est déjà affecté par un statut.")
        else:
            hit_count = result.get("hits", 1)
            hit_description = f"et touche {hit_count} fois " if hit_count > 1 else ""
            print(
                f"{action['pokemon'].name} utilise {action['move'].name} "
                f"{hit_description}et "
                f"inflige {result['damage']} dégâts. "
                f"PV restants de {target_pokemon.name} : {target_pokemon.current_hp}"
            )
            if target_pokemon.current_hp == 0:
                print(f"{target_pokemon.name} est K.O.")

            if effect and effect.get("stat") in ("attack", "defense", "speed"):
                recipient = (
                    action["pokemon"]
                    if effect.get("recipient") == "user"
                    else target_pokemon
                )
                stat_name = {
                    "attack": "L'Attaque",
                    "defense": "La Défense",
                    "speed": "La Vitesse",
                }[effect["stat"]]
                if effect["applied"]:
                    change = "augmente" if effect["stages"] > 0 else "baisse"
                    print(f"{stat_name} de {recipient.name} {change} d'un cran.")
                else:
                    limit = "augmenter" if effect.get("recipient") == "user" else "baisser"
                    print(f"{stat_name} de {recipient.name} ne peut pas {limit} davantage.")
            if effect and "healed" in effect:
                print(
                    f"{action['pokemon'].name} récupère "
                    f"{effect['healed']} PV."
                )
            if effect and "recoil" in effect:
                print(
                    f"{action['pokemon'].name} perd "
                    f"{effect['recoil']} PV à cause du contrecoup. "
                    f"PV restants : {action['pokemon'].current_hp}"
                )
                if action["pokemon"].current_hp == 0:
                    print(f"{action['pokemon'].name} est K.O.")
            if effect and effect.get("flinched"):
                print(f"{target_pokemon.name} est apeuré.")
            elif effect and effect.get("reason") == "target_already_acted":
                print(
                    f"{target_pokemon.name} a déjà agi et ne peut pas être apeuré."
                )
            if effect and effect.get("condition") == "leech_seed":
                if effect["applied"]:
                    print(f"{target_pokemon.name} est couvert par Vampigraine.")
                elif effect["reason"] == "already_seeded":
                    print(f"{target_pokemon.name} est déjà couvert par Vampigraine.")
                elif effect["reason"] == "target_fainted":
                    print(f"{target_pokemon.name} est K.O. et ne peut pas être couvert par Vampigraine.")


def _announce_winner(battle_field):
    """Announce the winner and return whether the battle has ended."""
    player_has_living = battle_field.has_living_pokemon("player")
    opponent_has_living = battle_field.has_living_pokemon("opponent")
    if player_has_living and opponent_has_living:
        return False

    if player_has_living:
        print("Tous les Pokémon adverses sont K.O. Le joueur gagne !")
    elif opponent_has_living:
        print("Tous les Pokémon du joueur sont K.O. L'adversaire gagne !")
    else:
        print("Tous les Pokémon des deux équipes sont K.O. Le combat est nul.")
    return True


def _replace_fainted_pokemon(battle_field, side):
    """Replace a fainted active Pokémon with a living teammate."""
    active_pokemon = (
        battle_field.player_active_pokemon
        if side == "player"
        else battle_field.opponent_active_pokemon
    )
    if active_pokemon.current_hp > 0:
        return

    if side == "player":
        print("Votre Pokémon est K.O. Choisissez un remplaçant.")
        action_index = input_player_action(battle_field, forced_switch=True)
        team_index = action_index - battle_field.SWITCH_INDEX_OFFSET
    else:
        team_index = battle_field.first_living_pokemon_index(side)
        print(f"L'adversaire envoie {battle_field.opponent_team[team_index].name}.")

    battle_field.switch_pokemon(side, team_index)


def main():
    """Run the interactive battle one complete two-sided turn at a time."""
    battle_field = field.Field()
    player_pokemon = pokemon.Pokemon("Charizard", "Mega Charizard X")
    player_bench_pokemon = pokemon.Pokemon("Pikachu")
    player_seed_pokemon = pokemon.Pokemon("Bulbasaur")
    player_grassy_pokemon = pokemon.Pokemon("Bulbasaur")
    player_wood_hammer_pokemon = pokemon.Pokemon("Bulbasaur")
    player_ivy_cudgel_pokemon = pokemon.Pokemon("Bulbasaur")
    opponent_pokemon = pokemon.Pokemon("Greninja")
    opponent_bench_pokemon = pokemon.Pokemon("Eevee")
    battle_field.add_pokemon(player_pokemon, "player")
    battle_field.add_pokemon(player_bench_pokemon, "player")
    battle_field.add_pokemon(player_seed_pokemon, "player")
    battle_field.add_pokemon(player_grassy_pokemon, "player")
    battle_field.add_pokemon(player_wood_hammer_pokemon, "player")
    battle_field.add_pokemon(player_ivy_cudgel_pokemon, "player")
    battle_field.add_pokemon(opponent_pokemon, "opponent")
    battle_field.add_pokemon(opponent_bench_pokemon, "opponent")

    player_pokemon.nature = Nature.MODEST
    opponent_pokemon.nature = Nature.TIMID

    player_pokemon.ivs["attack"] = 0
    opponent_pokemon.evs["speed"] = 252
    player_pokemon.stat_modifiers["attack"] = 2

    battle_field.initialize_battle()

    print(f"Player's Pokemon: {player_pokemon.name}, Type: {player_pokemon.type}, Stats: {player_pokemon.stats}")
    print(f"Opponent's Pokemon: {opponent_pokemon.name}, Type: {opponent_pokemon.type}, Stats: {opponent_pokemon.stats}")

    #Un pokémon a 4 attaques maximum, on les ajoute ici pour le test
    player_pokemon.add_move(Tackle())
    player_pokemon.add_move(Spore())
    player_pokemon.add_move(BulletSeed())
    player_pokemon.add_move(TropKick())
    player_bench_pokemon.add_move(SeedBomb())
    player_bench_pokemon.add_move(Trailblaze())
    player_bench_pokemon.add_move(HornLeech())
    player_bench_pokemon.add_move(LeechSeed())
    player_seed_pokemon.add_move(SappySeed())
    player_seed_pokemon.add_move(Leafage())
    player_seed_pokemon.add_move(GravApple())
    player_seed_pokemon.add_move(VineWhip())
    player_grassy_pokemon.add_move(GrassyGlide())
    player_grassy_pokemon.add_move(LeafBlade())
    player_grassy_pokemon.add_move(SolarBlade())
    player_grassy_pokemon.add_move(FlowerTrick())
    player_wood_hammer_pokemon.add_move(WoodHammer())
    player_ivy_cudgel_pokemon.add_move(IvyCudgel())
    player_ivy_cudgel_pokemon.add_move(PowerWhip())
    player_ivy_cudgel_pokemon.add_move(NeedleArm())
    player_ivy_cudgel_pokemon.add_move(DrumBeating())
    opponent_pokemon.add_move(Tackle())
    opponent_bench_pokemon.add_move(Tackle())
    attack = battle_field.player_active_pokemon.moves[0]

    print(f"Attaque donnée : {attack.name} ({attack.pp}/{attack.max_pp} PP)")
    print(f"Type de l'attaque : {attack.type}")
    print(f"Catégorie de l'attaque : {attack.category}")
    print(f"L'attaque est bien une instance de Moves : {isinstance(attack, move.Moves)}")

    while True:
        print(f"\nTour {battle_field.turn_number + 1}")
        player_action_index = input_player_action(battle_field)
        if player_action_index is None:
            print("Combat terminé.")
            break

        turn_results = battle_field.resolve_turn(player_action_index, 0)
        for turn_result in turn_results:
            _display_action_result(
                battle_field,
                turn_result["action"],
                turn_result["result"],
            )
        if _announce_winner(battle_field):
            break

        _replace_fainted_pokemon(battle_field, "player")
        _replace_fainted_pokemon(battle_field, "opponent")
        print(f"Fin du tour {battle_field.turn_number}.")

    fire_vs_grass = field.Field.calculate_type_effectiveness(Type.FIRE, Type.GRASS)
    assert fire_vs_grass == 2.0
    print(f"Test de type : Feu contre Plante = x{fire_vs_grass} (attendu : x2)")


if __name__ == "__main__":
    main()