import pytest

from rstt import Player, Duel, RoundRobin, LogSolver, BTRanking
from rstt.ranking.observer.game_observer import GameByGame
from rstt.ranking.inferer import Elo, Glicko


# Observer to test
gbg = GameByGame()

# Inference system to support
elo = Elo()
glicko = Glicko()

# --- data input to test


@pytest.fixture
def p1():
    return Player('p1', 1000)


@pytest.fixture
def p2():
    return Player('p2', 1500)


@pytest.fixture
def p3():
    return Player('p3', 2000)


@pytest.fixture
def duel(p1, p2):
    a_duel = Duel(p1, p2)
    LogSolver().solve(a_duel)
    return a_duel


@pytest.fixture
def duels(p1, p2):
    encounters = []
    for i in range(5):
        encounter = Duel(p1, p2)
        LogSolver().solve(encounter)
        encounters.append(encounter)
    return encounters


@pytest.fixture
def rr(p1, p2, p3):
    cup = RoundRobin('rr', seeding=BTRanking('dummy'), solver=LogSolver())
    cup.registration([p1, p2, p3])
    cup.run()
    return cup


@pytest.mark.parametrize("infer", [elo, glicko])
def test_intergration(infer, duel, duels, rr):
    ...


def test_elo_1vs1():
    ...


def test_glicko_1vs1():
    ...
