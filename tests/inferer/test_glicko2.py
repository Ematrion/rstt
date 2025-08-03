import pytest

from rstt.ranking.rating import Glicko2Rating, GlickoRating
from rstt.ranking.inferer import Glicko2


# Input
rating = Glicko2Rating(1500, 200, 0.06)
opponents = [Glicko2Rating(1400, 30, None),
             Glicko2Rating(1550, 100, None),
             Glicko2Rating(1700, 300, None)]
scores = [1, 0, 0]
glicko2 = Glicko2(tau=0.5)


# Table values
mu_j = [-0.5756, 0.2878, 1.1513]
phi_j = [0.1727, 0.5756, 1.7269]
G_j = [0.9955, 0.9531, 0.7242]
E_j = [0.639, 0.432, 0.303]


def test_scaling():
    # Example calculation - Converting to the Glicko-2 scale
    g2r = glicko2._step2(rating)
    assert g2r.mu == pytest.approx(0, 0.0001)
    assert g2r.sigma == pytest.approx(1.1513, 0.0001)


@pytest.mark.parametrize("rating, r, RD", zip(opponents, mu_j, phi_j))
def test_step2(rating, r, RD):
    # scaling for opponent j=1,2,3
    g2r = glicko2._step2(rating)
    assert g2r.mu == pytest.approx(r, 0.0001)  # column mu_j
    assert g2r.sigma == pytest.approx(RD, 0.0001)  # column phi_j


@pytest.mark.parametrize("phi, g", zip(phi_j, G_j))
def test_G(phi, g):
    assert glicko2.G(phi) == pytest.approx(g, 0.0001)


@pytest.mark.parametrize("mu, phi, e", zip(mu_j, phi_j, E_j))
def test_expectedScore(mu, phi, e):
    scaled = glicko2._step2(rating)
    r = GlickoRating(mu, phi)
    assert glicko2.expectedScore(scaled, r) == pytest.approx(e, 0.001)


def test_v():
    r = glicko2._step2(rating)
    rs = [glicko2._step2(opp) for opp in opponents]
    games = zip(rs, scores)
    assert glicko2.d2(r, games) == pytest.approx(1.7785, 0.001)  # !!! 1.778976


def test_step4():
    r = glicko2._step2(rating)
    rs = [glicko2._step2(opp) for opp in opponents]
    games = list(zip(rs, scores))
    v = glicko2.d2(r, games)
    assert glicko2._step4(r, games, v) == pytest.approx(-0.4834, abs=0.0006)


def test_step5():
    r = glicko2._step2(rating)
    rs = [glicko2._step2(opp) for opp in opponents]
    games = list(zip(rs, scores))
    v = glicko2.d2(r, games)
    delta = glicko2._step4(r, games, v)
    vol = glicko2._step5(r.sigma**2, 0.06**2, v, delta**2)
    assert vol == pytest.approx(0.05999, abs=0.0001)


def test_step6():
    assert glicko2._step6(1.1513, 0.05999) == pytest.approx(
        1.152863, abs=0.00001)


def test_step7():
    r = glicko2._step2(rating)
    rs = [glicko2._step2(opp) for opp in opponents]
    games = list(zip(rs, scores))
    mu, phi = glicko2._step7(rating=r, phi_star=1.1513, v=1.7785, games=games)
    assert phi == pytest.approx(0.8722, abs=0.001)
    assert mu == pytest.approx(-0.2069, abs=0.001)
