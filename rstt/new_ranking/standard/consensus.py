from rstt import Ranking, Standing
from rstt.new_ranking.observer import ObsTemplate
from rstt.new_ranking.observer.utils import *
from rstt.ranking import KeyModel
from rstt.stypes import SPlayer

from typeguard import typechecked
from typing import Optional

import numpy as np


class PlayerLevel:
    def rate(self, player: SPlayer) -> float:
        return player.level()


class PlayerWinPRC:
    def __init__(self, default: float = -1.0, scope: int = np.iinfo(np.int32).max):
        """Inferer based on Player win rate


        Parameters
        ----------
        default : float, optional
            A rating for when no game was yet played, by default -1.0
        scope : int, optional
            The number of game to consider, starting from the most recent one, by default np.iinfo(np.int32).max.
        """
        self.default = default
        self.scope = scope

    @typechecked
    def rate(self, player: SPlayer, *args, **kwargs) -> float:
        """Win rate inference

        Parameters
        ----------
        player : Player
            a player to rate

        Returns
        -------
        Dict[Player, float]
            the player and its associated rating
        """
        return self._win_rate(player)

    def _win_rate(self, player: SPlayer):
        games = player.games()
        if games:
            games = games[-self.scope:]
            nb_wins = sum([1 for game in games if player is game.winner()])
            # QUEST: How to support arbitrary game outcomes
            # ??? sum([game.score(player) for game in games])
            total = len(games)
            winrate = nb_wins / total * 100
        else:
            winrate = self.default
        return winrate


class KeyChecker(ObsTemplate):
    def __init__(self):
        super().__init__()

        self.convertor: callable = to_list_of_players
        self.extractor: callable = lambda players: [
            {PLAYER: player} for player in players]
        self.query: callable = get_rating_of_player
        self.output_formater: callable = new_player_rating
        self.push: callable = push_new_ratings


class BTRanking(Ranking):
    def __init__(self, name: str, players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(factory=lambda x: x.level()),
                         backend=PlayerLevel(),
                         handler=KeyChecker(),
                         players=players)


class WinRate(Ranking):
    def __init__(self, name: str,
                 default: float = -1.0,
                 scope: float = np.iinfo(np.int32).max,
                 players: list[SPlayer] | None = None):
        super().__init__(name,
                         datamodel=KeyModel(default=default),
                         backend=PlayerWinPRC(default=default, scope=scope),
                         handler=KeyChecker(),
                         players=players)

    def forward(self, *args, **kwargs):
        self.handler.handle_observations(
            datamodel=self.datamodel, infer=self.backend, ranking=self)
