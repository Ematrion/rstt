from typing import Optional
from typeguard import typechecked

import rstt.config as cfg
from .playerTVS import PlayerTVS

import random


class GaussianPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: Optional[str] = None, mu: Optional[float] = None, sigma: Optional[float] = None) -> None:
        """Player with a level following a gaussian distribution

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        mu : float, optional
            The player's mean level,  also considered as the 'original' level. By default None, in this case a level is generated
            using a random distribution :class:`rstt.config.GAUSSIAN_PLAYER_MEAN_DIST with default parameters :class:`rstt.config.GAUSSIAN_PLAYER_MEAN_ARGS`

        sigma : float, optional
            The player's level standard deviation. By default None, in this case a random value is generated
            using a random distribution :class:`rstt.config.GAUSSIAN_PLAYER_SIGMA_DIST with default parameters :class:`rstt.config.GAUSSIAN_PLAYER_SIGMA_ARGS`

        Example
        -------
        The figure below shows a population of 10 players generated with .create() without specifics params.

        .. image:: img/playertvs/GaussianPlayer.pdf
            :width: 800
        """

        # Genereate if needed a mu value
        mu = mu if mu is not None else cfg.GAUSSIAN_PLAYER_MEAN_DIST(
            **cfg.GAUSSIAN_PLAYER_MEAN_ARGS)

        # pass mu as level to Player
        super().__init__(name=name, level=mu)

        # generate if needed a sigma value
        self.__sigma = sigma if sigma is not None else cfg.GAUSSIAN_PLAYER_SIGMA_DIST(
            **cfg.GAUSSIAN_PLAYER_SIGMA_ARGS)

    def _update_level(self, *args, **kwars) -> None:
        self._PlayerTVS__current_level = random.gauss(
            self._BasicPlayer__level, self.__sigma)
