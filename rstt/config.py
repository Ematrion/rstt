"""_summary_

_extended_summary_
"""

import random



# -------------------- #
# --- Player cfg ----- #
# -------------------- #

# BasicPlayer 
PLAYER_GAUSSIAN_MU = 1500 
"""Deafault mu of :class:`PLAYER_DIST_ARGS`"""
PLAYER_GAUSSIAN_SIGMA = 500
"""Deafault sigma of :class:`PLAYER_DIST_ARGS`"""

PLAYER_DIST = random.gauss
"""Default level generator used by :func:`rstt.player.basicplayer.BasicPlayer.create` when param 'level_dist' is None"""
PLAYER_DIST_ARGS = {'mu': PLAYER_GAUSSIAN_MU,
                    'sigma': PLAYER_GAUSSIAN_SIGMA}
"""Default args for level generator used by :func:`rstt.player.basicplayer.BasicPlayer.create` when param 'level_params' is None"""


# GaussianPlayer

# ExpPlayer

# tracking game history 
MATCH_HISTORY = False
DUEL_HISTORY = False

# -------------------- #
# ---- Match cfg ----- #
# -------------------- #

# -------------------- #
# ---- Solver cfg ---- #
# -------------------- #

LOGSOLVER_BASE = 10
LOGSOLVER_LC = 400



# -------------------- #
# --- Competition ---- #
# -------------------- #

# EventStanding Inferer
EVENTSTANDING_DEFAULT_POINTS = {}