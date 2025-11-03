from rstt import Ranking
from rstt.stypes import SPlayer

from gpr import RegionalRatings, GlobalHandler, GPRElo


class GlobalRanking(Ranking):
    def __init__(self, name: str, players: list[SPlayer] | None = None):
        super().__init__(name, datamodel=RegionalRatings(...),
                         backend=GPRElo(...),
                         handler=GlobalHandler(...),
                         players=players)

    def forward(self, *args, **kwargs):
        ...
