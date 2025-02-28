from typing import List, Dict, Any, Callable
from typeguard import typechecked

import abc

from rstt.player import Player
import rstt.utils.functions as uf

import numpy as np
import random

class PlayerTVS(Player, metaclass=abc.ABCMeta):
    def __init__(self, name: str, level: float) -> None:
        super().__init__(name=name, level=level)
        self.__current_level = self._BasicPlayer__level
        self.__level_history = []
        
    # --- getter --- #
    def level_history(self) -> List[float]:
        return self.__level_history
    
    def original_level(self) -> float:
        return self._BasicPlayer__level
    
    # --- override --- #
    def level(self) -> float:
        return self.__current_level
    
    # --- internal mechanism --- #
    @abc.abstractmethod
    def update_level(self, *args, **kwars) -> None:
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
        
    def Update_level(self, *args, **kwars) -> float:
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

