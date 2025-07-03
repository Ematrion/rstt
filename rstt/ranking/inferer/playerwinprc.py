from rstt.stypes import SPlayer

from typeguard import typechecked

import numpy as np


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
