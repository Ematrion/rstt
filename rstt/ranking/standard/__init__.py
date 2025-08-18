"""Implement classic and usefull Ranking System
"""

from .consensus import BTRanking, WinRate
from .basicOS import BasicOS
from .basicElo import BasicElo
from .basicGlicko import BasicGlicko, BasicGlicko2
from .successRanking import SuccessRanking


__all__ = [
    "BTRanking",
    "WinRate",
    "BasicOS",
    "BasicElo",
    "BasicGlicko",
    "BasicGlicko2",
    "SuccessRanking"
]
