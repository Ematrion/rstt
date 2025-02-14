import pytest

from rstt import Player, Duel, BetterWin
from rstt.solver.solvers import WIN, LOSE, DRAW



# TODO: move funtion to test_match when fully supported

p1, p2, p3 = Player('p1', 2000), Player('p2', 1500), Player('p3', 1500)
duel1 = Duel(p1, p2)
duel2 = Duel(p2, p1)

def test_contains():
    assert p1 in duel1
    assert p2 in duel2
    
def test_players():
    assert duel1.players() == [p1, p2]
    assert duel2.players() == [p2, p1]
    
def test_teams():
    assert duel1.teams() == [[p1], [p2]]
    assert duel2.teams() == [[p2], [p1]]

def test_opponent_player1():
    assert duel1.opponent(duel1.player1()) == duel1.player2()
    
def test_opponent_player2():
    assert duel1.opponent(duel1.player1()) == duel1.player2()
    
def test_opponent_error():
    with pytest.raises(KeyError):
        duel1.opponent(p3)

def test_live():
    assert duel1.live() == True
    
def test_set_result_must_be_list():
    with pytest.raises(ValueError):
        duel = Duel(p3, p1)
        duel._Match__set_result(True)

def test_set_result_must_be_list_of_float():
    with pytest.raises(ValueError):
        duel = Duel(p3, p1)
        duel._Match__set_result([1, 0])
        
def test_set_result_lenght_2():
    with pytest.raises(ValueError):
        duel = Duel(p3, p1)
        duel._Match__set_result([1.0, 1.0, 0.0])
        
def test_set_result_success():
    duel = Duel(p3, p1)
    duel._Match__set_result(WIN)
        
    
def test_played_not_live():
    duel = Duel(p3, p1)
    duel._Match__set_result(WIN)
    assert duel.live() == False

def test_set_result_error():
    with pytest.raises(ValueError):
        duel1._Match__set_result(1)
    
def test_no_winner():
    assert not duel1.winner()
    
def test_no_loser():
    assert not duel1.loser()
    
def test_no_draw():
    assert not duel1.isdraw()

def test_play(): # ??? what does it test
    BetterWin().solve(duel1)
    BetterWin().solve(duel2)
  
def test_play_error():
    with pytest.raises(AttributeError):
        BetterWin().solve(duel1)
    
def test_winner():
    assert duel1.winner() == duel1.player1()
    assert duel2.winner() == duel2.player2()
    
def test_loser():
    assert duel1.loser() == duel1.player2()
    assert duel2.loser() == duel2.player1()
    
def test_no_draw():
    assert not duel1.isdraw()
    assert not duel2.isdraw()

def test_draw():
    duel = Duel(p1, p2)
    duel._Match__set_result(DRAW)
    assert duel.isdraw()
    
def test_scores():
    assert duel1.scores() == [1.0, 0.0]
    assert duel2.scores() == [0.0, 1.0]

def test_ranks():
    assert duel1.ranks() == [1, 2]
    assert duel2.ranks() == [2, 1]