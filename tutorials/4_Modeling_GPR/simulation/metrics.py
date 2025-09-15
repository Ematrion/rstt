from rstt import Ranking, Standing
from rstt.stypes import SPlayer

from scipy import stats


def kendall(test: Ranking | Standing, reference: Ranking | Standing, population: list[SPlayer] | None):
    pop = population if population else reference.players()
    return stats.kendalltau(reference[pop], test[pop]).statistic


def spearman(test: Ranking | Standing, reference: Ranking | Standing, population: list[SPlayer] | None):
    pop = population if population else reference.players()
    skills = [reference.point(p) for p in pop]
    points = [test.points(p) for p in pop]
    return stats.spearmanr(skills, points).statistic


def rank_differences(test: Ranking | Standing, reference: Ranking | Standing, population: list[SPlayer] | None):
    ref = reference.fit(population)
    ranks = test.fit(population)
    return [ref[p] - ranks[p] for p in population]


def accuracy(test: Ranking, reference: Ranking, percentile: int, population: list[SPlayer] | None):
    threshold = int(len(population) // (100/percentile))
    return len(set(reference[:threshold]).intersection(set(test[:threshold]))) / threshold
