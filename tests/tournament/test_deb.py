import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.knockout import DoubleEliminationBracket as DEB

import math

power = 8
total = 2**power
population = Player.create(nb=total)
seeding = BTRanking('Seedings', players=population)


def test_games_error_lower_and_upper():
    deb = DEB('test', seeding, BetterWin())
    with pytest.raises(ValueError):
        deb.games(lower=True, upper=True)
    
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)])
def test_player_lose_at_most_twice(nb):
    deb = DEB(f"test max 2 loses {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    losers = [game.loser() for game in deb.games()]
    for player in deb.participants():
        assert len([loser for loser in losers if loser == player]) <= 2

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_games(nb):
    deb = DEB(f"test games {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    # WikiPedia:
    # The number of games in a double-elimination tournament is one or two less than twice the number of teams participating (e.g. 8 teams would see 14 or 15 games).
    # https://en.wikipedia.org/wiki/Double-elimination_tournament (20.02.2025)
    assert len(deb.games()) == 2*nb-2

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)])
def test_nb_rounds_from_upper_lower_injector_GF(nb):
    deb = DEB(f"test nb rounds from parts {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    upper = deb.games(by_rounds=True, upper=True)
    lower = deb.games(by_rounds=True, lower=True)
    injector = deb.games(by_rounds=True, injector=True)
    assert len(deb.games(by_rounds=True)) == len(upper) + len(lower) + len(injector) + 1

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)])
def test_nb_games_from_upper_lower_injector_GF(nb):
    deb = DEB(f"test nb games from parts {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    upper = deb.games(upper=True)
    lower = deb.games(lower=True)
    injector = deb.games(injector=True)
    assert len(deb.games()) == len(upper) + len(lower) + len(injector) + 1


@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_rounds(nb):
    # NOTE: The test is build on deb.upper being an 'already tested' SingleEliminationBracket
    deb = DEB(f"test rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    '''
    for every round in the upper bracket except the first and the grand final
    there is a corresponding injector and a following lower round
    In the end, a grand final round is played
    
    The upper bracket is a simple Single Elimination Bracket.
    '''
    upper_rounds = int(math.log(nb, 2))
    assert len(deb.games(by_rounds=True)) == upper_rounds + 2*(upper_rounds-1)+1


"""@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_get_upper_games(nb):
    deb = DEB(f"test ug {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert deb.upper.games() == deb.games(upper=True)"""

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_lower_rounds(nb):
    deb = DEB(f"test lower nb rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    nbr = len(deb.games(upper = True, by_rounds=True))
    assert len(deb.games(lower=True, by_rounds=True)) == nbr - 1

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_lower_games(nb):
    deb = DEB(f"test lower nb games {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    nbr = len(deb.games(upper=True))
    assert len(deb.games(lower=True)) == nbr - nb/2

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_upper_rounds(nb):
    deb = DEB(f"test upper nb rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert len(deb.games(upper=True, by_rounds=True)) == int(math.log(nb, 2))
    
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_upper_games(nb):
    deb = DEB(f"test upper nb games {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert  len(deb.games(upper=True)) == nb-1
    
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_injector_rounds(nb):
    deb = DEB(f"test injector nb rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert len(deb.games(injector=True, by_rounds=True)) == len(deb.games(lower=True, by_rounds=True))
    
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_nb_injector_games(nb):
    deb = DEB(f"test injector nb games {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    assert  len(deb.games(injector=True)) == len(deb.games(lower=True))

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)])
def test_upper_only_winners(nb):
    deb = DEB(f"test upper only winners {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    upper_rounds = deb.games(upper=True, by_rounds=True)
    for i in range(len(upper_rounds)-2):
        winners = set([game.winner() for game in upper_rounds[i]])
        players = set([p for game in upper_rounds[i+1] for p in game.players()])
        assert players == winners
        
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)])
def test_injector_is_upper_plus_lower(nb):
    deb = DEB(f"test upper loser half of injector {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.run()
    upper_rounds = deb.games(upper=True, by_rounds=True)[1:]
    injector_rounds = deb.games(injector=True, by_rounds=True)
    lower_rounds = deb.games(lower=True, by_rounds=True)
    for upper, injector, lower in zip(upper_rounds, injector_rounds, lower_rounds):
        injector_players = set([p for game in injector for p in game.players()])
        upper_losers = set([game.loser() for game in upper])
        lower_winners = set([game.winner() for game in lower])
        assert upper_losers.intersection(injector_players) == upper_losers
        assert lower_winners.intersection(injector_players) == lower_winners
        assert upper_losers.intersection(lower_winners) == set()
        assert injector_players == lower_winners.union(upper_losers)

@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_manual_run_nb_rounds(nb):
    deb = DEB(f"test manual rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.start()
    
    nb_rounds = 0
    while deb.live():
        current_round = deb.generate_games()
        results = deb.play_games(current_round)
        deb.edit(results)
        nb_rounds += 1
        
    assert nb_rounds == len(deb.games(by_rounds=True))
    
@pytest.mark.parametrize("nb", [2**i for i in range(2, power+1)]) 
def test_manual_run_nb_games(nb):
    deb = DEB(f"test manual rounds {nb}", seeding, BetterWin())
    deb.registration(population[:nb])
    deb.start()
    
    nb_games = 0
    while deb.live():
        current_round = deb.generate_games()
        results = deb.play_games(current_round)
        deb.edit(results)
        nb_games += len(current_round)
        
    assert nb_games == len(deb.games())
        