"""Modules for Inferer
It include impleentation of the Elo and Glicko rating system
"""

from .elo import Elo
from .glicko import Glicko
from .glicko2 import Glicko2
from .playerlevel import PlayerLevel
from .playerwinprc import PlayerWinPRC
from .eventscoring import EventScoring


__all__ = [
    "Elo",
    "Glicko",
    "Glicko2",
    "PlayerLevel",
    "PlayerWinPRC",
    "EventScoring"
]
