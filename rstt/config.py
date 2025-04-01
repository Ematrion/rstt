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


# --- GaussianPlayer --- #
GAUSSIAN_PLAYER_MEAN_MEAN = 1500
"""Deafault mu of :class:`GAUSSIAN_PLAYER_MEAN_ARGS`"""

GAUSSIAN_PLAYER_MEAN_SIGMA = 500
"""Deafault sigmaof :class:`GAUSSIAN_PLAYER_MEAN_ARGS`"""

GAUSSIAN_PLAYER_SIGMA_MEAN = 250
"""Deafault mu of :class:`GAUSSIAN_PLAYER_SIGMA_ARGS`"""

GAUSSIAN_PLAYER_SIGMA_SIGMA = 250
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
EXPONENTIAL_DIFF_MEAN = 500
EXPONENTIAL_DIFF_SIGMA = 250
EXPONENTIAL_START_ARGS = {'mu': EXPONENTIAL_START_MEAN,
                          'sigma': EXPONENTIAL_START_SIGMA}
EXPONENTIAL_DIFF_ARGS = {'mu': EXPONENTIAL_DIFF_MEAN,
                         'sigma': EXPONENTIAL_DIFF_SIGMA}
EXPONENTIAL_START_DIST = random.gauss
EXPONENTIAL_DIFF_DIST = random.gauss


# --- LogisticPlayer --- #
LOGISTIC_START_MEAN = 1500
LOGISTIC_START_SIGMA = 500
LOGISTIC_DIFF_MEAN = 500
LOGISTIC_DIFF_SIGMA = 250
LOGISTIC_START_ARGS = {'mu': LOGISTIC_START_MEAN,
                       'sigma': LOGISTIC_START_SIGMA}
LOGISTIC_DIFF_ARGS = {'mu': LOGISTIC_DIFF_MEAN,
                      'sigma': LOGISTIC_DIFF_SIGMA}
LOGISTIC_START_DIST = random.gauss
LOGISTIC_DIFF_DIST = random.gauss


# --- CyclePlayer --- #


# --- JumpPlayer --- #


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
