from rstt.ranking import Ranking
from rstt.ranking.datamodel import KeyModel
from rstt.ranking.inferer import PlayerLevel, PlayerWinPRC
from rstt.ranking.observer import PlayerChecker
from rstt.stypes import SPlayer


import numpy as np


class BTRanking(Ranking):
    def __init__(self, name: str = '', players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(factory=lambda x: x.level()),
                         backend=PlayerLevel(),
                         handler=PlayerChecker(),
                         players=players)


class WinRate(Ranking):
    def __init__(self, name: str,
                 default: float = -1.0,
                 scope: float = np.iinfo(np.int32).max,
                 players: list[SPlayer] | None = None):
        super().__init__(name,
                         datamodel=KeyModel(default=default),
                         backend=PlayerWinPRC(default=default, scope=scope),
                         handler=PlayerChecker(),
                         players=players)

    def forward(self, *args, **kwargs):
        self.handler.handle_observations(
            datamodel=self.datamodel, infer=self.backend, ranking=self)
