import pytest

from rstt import Player, Duel, BetterWin
from rstt.stypes import Achievement


# players
p0, p1 = Player('p0', 1500), Player('p1', 1500)

# games
played_game = Duel(p0, p1, tracking=True)
BetterWin().solve(played_game)

# events
p0_achievements = [
    Achievement('test1', 1, 1500),
    Achievement('test2', 5, 200),
    Achievement('test3', 10, 0)
]
p1_achievements = [
    Achievement('test1', 2, 2000),
    Achievement('test2', 12, 50),
    Achievement('test3', 4, 320)
]

forbbiden_event = Achievement('test1', 10, 3000)


    
@pytest.mark.parametrize("p,achievements", [(p0, p0_achievements), (p1, p1_achievements)])
def test_collect_achievements(p, achievements):
    p.collect(achievements)
    assert p.achievements() == achievements

@pytest.mark.parametrize("p", [p0, p1])
def test_collect_event_name_error(p):
    with pytest.raises(ValueError):
        p.collect(forbbiden_event)

@pytest.mark.parametrize("p,achievements", [(p0, p0_achievements), (p1, p1_achievements)])
def test_earnings(p, achievements):
    assert p.earnings() == sum([ach.prize for ach in achievements])
    
def test_games_played():
    assert played_game in p0.games() and played_game in p1.games()

def test_reset_games():
    p0.reset()
    p1.reset()
    assert played_game not in p0.games() and played_game not in p1.games()

def test_reset_games():
    p0.reset()
    assert played_game not in p0.games()

def test_reset_all():
    p1.reset()
    assert p1.games() == []
    assert p1.achievements() == []
    assert p1.earnings() == 0


