import pytest


# from rstt.ranking.inferer import Elo
from rstt.ranking.inferer import Elo


'''
Test based on:
https://www.geeksforgeeks.org/dsa/elo-rating-algorithm/

'''


@pytest.fixture
def elo_gfg():
    return Elo(k=30, lc=400, base=10)


@pytest.fixture
def rating1():
    return 1200


@pytest.fixture
def rating2():
    return 1000


def test_P1(rating1, rating2, elo_gfg):
    assert elo_gfg.expectedScore(
        rating1=rating1, rating2=rating2) == pytest.approx(0.76, 0.01)


def test_P2(rating1, rating2, elo_gfg):
    assert elo_gfg.expectedScore(
        rating1=rating2, rating2=rating1) == pytest.approx(0.24, 0.01)


def test_case1(rating1, rating2, elo_gfg):
    # rating1 wins
    [[new_r1], [new_r2]] = elo_gfg.rate([[rating1], [rating2]], [1, 0])
    assert new_r1 == pytest.approx(1207.2, 0.01)
    assert new_r2 == pytest.approx(992.8, 0.01)


def test_case2(rating1, rating2, elo_gfg):
    # rating2 wins
    [[new_r1], [new_r2]] = elo_gfg.rate([[rating1], [rating2]], [0, 1])
    assert new_r1 == pytest.approx(1177.2, 0.01)
    assert new_r2 == pytest.approx(1022.8, 0.01)
