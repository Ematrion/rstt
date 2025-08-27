import pytest

from rstt import Player, Match


@pytest.fixture
def team1():
    return Player.create(nb=3)


@pytest.fixture
def team2():
    return Player.create(nb=3)


@pytest.fixture
def team3():
    return Player.create(nb=2)


@pytest.fixture
def match123(team1, team2, team3):
    return Match(teams=[team1, team2, team3])


def test_players(match123, team1, team2, team3):
    assert set(match123.players()) == set(team1+team2+team3)
    assert len(match123.players()) == len(team1+team2+team3)


def test_teams(match123, team1, team2, team3):
    assert len(match123.teams()) == 3
    assert all(team in match123.teams() for team in [team1, team2, team3])


def test_opponents(match123, team1, team2, team3):
    teams = [team1, team2, team3]
    for team in teams:
        for player in team:
            opponents = [other for other in teams if team != other]
            assert set(match123.opponents(player)) == set(opponents)
            assert len(match123.opponents(player)) == len(opponents)


def test_teammates():
    teams = [team1, team2, team3]
    for team in teams:
        for player in team:
            teammates = [p for p in team if p != player]
            assert set(match123.teammates(player)) == set(teammates)
            assert len(match123.teammates(player)) == len(teammates)
