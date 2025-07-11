"""Configuration module for rstt simulation default behaviours.

This module contains 'global' variables used as default values in functions and classes across the rstt package.
It offers a simple approach to tune behaviour of simulations once instead of passing identical parameters multiple times in different function calls.

.. warning::
    The module is a work in progress with limited test. Bugs are expected.
    
    
Example
-------
.. code-block:: python
    :linenos:
    
    from rstt import Player
    import rstt.config as cfg
    
    
    cfg.PLAYER_DIST_ARGS['mu'] = 2000
    cfg.PLAYER_DIST_ARGS['sigma'] = 50

    # create players with an average level of approximatively 2000 and a standard deviation of 50.
    players = Player.create(nb=10)
"""

import random


# -------------------- #
# --- Player cfg ----- #
# -------------------- #

# --- BasicPlayer --- #
PLAYER_GAUSSIAN_MU = 1500
"""Deafault mu of :class:`PLAYER_DIST_ARGS`"""

PLAYER_GAUSSIAN_SIGMA = 500
"""Deafault sigma of :class:`PLAYER_DIST_ARGS`"""

PLAYER_DIST = random.gauss
"""Default level generator used by :func:`rstt.player.basicplayer.BasicPlayer.create` when param 'level_dist' is None"""

PLAYER_DIST_ARGS = {'mu': PLAYER_GAUSSIAN_MU,
                    'sigma': PLAYER_GAUSSIAN_SIGMA}
"""Default args for level generator used by :func:`rstt.player.basicplayer.BasicPlayer.create` when param 'level_params' is None"""


# -------------------- #
# --- Player TVS ----- #
# -------------------- #
TIME_SCALE = 100

# --- GaussianPlayer --- #
GAUSSIAN_PLAYER_MEAN_MEAN = 1500
"""Deafault mu of :class:`GAUSSIAN_PLAYER_MEAN_ARGS`"""

GAUSSIAN_PLAYER_MEAN_SIGMA = 500
"""Deafault sigmaof :class:`GAUSSIAN_PLAYER_MEAN_ARGS`"""

GAUSSIAN_PLAYER_SIGMA_MEAN = 100
"""Deafault mu of :class:`GAUSSIAN_PLAYER_SIGMA_ARGS`"""

GAUSSIAN_PLAYER_SIGMA_SIGMA = 50
"""Deafault sigma of :class:`GAUSSIAN_PLAYER_SIGMA_ARGS`"""

GAUSSIAN_PLAYER_MEAN_DIST = random.gauss
"""Default mean level generator used by :class:`rstt.player.gaussian.GaussianPlayer` when param 'mu' is None"""

GAUSSIAN_PLAYER_SIGMA_DIST = random.gauss
"""Default level standard deviation generator used by :class:`rstt.player.gaussian.GaussianPlayer` when param 'sigma' is None"""

GAUSSIAN_PLAYER_MEAN_ARGS = {'mu': GAUSSIAN_PLAYER_MEAN_MEAN,
                             'sigma': GAUSSIAN_PLAYER_MEAN_SIGMA}
"""Default args for mean level generator used by :class:`rstt.player.gaussian.GaussianPlayer` when param 'mu' is None"""

GAUSSIAN_PLAYER_SIGMA_ARGS = {'mu': GAUSSIAN_PLAYER_SIGMA_MEAN,
                              'sigma': GAUSSIAN_PLAYER_SIGMA_SIGMA}
"""Default args for level deviation generator used by :class:`rstt.player.gaussian.GaussianPlayer` when param 'sigma' is None"""


# --- ExpPlayer --- #
EXPONENTIAL_START_MEAN = 1500
EXPONENTIAL_START_SIGMA = 500
EXPONENTIAL_DIFF_MEAN = 0
EXPONENTIAL_DIFF_SIGMA = 500
EXPONENTIAL_TAU_MEAN = 5*TIME_SCALE
EXPONENTIAL_TAU_SIGMA = 2.5*TIME_SCALE
EXPONENTIAL_START_ARGS = {'mu': EXPONENTIAL_START_MEAN,
                          'sigma': EXPONENTIAL_START_SIGMA}
EXPONENTIAL_DIFF_ARGS = {'mu': EXPONENTIAL_DIFF_MEAN,
                         'sigma': EXPONENTIAL_DIFF_SIGMA}
EXPONENTIAL_TAU_ARGS = {'mu': EXPONENTIAL_TAU_MEAN,
                        'sigma': EXPONENTIAL_TAU_SIGMA}
EXPONENTIAL_START_DIST = random.gauss
EXPONENTIAL_DIFF_DIST = random.gauss
EXPONENTIAL_TAU_DIST = random.gauss


