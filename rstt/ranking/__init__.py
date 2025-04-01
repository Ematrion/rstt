"""Modules for ranking purposes
"""

from . import rating

from .standing import Standing
from .ranking import Ranking

from .observer import GameByGame, BatchGame, KeyChecker
from .inferer import Elo, Glicko, PlayerLevel, PlayerWinPRC, EventStanding
from .datamodel import KeyModel, GaussianModel

from .standard import BTRanking, WinRate, SuccessRanking
from .standard import BasicElo, BasicGlicko, BasicOS
