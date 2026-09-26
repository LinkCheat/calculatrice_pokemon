import field
import pokemon

field = field.Field()
field.playerPokemon = pokemon.Pokemon("Pikachu")
field.opponentPokemon = pokemon.Pokemon("Charizard")

print(f"Player's Pokemon: {field.playerPokemon.name}, Type: {field.playerPokemon.type}")
print(f"Opponent's Pokemon: {field.opponentPokemon.name}, Type: {field.opponentPokemon.type}")