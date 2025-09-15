from rstt import Ranking, RoundRobin, LogSolver
from rstt.stypes import SPlayer, Solver

from typing import Callable


def one_round_robin(name: str, seeding: Ranking, population: list[SPlayer] | None = None, solver: Solver = LogSolver):
    population = population if population else seeding.players()
    cup = RoundRobin(name, seeding, solver)
    cup.registration(population)
    cup.run()
    return {'event': cup}


def regional_round_robins(name: str, seeding: Ranking, population: list[list[SPlayer]], solver: Solver = LogSolver):
    cups = []

    for i, pop in enumerate(population):
        cup = RoundRobin(f"{name}_region_{i}", seeding, solver)
        cup.registration(pop)
        cup.run()
        cups.append(cup)

    return {'events': cups}


def run_and_update(experiment, name: str, seeding: Ranking, tests: list[Ranking], depth: int, *args, **kwargs):
    results = {test.name: {0: [test.point(p) for p in test]}
               for test in tests}
    for i in range(depth):
        data = experiment(f"{name}_event_{i+1}", seeding, *args, **kwargs)

        for test in tests:
            test.update(**data)
            results[test.name][i+1] = [test.point(p) for p in test]

    return results
