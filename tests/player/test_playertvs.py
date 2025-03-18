import pytest

from rstt import Duel, BetterWin
from rstt.player.playerTVS import PlayerTVS

import copy



class DummyTVS(PlayerTVS):
    def __init__(self, name: str, levels: list[float]) -> None:
        levels = copy.copy(levels)
        level = levels.pop(0)
        super().__init__(name=name, level=level)
        self.future = levels
    
    def _update_level(self):
        self._PlayerTVS__current_level = self.future.pop(0)

# --- Const --- #
DEPTH = 10
INC = 100
START = 1000
LEVELS = [START+INC*i for i in range(DEPTH)]

# --- Fixture --- #
@pytest.fixture
def pTVS0():
    return DummyTVS(name='DummyTVS_0', levels=LEVELS)

@pytest.fixture
def pTVS1():
    return DummyTVS(name='DummyTVS_1', levels= [START for _ in range(DEPTH)])

# --- TEST --- #
@pytest.mark.parametrize("timer", [i for i in range(1, DEPTH)])
def test_update_level(pTVS0, timer):
    level = pTVS0.level()
    for i in range(timer):
        pTVS0.update_level()
    assert level != pTVS0.level()
    
@pytest.mark.parametrize("timer", [i for i in range(DEPTH)])
def test_level(pTVS0, timer):
    for i in range(timer):
        pTVS0.update_level()
    assert pTVS0.level() == LEVELS[timer]
 
@pytest.mark.parametrize("timer", [i for i in range(DEPTH)])   
def test_level_in(pTVS0, pTVS1, timer):
    duel = Duel(pTVS0, pTVS1, tracking=True)
    for i in range(timer):
        pTVS0.update_level()
    BetterWin().solve(duel)
    assert pTVS0.level_in(duel) == pTVS0.level() == LEVELS[timer]

@pytest.mark.parametrize("timer", [i for i in range(DEPTH)])
def test_original_level(pTVS0, timer):
    for i in range(timer):
        pTVS0.update_level()
    assert pTVS0.original_level() == LEVELS[0]

@pytest.mark.parametrize("timer", [i for i in range(DEPTH)])
def test_level_history(pTVS0, timer):
    for i in range(timer):
        pTVS0.update_level()
    assert pTVS0.level_history() == LEVELS[:timer+1]
    
#def test_reset():
#    ...
    