# --- LogisticPlayer --- #
LOGISTIC_START_MEAN = 1500
LOGISTIC_START_SIGMA = 500
LOGISTIC_DIFF_MEAN = 0
LOGISTIC_DIFF_SIGMA = 500
LOGISTIC_CENTER_MEAN = TIME_SCALE / 2
LOGISTIC_CENTER_SIGMA = TIME_SCALE / 4
LOGISTIC_R_MEAN = 0.2
LOGISTIC_R_SIGMA = 0.1
LOGISTIC_START_ARGS = {'mu': LOGISTIC_START_MEAN,
                       'sigma': LOGISTIC_START_SIGMA}
LOGISTIC_DIFF_ARGS = {'mu': LOGISTIC_DIFF_MEAN,
                      'sigma': LOGISTIC_DIFF_SIGMA}
LOGISTIC_CENTER_ARGS = {'mu': LOGISTIC_CENTER_MEAN,
                        'sigma': LOGISTIC_CENTER_SIGMA}
LOGISTIC_R_ARGS = {'mu': LOGISTIC_R_MEAN,
                   'sigma': LOGISTIC_R_SIGMA}
LOGISTIC_START_DIST = random.gauss
LOGISTIC_DIFF_DIST = random.gauss
LOGISTIC_CENTER_DIST = random.gauss
LOGISTIC_R_DIST = random.gauss


# --- CyclePlayer --- #
CYCLE_APPROX_NB_CYCLE = 5
CYCLE_LEVEL_MEAN = 1500
CYCLE_LEVEL_SIGMA = 500
CYCLE_SIGMA_MEAN = 200
CYCLE_SIGMA_SIGMA = 400
CYCLE_TAU_MEAN = TIME_SCALE / CYCLE_APPROX_NB_CYCLE
CYCLE_TAU_SIGMA = TIME_SCALE / (CYCLE_APPROX_NB_CYCLE * 2)
CYCLE_LEVEL_ARGS = {'mu': CYCLE_LEVEL_MEAN,
                    'sigma': CYCLE_LEVEL_SIGMA}
CYCLE_SIGMA_ARGS = {'mu': CYCLE_SIGMA_MEAN,
                    'sigma': CYCLE_SIGMA_SIGMA}
CYCLE_TAU_ARGS = {'mu': CYCLE_TAU_MEAN,
                  'sigma': CYCLE_TAU_SIGMA}
CYCLE_LEVEL_DIST = random.gauss
CYCLE_SIGMA_DIST = random.gauss
CYCLE_TAU_DIST = random.gauss

# --- JumpPlayer --- #
JUMP_LEVEL_MEAN = 1500
JUMP_LEVEL_SIGMA = 500
JUMP_SIGMA_MEAN = 100
JUMP_SIGMA_SIGMA = 50
JUMP_TAU_MEAN = TIME_SCALE / 10
JUMP_TAU_SIGMA = TIME_SCALE / 50
JUMP_LEVEL_ARGS = {'mu': JUMP_LEVEL_MEAN,
                   'sigma': JUMP_LEVEL_SIGMA}
JUMP_SIGMA_ARGS = {'mu': JUMP_SIGMA_MEAN,
                   'sigma': JUMP_SIGMA_SIGMA}
JUMP_TAU_ARGS = {'mu': JUMP_TAU_MEAN,
                 'sigma': JUMP_TAU_SIGMA}
JUMP_LEVEL_DIST = random.gauss
JUMP_SIGMA_DIST = random.gauss
JUMP_TAU_DIST = random.gauss


# -------------------- #
# ---- Match cfg ----- #
# -------------------- #

# tracking game history
MATCH_HISTORY = False
"""Default behaviour of the :class:`rstt.game.match.Match` when param 'tracking' is None.
If set to True, the Match instance will 'try' to add the match to its participants game history.  
"""

DUEL_HISTORY = False
"""Default behaviour of the :class:`rstt.game.match.Duel` when param 'tracking' is None.
If set to True, the Duel instance will 'try' to add the match to its participants game history.  
"""


# -------------------- #
# ---- Solver cfg ---- #
# -------------------- #

LOGSOLVER_BASE = 10
"""Default base of :class:`rstt.solver.solvers.LogSolver` when param 'base' is None"""

LOGSOLVER_LC = 400
"""Default logistic constant of :class:`rstt.solver.solvers.LogSolver` when param 'lc' is None """

# -------------------- #
# --- Competition ---- #
# -------------------- #

# EventStanding Inferer
EVENTSTANDING_DEFAULT_POINTS = {}
"""Default points dictionary of :class:`rstt.ranking.inferer.EventStanding` when param 'default' is None.

The empty dictionary means that if you instanciate an EventStanding without providing a value for 'the default' parameter
and later call the :func:`rstt.ranking.inferer.add_event` without providing a value for the 'points' parameter, you may aswell just not passan 'event' value.
Or even not call the method at all as the corresponding added event will be ignored by the inferer. 
"""
