"""Package for automated matches generation procedure

We consider scheduler in competition as a very large notion including tournaments and live-matchmaking.
"""

from .tournament import Competition
from .tournament import RoundRobin, SwissRound, RandomRound, SwissBracket, SingleEliminationBracket, DoubleEliminationBracket, Snake
