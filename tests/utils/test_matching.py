import pytest
from rstt import BasicPlayer
from rstt.utils.matching import ruban
from rstt.utils.competition import playersToDuel


DEPTH = 30


@pytest.mark.parametrize('nb_players', list(range(2, DEPTH)))
def test_ruban_number_of_rounds(nb_players):
    players = BasicPlayer.create(nb=nb_players)
    if nb_players % 2 == 0:
        assert len(ruban(players)) == len(players)-1
    else:
        assert len(ruban(players)) == len(players)


@pytest.mark.parametrize('nb_players', list(range(2, DEPTH)))
def test_ruban_number_of_matchups(nb_players):
    players = BasicPlayer.create(nb=nb_players)
    rounds = [playersToDuel(round) for round in ruban(players)]
    games = []
    for round in rounds:
        games += round
    assert len(games) == (nb_players * (nb_players-1)) / 2


'''@pytest.mark.parametrize('nb_players', list(range(2, DEPTH)))
def test_ruban_number_of_matchups_per_player(nb_players):
    ...
'''


@pytest.mark.parametrize('nb_players', list(range(2, DEPTH)))
def test_ruban_player_plays_every_round(nb_players):
    players = BasicPlayer.create(nb=nb_players)
    rounds = ruban(players)
    for player in players:
        played_round = [r for r in rounds if player in r]
        if len(players) % 2 == 0:
            assert len(played_round) == len(rounds)
        else:
            # one bye round if odd amount of participants
            assert len(played_round) == len(rounds)-1


@pytest.mark.parametrize('nb_players', list(range(2, DEPTH)))
def test_ruban_everyone_faces_everyone_else_exactly_once(nb_players):
    players = BasicPlayer.create(nb=nb_players)
    rounds = [playersToDuel(round) for round in ruban(players)]
    games = []
    for round in rounds:
        games += round
    for player in players:
        opponents = [game.opponent(player) for game in games if player in game]
        assert len(opponents) == len(set(opponents)) == nb_players-1
