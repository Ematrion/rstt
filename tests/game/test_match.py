import pytest

from rstt import Player, Match


@pytest.fixture
def team1():
    return [Player("Team1_Player1", level=1001), Player("Team1_Player2", level=1002), Player("Team1_Player3", level=1003)]


@pytest.fixture
def team2():
    return [Player("Team2_Player1", level=2001), Player("Team2_Player2", level=2002), Player("Team2_Player3", level=2003)]


@pytest.fixture
def team3():
    return [Player("Team3_Player1", level=3001), Player("Team3_Player2", level=3002)]

@pytest.fixture()
def teams(team1, team2, team3):
    return [team1, team2, team3]


@pytest.fixture
def match123(team1, team2, team3):
    return Match(teams=[team1, team2, team3])


def test_players(match123, team1, team2, team3):
    assert set(match123.players()) == set(team1+team2+team3)
    assert len(match123.players()) == len(team1+team2+team3)


def test_teams(match123, team1, team2, team3):
    assert len(match123.teams()) == 3
    assert all(team in match123.teams() for team in [team1, team2, team3])


def test_opponents_are_not_mates(match123, teams):
    for team in teams:
        for player in team:
            opps = set(match123.opponents(player))
            mates =set(match123.teammates(player))
            assert opps.intersection(mates) == set()

def test_players_are_mates_or_opponents(match123, teams):
    for team in teams:
        for player in team:
            #opponents = [other for other in teams if team != other]
            #assert set(match123.opponents(player)) == set(opponents)
            #assert len(match123.opponents(player)) == len(opponents)
            opps = set(match123.opponents(player))
            mates =set(match123.teammates(player))
            assert opps.union(mates).union({player}) == set(match123.players())
            
def test_teammates(match123, teams):
    for team in teams:
        for player in team:
            mates = set(match123.teammates(player))
            # player is not a teammate
            assert player not in mates
            # a team consist of a player and its mate
            
            assert mates.union({player}) == set(team)
