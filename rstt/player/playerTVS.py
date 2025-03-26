from typing import List, Optional, Callable
from typeguard import typechecked

import abc

from rstt.stypes import SMatch
from rstt.player import Player
import rstt.utils.functions as uf

import numpy as np
import random


class PlayerTVS(Player, metaclass=abc.ABCMeta):
    def __init__(self, name: Optional[str]=None, level: Optional[float]=None) -> None:
        """Player with time varying level.

        The class introduce a mechanism for Player to change their level during simulation while maintaining the ability to track their match properly.
        Their is only one abstract method to implement when inheriting from it, the :func:`rstt.player.playerTVS.PlayerTVS._update_level`

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : float, optional
            The level/skill/strenght of the player. By default None, in this case a level is randoly generated.
        """
        super().__init__(name=name, level=level)
        self.__current_level = self._BasicPlayer__level # ??? redundancy with self.__level_history[-1]
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
    def __init__(self, name: str, start: float, final: float, tau: float):
        super().__init__(name=name, level=start)
        # start to end function of time
        self.__final = final
        self.__time = 0
        self.__relax = uf.exponential_decay
        
        # parameters of the relaxation
        self.__tau = tau
        
    def update_level(self, *args, **kwars) -> float:
        self._time += 1
        self._PlayerTVS__current_level = self.__final - (self.__final - self._PlayerTVS__current_level)*self.__relax(time=self.__time, tau=self.__tau)


class LogisticPlayer(PlayerTVS):
    def __init__(self, name: str, start: float, final: float, center_x: float, r: float, shift: float=0):
        super().__init__(name=name, level=start)
        # start to end function of time
        self.__final = final
        self.__time = 0
        self._relax = uf.verhulst 
        
        # parameters of the relaxation
        self.__tau=uf.a_from_logistic_center(center_x, r)
        self.__r = r
        self.__shift = shift
 
    def update_level(self, *args, **kwars) -> float:
        self.__time += 1
        self._PlayerTVS__current_level += self._relax(K=self.__limit- self._PlayerTVS__current_level,
                                                      a=self.__tau, r=self.__r, t=self.__time, shift=self.__shift)


class CyclePlayer(PlayerTVS):
    """Cycle Player


    Implement the 'Cycle Model' descirbed in
    Aldous D. in 'Elo ratings and the Sports Model: A Negleted Topic in Applied Probability?'
    
    Cycle player have a deterministic level evolution in cycle.
    The variance of the level is given by the attribute __sigma^2,
    while the attribute __tau indicates the number of game needed for the level to decrease
    from its maximum to its avergae value

    Parameters
    ----------
    PlayerTVS : _type_
        _description_
    """
    def __init__(self, name: str, level: float=0, sigma: float=1.0, tau: int=100):
        super().__init__(name, level)
        self.__time = 0
        self.__sigma = sigma # controls the 'variance'
        self.__tau = tau # controls the cycle duration
        
    def update_level(self, *args, **kwars):
        X0 = self._BasicPlayer__level
        self.__time += 1
        self._PlayerTVS__current_level = X0 + uf.deterministic_cycle(mu=X0, sigma=self.__sigma, tau=self.__tau, time=self.__time)


class JumpPlayer(PlayerTVS):
    """Jump Player


    Implement a 'Jump Model' adapted from 
    Aldous D. in 'Elo ratings and the Sports Model'
    
    A JumpPlayer level remains constant for an amount of time given by a geometric distribution
    before 'jumping' to a new level given by a Normal distribution. 

    The class differs from the source document by jumping mulitple times as simulation progress, and not just once.    

    Parameters
    ----------
    PlayerTVS : _type_
        _description_
    """
    def __init__(self, name: str, level: float=0, sigma2: float=1.0, tau: int=400):
        super().__init__(name, level)
        self.__sigma2 = sigma2
        self.__tau = tau
        self.__timer = np.random.geometric(1/self.__tau)
    
    def update_level(self, *args, **kwars):
        self.__tictac()
        self.__jump()
    
    def __tictac(self) -> None:
        self.__timer -= 1
    
    def __jump(self):
        if self.__timer == 0:
            # new timer
            self.__timer = np.random.geometric(1/self.__tau)
            # new level
            self._PlayerTVS__current_level += random.gauss(0, self.__sigma2)

