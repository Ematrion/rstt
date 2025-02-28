import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.knockout import SingleEliminationBracket as SEB


power = 8
total = 2**power
population = Player.create(nb=total)
seeding = BTRanking('Seedings', players=population)

test_data = [(2**i, i) for i in range(1, power+1)]

'''
    test balanced_tree
    
    
'''

@pytest.mark.parametrize("nb", [i for i in range(2, total+1) if i%2 == 1])
def test_initialise_error(nb):
    seb = SEB(f"test error {nb}", seeding, BetterWin())
    seb.registration(population[:nb])
    with pytest.raises(AssertionError):
        seb._initialise()

@pytest.mark.parametrize("nb_part, nb_r", test_data)
def test_nb_rounds(nb_part, nb_r):
    seb = SEB(f"test part {nb_part}", seeding, BetterWin())
    seb.registration(population[:nb_part])
    seb.run()
    assert len(seb.games(by_rounds=True)) == nb_r

@pytest.mark.parametrize("nb", [2**i for i in range(1, power+1)])    
def test_nb_games(nb):
    seb = SEB(f"test games {nb}", seeding, BetterWin())
    seb.registration(population[:nb])
    seb.run()
    assert len(seb.games()) == nb-1