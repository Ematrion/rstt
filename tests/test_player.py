import pytest

from rstt import Player, Duel, BetterWin


# players
#pop = Player.create(nb=2)
#p0, p1 = pop
p0, p1 = Player('p0', 1500), Player('p1', 1500)

# games
played_game = Duel(p0, p1)
#played_game.play(BetterWin())
BetterWin().solve(played_game)
unplayed_game = Duel(p0, p1)

# events
#results = [('event0', 5), ('event1', 2)]
#same_event = ('event0', 8)

# cashprizes
#cash = [300, 5000]

def test_player_level(level=1500):
    player = Player('test', level)
    assert player.level() == level

def test_player_name(name='test'):
    player = Player(name, 1500)
    assert player.name() == name
    
#def test_games_not_played():
#    assert unplayed_game not in p0.games()
    
#def test_games_played():
#    assert played_game in p0.games()
    
#def test_collect():
#    for e, c  in zip(results, cash):
#        p1.collect(e, c)
#    assert p1.trophies() == results
#    assert p1.money() == sum(cash)

#def test_collect_error_event():
#    with pytest.raises(Exception):
#        p1.collect(same_event)
        
#def test_collect_error_money():
#    with pytest.raises(Exception):
#        p1.collect(['neg_money', 10], -100)

#def test_reset_games():
#    p0.reset()
#    assert played_game not in p0.games()
    
#def test_reset_all():
#    p1.reset()
#    assert p1.games() == []
#    assert p1.trophies() == []
#    assert p1.money() == 0

