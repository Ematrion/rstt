import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.knockout import DoubleEliminationBracket as DEB

power = 8
total = 2**power
population = Player.create(nb=total)
seeding = BTRanking('Seedings', players=population)


def test_games_error_lower_and_upper():
    deb = DEB('test', seeding, BetterWin())
    with pytest.raises(ValueError):
        deb.games(lower=True, upper=True)
    
@pytest.mark.parametrize("nb", [2**i for i in range(1, power+1)]) 
def test_nb_games(nb):
    deb = DEB('test', seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    # WikiPedia:
    # The number of games in a double-elimination tournament is one or two less than twice the number of teams participating (e.g. 8 teams would see 14 or 15 games).
    # https://en.wikipedia.org/wiki/Double-elimination_tournament (20.02.2025)
    assert len(deb.games()) == 2*nb-2

@pytest.mark.parametrize("nb", [2**i for i in range(1, power+1)]) 
def test_nb_rounds(nb):
    # NOTE: The test is build on deb.upper being an 'already tested' SingleEliminationBracket
    deb = DEB('test', seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    '''
    for every round in the upper bracket except the final
    there is a corresponding lower and a following injector round
    In the end, a grand final round is played
    '''
    upper_rounds = len(deb.games(by_rounds=True, upper=True))
    assert len(deb.games(by_rounds=True)) == upper_rounds + 2*(upper_rounds-1)+1

@pytest.mark.parametrize("nb", [2**i for i in range(1, power+1)]) 
def test_get_upper_games(nb):
    deb = DEB('test', seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert deb.upper.games() == deb.games(upper=True)

@pytest.mark.parametrize("nb", [2**i for i in range(1, power+1)]) 
def test_get_lower_games(nb):
    deb = DEB('test', seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    upper_games = set(deb.games(upper=True))
    lower_games = set(deb.games(lower=True))
    all_games = set(deb.games())
    assert upper_games.intersection(lower_games) == set() and upper_games.union(lower_games) == all_games