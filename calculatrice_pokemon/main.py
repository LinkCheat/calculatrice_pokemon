from enums.nature import Nature

try:
    from moves import Tackle
except ModuleNotFoundError:
    from calculatrice_pokemon.moves import Tackle

import field
import pokemon
import move


field = field.Field()
field.playerPokemon = pokemon.Pokemon("Pikachu")
field.opponentPokemon = pokemon.Pokemon("Charizard")

field.playerPokemon.nature = Nature.MODEST
field.opponentPokemon.nature = Nature.TIMID

field.playerPokemon.ivs["attack"] = 0
field.opponentPokemon.evs["speed"] = 252
field.playerPokemon.stat_modifiers["attack"] = 2

field.playerPokemon.calculateStats()
field.opponentPokemon.calculateStats()


print(f"Player's Pokemon: {field.playerPokemon.name}, Type: {field.playerPokemon.type}, Stats: {field.playerPokemon.stats}")
print(f"Opponent's Pokemon: {field.opponentPokemon.name}, Type: {field.opponentPokemon.type}, Stats: {field.opponentPokemon.stats}")

# Test : on donne une attaque Charge à un Pokémon, puis on récupère sa catégorie et son type via Moves
charge = Tackle()
field.playerPokemon.moves = [charge]
attack = field.playerPokemon.moves[0]

print(f"Attaque donnée : {attack.name}")
print(f"Type de l'attaque : {attack.type}")
print(f"Catégorie de l'attaque : {attack.category}")
print(f"L'attaque est bien une instance de Moves : {isinstance(attack, move.Moves)}")