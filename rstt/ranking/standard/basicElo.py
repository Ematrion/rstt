from rstt.ranking import Ranking
from rstt.ranking.datamodel import KeyModel
from rstt.ranking.inferer import Elo
from rstt.ranking.observer import GameByGame
from rstt.stypes import SPlayer

from typeguard import typechecked


class BasicElo(Ranking):
    def __init__(self, name: str, default: float = 1500,
                 k: float = 20.0,
                 lc: float = 400.0,
                 base: float = 10.0,
                 players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(default=default),
                         backend=Elo(k=k, lc=lc, base=base),
                         handler=GameByGame(),
                         players=players)
