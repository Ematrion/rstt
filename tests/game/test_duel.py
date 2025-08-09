import pytest

from rstt import Player, Duel, BetterWin
from rstt.solver.solvers import WIN, LOSE, DRAW


@pytest.fixture
def p1():
    return Player('p1', 2000)


@pytest.fixture
def p2():
    return Player('p2', 1500)


@pytest.fixture
def p3():
    return Player('p3', 1500)


@pytest.fixture
def p1_versus_p2(p1, p2):
    return Duel(p1, p2)


@pytest.fixture
def p2_versus_p1(p2, p1):
    return Duel(p2, p1)


@pytest.fixture
def p1_beats_p2(p1, p2):
    duel = Duel(p1, p2)
    BetterWin().solve(duel)
    return duel


@pytest.fixture
def p2_loses_p1(p2, p1):
    duel = Duel(p2, p1)
    BetterWin().solve(duel)
    return duel

# --- TESTING --- #


def test_contains(p1, p2, p1_versus_p2):
    assert p1 in p1_versus_p2 and p2 in p1_versus_p2


def test_players(p1, p2, p1_versus_p2):
    assert p1_versus_p2.players() == [p1, p2]


def test_teams(p1, p2, p1_versus_p2):
    assert p1_versus_p2.teams() == [[p1], [p2]]


def test_opponent_player1(p1_versus_p2):
    assert p1_versus_p2.opponent(
        p1_versus_p2.player1()) == p1_versus_p2.player2()


def test_opponent_player2(p1_versus_p2):
    assert p1_versus_p2.opponent(
        p1_versus_p2.player1()) == p1_versus_p2.player2()


def test_opponent_error(p1_versus_p2):
    with pytest.raises(KeyError):
        p1_versus_p2.opponent(p3)


def test_live(p1_versus_p2):
    assert p1_versus_p2.live()


@pytest.mark.parametrize("result", [WIN, LOSE, DRAW, [5.0, -10.43]])
def test_played_not_live(p1_versus_p2, result):
    p1_versus_p2._Match__set_result(result)
    assert not p1_versus_p2.live()


@pytest.mark.parametrize("result", [1, 1.0, 'win', True, {}, (1, 1)])
def test_set_result_must_be_list(p1_versus_p2, result):
    with pytest.raises(TypeError):
        p1_versus_p2._Match__set_result(result)


@pytest.mark.parametrize("result", [['win', 'lose'], [True, False], {'a': 1, 'b': 2}, (1, 1)])
def test_set_result_must_be_list_of_float(p1_versus_p2, result):
    with pytest.raises(TypeError):
        p1_versus_p2._Match__set_result(result)


@pytest.mark.parametrize("result", [[1.0], [1.0, 1.0, 1.0]])
def test_set_result_lenght_2(p1_versus_p2, result):
    with pytest.raises(ValueError):
        p1_versus_p2._Match__set_result(result)


@pytest.mark.parametrize("result", [WIN, LOSE, DRAW])
def test_set_result_success(p1_versus_p2, result):
    p1_versus_p2._Match__set_result(result)


def test_no_winner(p1_versus_p2):
    assert not p1_versus_p2.winner()


def test_no_loser(p1_versus_p2):
    assert not p1_versus_p2.loser()


def test_play_error(p1_beats_p2):
    with pytest.raises(RuntimeError):
        BetterWin().solve(p1_beats_p2)


def test_winner(p1_beats_p2, p2_loses_p1, p1):
    assert p1_beats_p2.winner() == p1
    assert p2_loses_p1.winner() == p1


def test_loser(p1_beats_p2, p2_loses_p1, p2):
    assert p1_beats_p2.loser() == p2
    assert p2_loses_p1.loser() == p2


def test_no_draw(p1_beats_p2, p2_loses_p1, p1_versus_p2):
    assert not p1_versus_p2.isdraw()
    assert not p1_beats_p2.isdraw()
    assert not p2_loses_p1.isdraw()


def test_draw(p1, p2):
    duel = Duel(p1, p2)
    duel._Match__set_result(DRAW)
    assert duel.isdraw()


@pytest.mark.parametrize("score", [WIN, LOSE, DRAW])
def test_scores(p1_versus_p2, score):
    p1_versus_p2._Match__set_result(score)
    assert p1_versus_p2.scores() == score


@pytest.mark.parametrize("score,ranks", [(WIN, [1, 2]), (LOSE, [2, 1]), (DRAW, [1, 1])])
def test_ranks(score, ranks, p1_versus_p2):
    p1_versus_p2._Match__set_result(score)
    assert p1_versus_p2.ranks() == ranks
