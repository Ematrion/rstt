import math

def bradleyterry(level1, level2):
    #https://en.wikipedia.org/wiki/Bradley–Terry_model
    return level1/(level1 + level2)

def logistic_elo(base, diff, constant):
    # https://wismuth.com/elo/calculator.html
    return 1.0 / (1.0 + math.pow(base, -diff/constant))

def normal_elo(diff):
    # TODO: add parametrization
    # https://wismuth.com/elo/calculator.html
    # https://fr.wikipedia.org/wiki/Fonction_d%27erreur_complémentaire
    return math.erfc(-diff/((2000.0/7)*math.sqrt(2)))/2
