import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.swissbracket import SwissBracket

population = Player.create(nb=16)
seeding = BTRanking('Seedings', population)

def test_initialise_error():
    pop = Player.create(nb=32)
    seeds = BTRanking('Seeds', pop)
    sb = SwissBracket('test', seeds, BetterWin())
    sb.registration(pop)
    with pytest.raises(AssertionError):
        sb._initialise()

def test_nb_rounds():
    sb = SwissBracket('test', seeding, BetterWin())
    sb.registration(population)
    sb.run()
    assert len(sb.games(by_rounds=True)) == 5
   
def test_nb_games():
    sb = SwissBracket('test', seeding, BetterWin())
    sb.registration(population)
    sb.run()
    assert len(sb.games()) == 33