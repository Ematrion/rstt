from typing import List, Optional
from typeguard import typechecked

import abc

import rstt.config as cfg
from rstt.stypes import SMatch
from rstt.player import Player
import rstt.utils.functions as uf

import numpy as np
import random


class PlayerTVS(Player, metaclass=abc.ABCMeta):
    def __init__(self, name: Optional[str] = None, level: Optional[float] = None) -> None:
        """Player with time varying level.

        The class introduce a mechanism for Player to change their level during simulation while maintaining the ability to track their match properly.
        Their is only one abstract method to implement when inheriting from it, the :func:`rstt.player.playerTVS.PlayerTVS._update_level`

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : float, optional
            The level/skill/strenght of the player. By default None, in this case a level is randomly generated.
        """
        super().__init__(name=name, level=level)
        # ??? redundancy with self.__level_history[-1]
        self.__current_level = self._BasicPlayer__level
        self.__level_history = [self.__current_level]
        self._Player__games = [None]

    # --- getter --- #
    def level_history(self) -> List[float]:
        """Getter for the player's level's evolution.

        Returns
        -------
        List[float]
            All the level the player had in chronological order
        """
        return self.__level_history

    def original_level(self) -> float:
        """The first level

        Sugar for PlayerTVS.level_history()[0]

        Returns
        -------
        float
            The original level (at instanciation)
        """
        return self._BasicPlayer__level

    def level_in(self, game: SMatch) -> float:
        """The level a player displayed in a given game

        Parameters
        ----------
        game : SMatch
            A match to query the player's level in.

        Returns
        -------
        float
            The player's level in the given game.
        """
        return self.__level_history[self._Player__games.index(game)]

    # --- setter --- #
    def update_level(self, *args, **kwars) -> None:
        """Method to update the player's level
        """
        self._update_level(*args, **kwars)
        self.__level_history.append(self.__current_level)
        self._Player__add_game(None)

    # --- override --- #
    def level(self) -> float:
        """Getter method for the player's level

        Returns
        -------
        float
            The current level of the player.
        """
        return self.__current_level

    def games(self) -> list[SMatch]:
        """Getter method for match the player participated in

        Returns
        -------
        List[Match]
            All the matches the player played in chronolgical order, from oldest to the most recent.
        """
        return [game for game in self.games() if game != None]

    def add_game(self, *args, **kwars) -> None:
        """Adds match to the player history

        Parameters
        ----------
        match : Match
            A match to track.

        Raises
        ------
        ValueError
            The match needs to be a game in which the player partipiated in and not already tracked. Either condition violated will raise an Error.
        """
        super().add_game(*args, **kwars)
        self.__level_history.append(self.__current_level)

    def reset(self):
        # TODO: check how to match the Player.reset() param calls
        self._reset_level()
        super().reset()
        self.__level_history.append(self.__current_level)

    # --- internal mechanism --- #
    def _reset_level(self) -> None:
        self.__level_history = []
        self.__current_level = self._BasicPlayer__level

    @abc.abstractmethod
    def _update_level(self) -> None:
        '''change the self.__current_level value'''


class ExponentialPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: Optional[str] = None,
                 start: Optional[float] = None,
                 final: Optional[float] = None,
                 tau: Optional[float] = None):
        """Player with a level that tends to a final value.

        The transition to the final level is controlled by an exponential decay function.

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        start : float, optional
            The initial level of the player. By default None, in this case a level is randomly generated.
        final : float, optional
            The final level of the player. By default None, in this case a level is randomly generated.
        tau : float, optional
            Controls how fast (number of level update) the player's level gets close to its final level.

        Example
        -------
        The figure below shows a population of 10 players generated with .create() without specifics params.

        .. image:: img/playertvs/ExponentialPlayer.pdf
            :width: 800

        """

        start = start if start is not None else cfg.EXPONENTIAL_START_DIST(
            **cfg.EXPONENTIAL_START_ARGS)
        super().__init__(name=name, level=start)

        self.__final = final if final is not None else self.original_level(
        ) + cfg.EXPONENTIAL_DIFF_DIST(**cfg.EXPONENTIAL_DIFF_ARGS)

        # parameters of the relaxation
        self.__tau = tau if tau else cfg.EXPONENTIAL_TAU_DIST(
            **cfg.EXPONENTIAL_TAU_ARGS)
        # relaxation
        self._relax = uf.exponential_decay

        self.__time = 0

    def _update_level(self, *args, **kwars) -> float:
        self.__time += 1
        self._PlayerTVS__current_level = self.__final - \
            (self.__final - self._PlayerTVS__current_level) * \
            self._relax(time=self.__time, tau=self.__tau)


class LogisticPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: Optional[str] = None,
                 start: Optional[float] = None,
                 final: Optional[float] = None,
                 center_x: Optional[float] = None,
                 r: Optional[float] = None):
        """Player with a level that tends to a final value.

        The transition to the final level is controlled by a logistic function.

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        start : float, optional
            The initial level of the player. By default None, in this case a level is randomly generated.
        final : float, optional
            The final level of the player. By default None, in this case a level is randomly generated.
        center_x : float, optional
            Number of level update for the player to reach the level:=(final-start)/2, by default 100.
        r : float, optional
            Controls the sharpness of the level transition, by default 0.5.

        Example
        -------
        The figure below shows a population of 10 players generated with .create() without specifics params.

        .. image:: img/playertvs/LogisticPlayer.pdf
            :width: 800
        """

        start = start if start is not None else cfg.LOGISTIC_START_DIST(
            **cfg.LOGISTIC_START_ARGS)
        super().__init__(name=name, level=start)
        self.__final = final if final is not None else self.original_level(
        ) + cfg.LOGISTIC_DIFF_DIST(**cfg.LOGISTIC_DIFF_ARGS)
        self.__time = 0
        self._relax = uf.verhulst

        # parameters of the relaxation
        center_x = center_x if center_x else cfg.LOGISTIC_CENTER_DIST(
            **cfg.LOGISTIC_CENTER_ARGS)
        self.__r = r if r else cfg.LOGISTIC_R_DIST(**cfg.LOGISTIC_R_ARGS)
        self.__tau = uf.a_from_logistic_center(center_x, self.__r)

    def _update_level(self, *args, **kwars) -> float:
        self.__time += 1
        self._PlayerTVS__current_level += self._relax(K=self.__final - self._PlayerTVS__current_level,
                                                      a=self.__tau, r=self.__r, t=self.__time, shift=0)


class CyclePlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: Optional[str] = None,
                 level: Optional[float] = None,
                 sigma: Optional[float] = None,
                 tau: Optional[int] = None):
        """Cycle Player

        Implement the 'Cycle Model' descirbed by
        Aldous D. in 'Elo ratings and the Sports Model: A Negleted Topic in Applied Probability?' [section 4.1]

        Cycle player have a deterministic level evolution in cycle.
        The variance of the level is given by the attribute __sigma^2,
        while the attribute __tau indicates the number of game needed for the level to decrease
        from its maximum to its avergae value.

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : float, optional
            The mean level, by default None, int this case a level is randomly generated
        sigma : float, optional
            The standard deviation of the level, by default 1.0
        tau : int, optional
            The number of update needed for a level to decrease from its maximal value to its mean level, by default 100

        Example
        -------
        The figure below shows a population of 10 players generated with .create() without specifics params.

        .. image:: img/playertvs/CyclePlayer.pdf
            :width: 800
        """
        super().__init__(name, level)
        self.__time = 0
        # controls the 'variance'
        self.__sigma = sigma if sigma else cfg.CYCLE_SIGMA_DIST(
            **cfg.CYCLE_SIGMA_ARGS)
        # controls the cycle duration
        self.__tau = tau if tau else cfg.CYCLE_TAU_DIST(**cfg.CYCLE_TAU_ARGS)

    def _update_level(self, *args, **kwars):
        X0 = self._BasicPlayer__level
        self.__time += 1
        self._PlayerTVS__current_level = X0 + \
            uf.deterministic_cycle(
                mu=X0, sigma=self.__sigma, tau=self.__tau, time=self.__time)


class JumpPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: Optional[str] = None,
                 level: Optional[float] = None,
                 sigma: Optional[float] = None,
                 tau: Optional[int] = None):
        """Jump Player

        Implement a 'Jump Model' adapted from
        Aldous D. in 'Elo ratings and the Sports Model' [section 4.3]
        The implementation differs from the source document by allowing a player to 'jumpe' mulitple times as simulation progress, and not just once. 

        A JumpPlayer level remains constant for an amount of time given by a geometric distribution
        before 'jumping' to a new level given by a Normal distribution.

        In practice, calling the :func:`rstt.player.playerTVS.PlayerTVS.update_level` will often result in no level changes.


        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : float, optional
            The initial level, by default None, int this case a level is randomly generated.
        sigma : float, optional
            Standard deviantion of the level changes, by default 1.0.
            Remark that the mean level changes is 0, as a consequences the player's level as equal chances to increase or decrease.
        tau : int, optional
            Parameter of the geometric distribution, by default 400.
            This will tune the tendancy that a player has to stay at a level before the level is updated.

        Example
        -------
        The figure below shows a population of 10 players generated with .create() without specifics params.

        .. image:: img/playertvs/JumpPlayer.pdf
            :width: 800
        """
        super().__init__(name, level)
        self.__sigma = sigma if sigma else cfg.JUMP_SIGMA_DIST(
            **cfg.JUMP_SIGMA_ARGS)
        self.__tau = tau if tau else cfg.JUMP_TAU_DIST(**cfg.JUMP_TAU_ARGS)
        self.__timer = np.random.geometric(1/self.__tau)

    def _update_level(self, *args, **kwars):
        self.__tictac()
        self.__jump()

    def __tictac(self) -> None:
        self.__timer -= 1

    def __jump(self):
        if self.__timer == 0:
            # new timer
            self.__timer = np.random.geometric(1/self.__tau)
            # new level
            self._PlayerTVS__current_level += random.gauss(0, self.__sigma)


# TODO: add the Ornstein-Uhlenbeck model from D. Aldous


# TODO: add learning effect model proposed by  B. Düring & Cie
# source: https://arxiv.org/pdf/1806.06648
# source: https://arxiv.org/pdf/2204.10260
