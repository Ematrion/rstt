"""Module for rating

Contains standard rating for common Ranking systems.
"""


from dataclasses import dataclass
import rstt.utils.constants as cst


@dataclass
class Elo:
    elo: float = cst.DEFAULT_ELO


@dataclass
class GlickoRating:
    mu: float = cst.GLICKO2_MEAN
    sigma: float = cst.GLICKO2_VAR


@dataclass
class Glicko2Rating:
    mean: float = cst.GLICKO2_MEAN
    variance: float = cst.GLICKO2_VAR
    volatility: float = cst.GLICKO2_VOLATILITY
