from . import stypes, config

from .player import BasicPlayer, Player, GaussianPlayer
from .game import Match, Duel
from .solver import BetterWin, BradleyTerry, CoinFlip, LogSolver, WIN, DRAW, LOSE
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

__all__ = ["stypes",
           "config",
           "BasicPlayer",
           "Player",
           "GaussianPlayer",
           "Match",
           "Duel",
           "BetterWin",
           "BradleyTerry",
           "CoinFlip",
           "LogSolver",
           "WIN",
           "DRAW",
           "LOSE",
           "Standing",
           "Ranking",
           "BTRanking",
           "BasicElo",
           "BasicGlicko",
           "BasicOS",
           "WinRate",
           "SuccessRanking",
           "Competition",
           "RoundRobin",
           "SwissRound",
           "RandomRound",
           "SwissBracket",
           "SingleEliminationBracket",
           "DoubleEliminationBracket",
           "Snake"
           ]
