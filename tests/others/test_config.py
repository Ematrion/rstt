import pytest

from rstt import Player, BasicPlayer, Match, Duel, BetterWin
import rstt.config as cfg

import numpy as np
import math



@pytest.fixture
def p0():
    return Player('p0', 1500)

@pytest.fixture
def p1():
    return Player('p1', 1500)


def test_duel_history_default_not_tracking(p0, p1):
    duel = Duel(p0, p1)
    BetterWin().solve(duel)
    assert duel not in p0.games()
    
def test_duel_history_default_set_tracking(p0, p1):
    cfg.DUEL_HISTORY = True
    duel = Duel(p0, p1)
    cfg.DUEL_HISTORY = False
    BetterWin().solve(duel)
    assert duel in p0.games()
    
'''
NOTE: Currently rstt solvers are only define for the Duel class


def test_match_history_default(p0, p1):
    match = Match([[p0], [p1]])
    BetterWin().solve(match)
    assert match not in p0.games()

def test_match_history_default_set_tracking(p0, p1):
    cfg.MATCH_HISTORY = True
    match = Match([[p0], [p1]])
    cfg.MATCH_HISTORY = False
    BetterWin().solve(match)
    assert match in p0.games()
'''


def test_basicPlayer_default_gaussian_args():
    players = [BasicPlayer(f'player_{i}') for i in range(1000)]
    levels = [player.level() for player in players]
    
    assert np.average(levels) == pytest.approx(cfg.PLAYER_GAUSSIAN_MU, 0.1)
    assert math.sqrt(np.var(levels)) == pytest.approx(cfg.PLAYER_GAUSSIAN_SIGMA, 0.1)
    
def test_basicPlayer_set_gaussian_args():
    new_mu = 1000
    new_sigma = 100
    
    cfg.PLAYER_DIST_ARGS['mu'] = new_mu
    cfg.PLAYER_DIST_ARGS['sigma'] = new_sigma
    players = [BasicPlayer(f'player_{i}') for i in range(1000)]
    cfg.PLAYER_DIST_ARGS['mu'] = cfg.PLAYER_GAUSSIAN_MU
    cfg.PLAYER_DIST_ARGS['sigma'] = cfg.PLAYER_GAUSSIAN_SIGMA
    
    levels = [player.level() for player in players]
    
    assert np.average(levels) == pytest.approx(new_mu, 0.1)
    assert math.sqrt(np.var(levels)) == pytest.approx(new_sigma, 0.1)

