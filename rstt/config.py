import random



# -------------------- #
# --- Player cfg ----- #
# -------------------- #

# BasicPlayer 
PLAYER_GAUSSIAN_MU = 1500
PLAYER_GAUSSIAN_SIGMA = 500

PLAYER_DIST = random.gauss
PLAYER_DIST_ARGS = {'mu': PLAYER_GAUSSIAN_MU,
                    'sigma': PLAYER_GAUSSIAN_SIGMA}

# GaussianPlayer

# ExpPlayer



# -------------------- #
# --- Solver cfg ----- #
# -------------------- #

LOGSOLVER_BASE = 10
LOGSOLVER_LC = 400