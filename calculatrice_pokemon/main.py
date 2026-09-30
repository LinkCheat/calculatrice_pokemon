from enums.nature import Nature

try:
    from moves import Tackle
except ModuleNotFoundError:
    from calculatrice_pokemon.moves import Tackle

import field
import pokemon
import move


def input_player_action(battle_field):
    active_pokemon = battle_field.player_active_pokemon
    valid_indexes = set()

    print(f"Actions disponibles pour {active_pokemon.name} :")
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
        else:
            valid_indexes.add(action_index)
            availability = ""
        print(f"{action_index}: Switch vers {selected_pokemon.name}{availability}")

    if not valid_indexes:
        raise ValueError("Aucune action utilisable n'est disponible pour le Pokémon actif.")

    while True:
        try:
            action_index = int(input("Choisissez l'index de votre action : "))
        except ValueError:
            print("Veuillez saisir un nombre entier.")
            continue

        if action_index in valid_indexes:
            return action_index
        print("Cet index ne correspond pas à une action disponible.")


battle_field = field.Field()
player_pokemon = pokemon.Pokemon("Charizard", "Mega Charizard X")
player_bench_pokemon = pokemon.Pokemon("Pikachu")
opponent_pokemon = pokemon.Pokemon("Charizard")
battle_field.add_pokemon(player_pokemon, "player")
battle_field.add_pokemon(player_bench_pokemon, "player")
battle_field.add_pokemon(opponent_pokemon, "opponent")

player_pokemon.nature = Nature.MODEST
opponent_pokemon.nature = Nature.TIMID

player_pokemon.ivs["attack"] = 0
opponent_pokemon.evs["speed"] = 252
player_pokemon.stat_modifiers["attack"] = 2

player_pokemon.calculateStats()
opponent_pokemon.calculateStats()


print(f"Player's Pokemon: {player_pokemon.name}, Type: {player_pokemon.type}, Stats: {player_pokemon.stats}")
print(f"Opponent's Pokemon: {opponent_pokemon.name}, Type: {opponent_pokemon.type}, Stats: {opponent_pokemon.stats}")

# Test : on donne une attaque Charge à un Pokémon, puis on récupère sa catégorie et son type via Moves
charge = Tackle()
player_pokemon.add_move(charge)
opponent_pokemon.add_move(Tackle())
attack = battle_field.player_active_pokemon.moves[0]

print(f"Attaque donnée : {attack.name} ({attack.pp}/{attack.max_pp} PP)")
print(f"Type de l'attaque : {attack.type}")
print(f"Catégorie de l'attaque : {attack.category}")
print(f"L'attaque est bien une instance de Moves : {isinstance(attack, move.Moves)}")

player_action_index = input_player_action(battle_field)
attack_order = battle_field.determine_attack_order(player_action_index, 0)
for action in attack_order:
    if action["type"] == "switch":
        battle_field.switch_pokemon(action["side"], action["team_index"])
        print(f"{action['side']} switch vers {action['pokemon'].name}")
    else:
        print(f"{action['side']} joue {action['move'].name}")