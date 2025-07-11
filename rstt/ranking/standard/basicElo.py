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
        """Simple Elo System


        Attributes
        ----------
        datamodel: :class:`rstt.ranking.datamodel.KeyModel` (float as rating type)
        backend: :class:`rstt.ranking.inferer.Elo`
        handler: :class:`rstt.ranking.observer.GameByGame`


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        default : float, optional
            Datamodel parameter, a default elo rating, by default 1500.0
        k : float, optional
            Backend parameter, the K value, by default 20.0
        lc : float, optional
            Backend parameter, constant dividing the ratings difference in the expected score formula , by default 400.0
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
        super().__init__(name=name,
                         datamodel=KeyModel(default=default),
                         backend=Elo(k=k, lc=lc, base=base),
                         handler=GameByGame(),
                         players=players)
