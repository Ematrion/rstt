from rstt import Ranking
from rstt.stypes import SPlayer


def init_results(pop: list[SPlayer], ranking: Ranking):
    data = {}
    for p in pop:
        data[p] = {'elo': [ranking.rating(p)], 'rho': [p.level()]}
    return data


def track_results(pop: list[SPlayer], ranking: Ranking, results: dict[SPlayer, dict[str, any]]):
    for p in pop:
        results[p]['elo'].append(ranking.rating(p))
        results[p]['rho'].append(p.level())
