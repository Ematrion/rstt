from rstt import Ranking
from gpr import RegionalRatings, GlobalHandler, GPRElo
from rstt.stypes import Inference, Observer, RatingSystem, SPlayer


class GlobalRanking(Ranking):
    def __init__(self, name: str, players: list[SPlayer] | None = None):
        super().__init__(name, datamodel=RegionalRatings(...),
                         backend=GPRElo(...),
                         handler=GlobalHandler(...),
                         players=players)

    def forward(self, *args, **kwargs):
        ...
