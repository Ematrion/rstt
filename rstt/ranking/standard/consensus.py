from rstt.ranking import Ranking
from rstt.ranking.datamodel import KeyModel
from rstt.ranking.inferer import PlayerLevel, PlayerWinPRC
from rstt.ranking.observer import PlayerChecker
from rstt.stypes import SPlayer


import numpy as np


class BTRanking(Ranking):
    def __init__(self, name: str = '', players: list[SPlayer] | None = None):
        """Consensus Ranking For the Bradley-Terry Model

        Ranking based on the player's level() method.
        This also work for Time varying player, inherited class from :class:`rstt.player.playerTVS.PlayerTVS`,
        But it needs to be updated manually everytime player's level is updated.


        Attributes
        ----------
        datamodel: :class:`rstt.ranking.datamodel.KeyModel` (float as rating type)
        backend: :class:`rstt.ranking.inferer.PlayerLevel`
        handler: :class:`rstt.ranking.observer.PlayerChecker`


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        players : _type_, optional
            SPlayer to add to the ranking, by default None

        .. warning::
            BTRanking validity is limited to Bradley-Terry like models and is not suited for simulation using 'None-transitive' level.
        """
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
        """Ranking based on Win rate


        Ranking that tracks the winrate of :class:`rstt.player.player.Player`.
        The update function does not take any parameters, win rate is computed directly with the player's game history.

        Attributes
        ----------
        datamodel :class:`rstt.ranking.datamodel.KeyModel` (float as rating)
        backend :class:`rstt.ranking.inferer.PlayerWinPRC`
        handler :class:`rstt.ranking.observer.PlayerChecker`


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        default : float, optional
            A default rating value for when player have no game in their history, by default -1.0
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
        super().__init__(name,
                         datamodel=KeyModel(default=default),
                         backend=PlayerWinPRC(default=default, scope=scope),
                         handler=PlayerChecker(),
                         players=players)
        # incase player already played games
        self.update()

    def forward(self, *args, **kwargs):
        self.handler.handle_observations(
            datamodel=self.datamodel, infer=self.backend, players=self.players())
