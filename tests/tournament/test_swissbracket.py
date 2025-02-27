import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.swissbracket import SwissBracket
from rstt.utils import matching as um

population = Player.seeded_players(16)
seeding = BTRanking('Seedings', population)

class Chord6:
    def generate(self, status, *args, **kwargs):
        return um.chord_diagrams_n6(status)

@pytest.fixture
def sbf():
    sb = SwissBracket('test', seeding=seeding, solver=BetterWin(), generators={(2,2): Chord6()})
    sb.registration(population)
    sb.run()
    return sb
    


def test_initialise_error():
    pop = Player.create(nb=32)
    seeds = BTRanking('Seeds', pop)
    sb = SwissBracket('test', seeds, BetterWin())
    sb.registration(pop)
    with pytest.raises(AssertionError):
        sb._initialise()

def test_nb_rounds(sbf):
    assert len(sbf.games(by_rounds=True)) == 5

def test_nb_games(sbf):
    assert len(sbf.games()) == 33