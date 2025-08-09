from rstt import Player, Duel, BetterWin
from rstt.solver.solvers import WIN, LOSE, DRAW

p1 = Player('p1', 2000)
p2 = Player('p2', 1000)
p3 = Player('p3', 1000)


def test_BetterWin_win():
    game = Duel(p1, p2)
    BetterWin().solve(game)
    assert game.scores() == WIN


def test_BetterWin_lose():
    game = Duel(p2, p1)
    BetterWin().solve(game)
    assert game.scores() == LOSE


def test_BetterWin_draw():
    game = Duel(p2, p3)
    BetterWin(with_draw=True).solve(game)
    assert game.scores() == DRAW


def test_BetterWin_home_advantage():
    game = Duel(p3, p2)
    BetterWin().solve(game)
    assert game.scores() == WIN
