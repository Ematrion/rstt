import pytest

from rstt import BasicPlayer, Duel, BetterWin


# players
p0, p1 = BasicPlayer('p0', 1500), BasicPlayer('p1', 1500)

# games
played_game = Duel(p0, p1)
BetterWin().solve(played_game)

unplayed_game = Duel(p0, p1)


def test_player_level(level=1500):
    player = BasicPlayer('test', level)
    assert player.level() == level

def test_player_name(name='test'):
    player = BasicPlayer(name, 1500)
    assert player.name() == name
    
