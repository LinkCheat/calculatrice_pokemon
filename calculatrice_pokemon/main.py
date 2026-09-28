from enums.nature import Nature
import field
import pokemon

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