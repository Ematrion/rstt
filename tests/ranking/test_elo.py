import pytest
from collections import namedtuple

from rstt import Player, Duel
from rstt.ranking.standard import BasicElo
from rstt.solver import WIN, LOSE

EloParam = namedtuple('EloParam', 'player, prior, posteriori')


def decide_outcome(game, score):
    game._Match__set_result(score)


@pytest.fixture
def p1():
    return EloParam(Player('p1'), 1200, 1207.2)

@pytest.fixture
def p2():
    return EloParam(Player('p2'), 1000, 992.8)

@pytest.fixture
def p3():
    return EloParam(Player('p2'), 1200, 1177.2)

@pytest.fixture
def p4():
    return EloParam(Player('p2'), 1000, 1022.8)

@pytest.fixture
def elo():
    return BasicElo(name='test', k=30, lc=400, base=10)

@pytest.fixture
def games(p1, p2, p3, p4):
    duel1 = Duel(p1.player, p2.player)
    duel2 = Duel(p3.player, p4.player)
    decide_outcome(duel1, WIN)
    decide_outcome(duel2, LOSE)
    return [duel1, duel2]

def test_elo_with_examples(elo, p1, p2, p3, p4, games):
    for p in [p1, p2, p3, p4]:
        elo.set_rating(p.player, p.prior)
        
    elo.update(games=games)
    
    for p in [p1, p2, p3, p4]:
        assert elo.rating(p.player) == pytest.approx(p.posteriori, 0.01)