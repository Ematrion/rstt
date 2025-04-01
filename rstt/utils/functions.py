import math


def bradleyterry(level1, level2):
    # https://en.wikipedia.org/wiki/Bradley–Terry_model
    return level1/(level1 + level2)


def logistic_elo(base, diff, constant):
    # https://wismuth.com/elo/calculator.html
    return 1.0 / (1.0 + math.pow(base, -diff/constant))


def normal_elo(diff):
    # TODO: add parametrization
    # https://wismuth.com/elo/calculator.html
    # https://fr.wikipedia.org/wiki/Fonction_d%27erreur_complémentaire
    return math.erfc(-diff/((2000.0/7)*math.sqrt(2)))/2


def exponential_decay(time, tau):
    # https://en.wikipedia.org/wiki/Exponential_decay
    return math.exp(-time/tau)


def verhulst(K, a, r, t, shift):
    # https://fr.wikipedia.org/wiki/Fonction_logistique_(Verhulst)
    t -= shift
    return K / (1 + a*math.exp(-r*t))


def logistic_symetrical_center(a, r, k):
    # https://fr.wikipedia.org/wiki/Fonction_logistique_(Verhulst)
    return math.log(a)/r, k/2


def a_from_logistic_center(center, r):
    return math.exp(center * r)


def deterministic_cycle(mu, sigma, tau, time):
    # from D. Aldous 'Elo Ratings and the Sport Model'
    return math.pow(2, 1/2)*sigma*math.sin(mu + (math.pi/(2*tau))*time)
