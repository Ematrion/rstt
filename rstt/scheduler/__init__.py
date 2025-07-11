"""Package for automated matches generation procedure

RSTT consider scheduler in competition as a large notion covering both sport tournaments and live-matchmaking.
"""

from .tournament import Competition
from .tournament import RoundRobin, SwissRound, RandomRound, SwissBracket, SingleEliminationBracket, DoubleEliminationBracket, Snake
