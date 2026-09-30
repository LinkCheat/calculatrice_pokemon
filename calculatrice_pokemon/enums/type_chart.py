from enum import Enum

from enums.type import Type


class TypeChart(Enum):
    NORMAL = {
        Type.ROCK: 0.5, 
        Type.STEEL: 0.5, 
        Type.GHOST: 0.0
    }
    
    FIRE = {
        Type.GRASS: 2.0,
        Type.ICE: 2.0,
        Type.BUG: 2.0,
        Type.STEEL: 2.0,
        Type.FIRE: 0.5,
        Type.WATER: 0.5,
        Type.ROCK: 0.5,
        Type.DRAGON: 0.5,
    }
    WATER = {
        Type.FIRE: 2.0,
        Type.GROUND: 2.0,
        Type.ROCK: 2.0,
        Type.WATER: 0.5,
        Type.GRASS: 0.5,
        Type.DRAGON: 0.5,
    }
    GRASS = {
        Type.WATER: 2.0,
        Type.GROUND: 2.0,
        Type.ROCK: 2.0,
        Type.FIRE: 0.5,
        Type.GRASS: 0.5,
        Type.POISON: 0.5,
        Type.FLYING: 0.5,
        Type.BUG: 0.5,
        Type.DRAGON: 0.5,
        Type.STEEL: 0.5,
    }
    ELECTRIC = {
        Type.WATER: 2.0,
        Type.FLYING: 2.0,
        Type.ELECTRIC: 0.5,
        Type.GRASS: 0.5,
        Type.DRAGON: 0.5,
        Type.GROUND: 0.0,
    }
    ICE = {
        Type.GRASS: 2.0,
        Type.GROUND: 2.0,
        Type.FLYING: 2.0,
        Type.DRAGON: 2.0,
        Type.FIRE: 0.5,
        Type.WATER: 0.5,
        Type.ICE: 0.5,
        Type.STEEL: 0.5,
    }
    FIGHTING = {
        Type.NORMAL: 2.0,
        Type.ICE: 2.0,
        Type.ROCK: 2.0,
        Type.DARK: 2.0,
        Type.STEEL: 2.0,
        Type.POISON: 0.5,
        Type.FLYING: 0.5,
        Type.PSYCHIC: 0.5,
        Type.BUG: 0.5,
        Type.FAIRY: 0.5,
        Type.GHOST: 0.0,
    }
    POISON = {
        Type.GRASS: 2.0,
        Type.FAIRY: 2.0,
        Type.POISON: 0.5,
        Type.GROUND: 0.5,
        Type.ROCK: 0.5,
        Type.GHOST: 0.5,
        Type.STEEL: 0.0,
    }
    GROUND = {
        Type.FIRE: 2.0,
        Type.ELECTRIC: 2.0,
        Type.POISON: 2.0,
        Type.ROCK: 2.0,
        Type.STEEL: 2.0,
        Type.GRASS: 0.5,
        Type.BUG: 0.5,
        Type.FLYING: 0.0,
    }
    FLYING = {
        Type.GRASS: 2.0,
        Type.FIGHTING: 2.0,
        Type.BUG: 2.0,
        Type.ELECTRIC: 0.5,
        Type.ROCK: 0.5,
        Type.STEEL: 0.5,
    }
    PSYCHIC = {
        Type.FIGHTING: 2.0,
        Type.POISON: 2.0,
        Type.PSYCHIC: 0.5,
        Type.STEEL: 0.5,
        Type.DARK: 0.0,
    }
    BUG = {
        Type.GRASS: 2.0,
        Type.PSYCHIC: 2.0,
        Type.DARK: 2.0,
        Type.FIRE: 0.5,
        Type.FIGHTING: 0.5,
        Type.POISON: 0.5,
        Type.FLYING: 0.5,
        Type.GHOST: 0.5,
        Type.STEEL: 0.5,
        Type.FAIRY: 0.5,
    }
    ROCK = {
        Type.FIRE: 2.0,
        Type.ICE: 2.0,
        Type.FLYING: 2.0,
        Type.BUG: 2.0,
        Type.FIGHTING: 0.5,
        Type.GROUND: 0.5,
        Type.STEEL: 0.5,
    }
    GHOST = {
        Type.PSYCHIC: 2.0,
        Type.GHOST: 2.0,
        Type.DARK: 0.5,
        Type.NORMAL: 0.0,
    }
    DRAGON = {Type.DRAGON: 2.0, Type.STEEL: 0.5, Type.FAIRY: 0.0}
    DARK = {
        Type.PSYCHIC: 2.0,
        Type.GHOST: 2.0,
        Type.FIGHTING: 0.5,
        Type.DARK: 0.5,
        Type.FAIRY: 0.5,
    }
    STEEL = {
        Type.ICE: 2.0,
        Type.ROCK: 2.0,
        Type.FAIRY: 2.0,
        Type.FIRE: 0.5,
        Type.WATER: 0.5,
        Type.ELECTRIC: 0.5,
        Type.STEEL: 0.5,
    }
    FAIRY = {
        Type.FIGHTING: 2.0,
        Type.DRAGON: 2.0,
        Type.DARK: 2.0,
        Type.FIRE: 0.5,
        Type.POISON: 0.5,
        Type.STEEL: 0.5,
    }
    STELLAR = {}

    def __repr__(self):
        return self.name