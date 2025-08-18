import pytest
from collections import namedtuple

from rstt import Player, Duel
from rstt.ranking.standard import BasicGlicko2
from rstt.ranking.rating import Glicko2Rating
from rstt.solver import WIN, LOSE


GlickoParam = namedtuple('GlickoParam', 'player, prior, posteriori')


def decide_outcome(game, score):
    game._Match__set_result(score)


@pytest.fixture
def player():
    return GlickoParam(Player('player'),
                       Glicko2Rating(1500, 200, 0.06),
                       Glicko2Rating(1464.06, 151.52, 0.05999))


@pytest.fixture
def p1():
    return GlickoParam(Player('p1'),
                       Glicko2Rating(1400, 30, 0.6),
                       None)


@pytest.fixture
def p2():
    return GlickoParam(Player('p2'),
                       Glicko2Rating(1550, 100, 0.6),
                       None)


@pytest.fixture
def p3():
    return GlickoParam(Player('p3'),
                       Glicko2Rating(1700, 300, 0.6),
                       None)


@pytest.fixture
def games(player, p1, p2, p3):
    duel1 = Duel(player.player, p1.player)
    duel2 = Duel(player.player, p2.player)
    duel3 = Duel(player.player, p3.player)
    decide_outcome(duel1, WIN)
    decide_outcome(duel2, LOSE)
    decide_outcome(duel3, LOSE)
    return [duel1, duel2, duel3]


@pytest.fixture
def glicko2():
    return BasicGlicko2(name='test-glicko-2', tau=0.5)


def test_glicko2__with_paper_example(glicko2, player, p1, p2, p3, games):
    # the test: glicko2 user interface
    for p in [player, p1, p2, p3]:
        glicko2.set_rating(p.player, p.prior)
    glicko2.update(games=games)

    # verification
    computed = glicko2.rating(player.player)
    targeted = player.posteriori
    assert computed.mu == pytest.approx(targeted.mu, abs=0.01)
    assert computed.sigma == pytest.approx(targeted.sigma, abs=0.01)
    assert computed.volatility == pytest.approx(
        targeted.volatility, abs=0.00001)
