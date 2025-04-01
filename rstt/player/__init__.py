"""Modules defining SPlayer

SPlayer is the notion of competitors facing each others. They are elemts of :class:`rstt.ranking.ranking.Ranking`, and participants in :class:`rstt.stypes.SMatch`
"""


from .basicplayer import BasicPlayer
from .player import Player
from .playerTVS import PlayerTVS, ExponentialPlayer, LogisticPlayer, CyclePlayer, JumpPlayer
from .gaussian import GaussianPlayer
