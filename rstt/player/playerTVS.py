from typing import List
from typeguard import typechecked

import abc

from rstt.player import Player

import random

class PlayerTVS(Player, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwars):
        super().__init__(*args, **kwars)
        self.__current_level = self._Player__level
        self.__level_history = []
        self.__params = kwars # level evolution parameters
        
    # --- getter --- #
    def level_history(self) -> List[float]:
        return self.__level_history
    
    def original_level(self) -> float:
        return self._Player__level
    
    def params(self):
        return self.__params
    
    # --- override --- #
    def level(self):
        return self.__current_level
    
    # --- internal mechanism --- #
    @abc.abstractmethod
    def update_level(self, *args, **kwars) -> None:
        '''change the self.__current_level value'''


class GaussianPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: str, mu: float, sigma: float):
        # pass mu as level to Player, and mu/sigam as params to PlayerTVS
        super().__init__(name, mu, mu=mu, sigma=sigma)
        self.__mu = mu
        self.__sigma = sigma
        
    def update_level(self, *args, **kwars) -> None:
        self._PlayerTVS__current_level = random.gauss(self.__mu, self.__sigma)