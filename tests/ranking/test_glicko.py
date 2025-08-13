import pytest
from collections import namedtuple

from rstt import Player, Duel
from rstt.ranking.standard import BasicGlicko
from rstt.ranking.rating import GlickoRating
from rstt.solver import WIN, LOSE


GlickoParam = namedtuple('GlickoParam', 'player, prior, posteriori')


def decide_outcome(game, score):
    game._Match__set_result(score)


@pytest.fixture
def player():
    return GlickoParam(Player('player'),
                       GlickoRating(1500, 200),
                       GlickoRating(1464, 151.4))


@pytest.fixture
def p1():
    return GlickoParam(Player('p1'),
                       GlickoRating(1400, 30),
                       None)


@pytest.fixture
def p2():
    return GlickoParam(Player('p2'),
                       GlickoRating(1550, 100),
                       None)


@pytest.fixture
def p3():
    return GlickoParam(Player('p3'),
                       GlickoRating(1700, 300),
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
def glicko():
    return BasicGlicko(name='test-glicko')


def test_glicko2__with_paper_example(glicko, player, p1, p2, p3, games):
    # the test: glicko2 user interface
    for p in [player, p1, p2, p3]:
        glicko.set_rating(p.player, p.prior)
    glicko.update(games=games)

    # verification
    computed = glicko.rating(player.player)
    targeted = player.posteriori
    assert computed.mu == pytest.approx(targeted.mu, 0.1)
    assert computed.sigma == pytest.approx(targeted.sigma, 0.1)
