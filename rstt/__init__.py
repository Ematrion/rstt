from . import stypes, config

from .player import BasicPlayer, Player, GaussianPlayer
from .game import Match, Duel
from .solver import BetterWin, BradleyTerry, CoinFlip, LogSolver
from .ranking import (
    Standing,
    Ranking,
    BTRanking,
    BasicElo, BasicGlicko, BasicOS,
    WinRate, SuccessRanking
)
from .scheduler import (
    Competition,
    RoundRobin, SwissRound, RandomRound,
    SwissBracket,
    SingleEliminationBracket, DoubleEliminationBracket,
    Snake
)
