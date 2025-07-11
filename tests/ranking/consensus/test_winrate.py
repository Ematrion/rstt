import pytest
from rstt import WinRate, Player, BetterWin, BTRanking, RoundRobin
import rstt.config as cfg


@pytest.fixture
def pop():
    return Player.seeded_players(100)


@pytest.fixture
def wr(pop):
    return WinRate('test', players=pop)


@pytest.fixture
def gt(pop):
    return BTRanking('gt', players=pop)


def test_update(wr, gt, pop):
    cfg.DUEL_HISTORY = True
    rr = RoundRobin('data test', gt, BetterWin())
    rr.registration(pop)
    rr.run()
    wr.update()
    assert [p for p in gt] == [p for p in wr]
    cfg.DUEL_HISTORY = False
