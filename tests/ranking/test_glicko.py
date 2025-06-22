import pytest

from rstt.ranking.rating import GlickoRating
from rstt.ranking.inferer import Glicko

# test on glicko formula
glicko = Glicko()

# initial values
test_player = GlickoRating(mu=1500, sigma=200)
r1 = GlickoRating(mu=1400, sigma=30)
r2 = GlickoRating(mu=1550, sigma=100)
r3 = GlickoRating(mu=1700, sigma=300)

# game
opponents = [r1, r2, r3]
scores = [1, 0, 0]

# targeted values
g = [0.9955, 0.9531, 0.7242]
e = [0.639, 0.432, 0.303]
d2 = 53670.85
updated_player_rating = GlickoRating(mu=1464, sigma=151.4)


def test_G_j1():
    assert glicko.G(r1.sigma) == pytest.approx(g[0], 0.0001)


def test_G_j2():
    assert glicko.G(r2.sigma) == pytest.approx(g[1], 0.0001)


def test_G_j3():
    assert glicko.G(r3.sigma) == pytest.approx(g[2], 0.0001)


def test_E_j1():
    assert glicko.expectedScore(test_player, r1) == pytest.approx(e[0], 0.001)


def test_E_j2():
    assert glicko.expectedScore(test_player, r2) == pytest.approx(e[1], 0.001)


def test_E_j3():
    assert glicko.expectedScore(test_player, r3) == pytest.approx(e[2], 0.001)


def test_d2():
    games = [(r, s) for r, s in zip(opponents, scores)]
    assert glicko.d2(test_player, games) == pytest.approx(d2, 0.001)


def test_rate_mu():
    assert glicko.rate(test_player, opponents, scores).mu == pytest.approx(
        updated_player_rating.mu, 0.1)


def test_rate_sigmae():
    assert glicko.rate(test_player, opponents, scores).sigma == pytest.approx(
        updated_player_rating.sigma, 0.1)
