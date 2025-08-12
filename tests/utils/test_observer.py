import pytest

from rstt import BasicPlayer, Duel, BTRanking, RoundRobin, BetterWin, SingleEliminationBracket
from rstt.utils.observer import to_list_of_games, to_list_of_players, duel_data, players_records


@pytest.fixture
def pop():
    return BasicPlayer.create(nb=16)


@pytest.fixture
def p1(pop):
    return pop[0]


@pytest.fixture
def gt(pop):
    return BTRanking('GT', players=pop)


@pytest.fixture
def duel(pop):
    d = Duel(pop[0], pop[1])
    BetterWin().solve(d)
    return d


@pytest.fixture
def bunch_of_games(pop):
    games = []
    solver = BetterWin()
    for p1 in pop:
        for p2 in pop:
            if p1 != p2:
                duel = Duel(p1, p2)
                solver.solve(duel)
                games.append(duel)

    return games


@pytest.fixture
def roundrobin(gt):
    cup = RoundRobin('tournament', gt, BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def seb(gt):
    cup = SingleEliminationBracket('tournament', gt, BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


# --- TEST --- #
def test_to_list_of_games_from_game(duel):
    returned_value = to_list_of_games(game=duel)
    assert len(returned_value) == 1
    assert set([duel]) == set(returned_value)


def test_to_list_of_games_from_games(bunch_of_games):
    returned_value = to_list_of_games(games=bunch_of_games)
    assert len(returned_value) == len(bunch_of_games)
    assert set(bunch_of_games) == set(returned_value)


def test_to_list_of_games_from_event(roundrobin):
    returned_value = to_list_of_games(event=roundrobin)
    assert len(returned_value) == len(roundrobin.games())
    assert set(roundrobin.games()) == set(returned_value)


def test_to_list_of_games_from_events(roundrobin, seb):
    returned_value = to_list_of_games(events=[roundrobin, seb])
    assert len(returned_value) == len(roundrobin.games()) + len(seb.games())
    assert set(roundrobin.games()+seb.games()) == set(returned_value)


def test_to_list_of_player_from_player(p1):
    returned_value = to_list_of_players(player=p1)
    assert len(returned_value) == 1
    assert set([p1]) == set(returned_value)


def test_to_list_of_player_from_players(pop):
    returned_value = to_list_of_players(players=pop)
    assert len(returned_value) == len(pop)
    assert set(pop) == set(returned_value)


def test_to_list_of_player_from_team(p1):
    returned_value = to_list_of_players(team=p1)
    assert len(returned_value) == 1
    assert set([p1]) == set(returned_value)


def test_to_list_of_player_from_teams(pop):
    returned_value = to_list_of_players(teams=pop)
    assert len(returned_value) == len(pop)
    assert set(pop) == set(returned_value)


def test_to_list_of_player_from_game(duel):
    returned_value = to_list_of_players(game=duel)
    assert len(returned_value) == 2
    assert set(duel.players()) == set(returned_value)


def test_to_list_of_player_from_games(bunch_of_games, pop):
    returned_value = to_list_of_players(games=bunch_of_games)
    assert set(pop) == set(returned_value)


def test_to_list_of_player_from_event(roundrobin):
    returned_value = to_list_of_players(event=roundrobin)
    assert set(roundrobin.participants()) == set(returned_value)


def test_to_list_of_player_from_events(roundrobin, seb):
    returned_value = to_list_of_players(events=[roundrobin, seb])
    assert set(roundrobin.participants() +
               seb.participants()) == set(returned_value)


@pytest.mark.parametrize("key", ['teams', 'scores', 'ranks'])
def test_duel_data_keys(duel, key):
    data = duel_data(duel)
    assert key in data.keys()


@pytest.mark.parametrize("key", ['teams', 'scores'])
def test_players_records_keys(duel, key):
    data, *_ = players_records([duel])
    assert key in data.keys()
