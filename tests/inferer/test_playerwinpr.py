import pytest

import rstt.config as cfg
from rstt import Player, BetterWin, Duel

# from rstt.ranking.inferer import PlayerWinPRC
from rstt.new_ranking.standard.consensus import PlayerWinPRC


@pytest.fixture
def p1():
    return Player('p1', 1000)


@pytest.fixture
def p2():
    return Player('p2', 2000)


@pytest.fixture
def p3():
    return Player('p3', 3000)


@pytest.mark.parametrize("_1v2, _2v3", [(5, 10), (10, 5)])
def test_PlayerWinPr_rate(p1, p2, p3, _1v2, _2v3):
    cfg.DUEL_HISTORY = True
    for nb, (player1, player2) in zip([_1v2, _2v3], [(p1, p2), (p2, p3)]):
        for _ in range(nb):
            duel = Duel(player1, player2)
            BetterWin().solve(duel)
    assert PlayerWinPRC().rate(p2) == pytest.approx(_1v2 / (_1v2 + _2v3) * 100, 0.01)
    cfg.DUEL_HISTORY = False
