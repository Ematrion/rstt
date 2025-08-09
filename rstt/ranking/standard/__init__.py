"""Implement classic and usefull Ranking System
"""

from .consensus import BTRanking, WinRate
from .basicOS import BasicOS
from .basicElo import BasicElo
from .basicGlicko import BasicGlicko
from .successRanking import SuccessRanking


__all__ = [
    BTRanking,
    WinRate,
    BasicOS,
    BasicElo,
    BasicGlicko,
    SuccessRanking,
]
