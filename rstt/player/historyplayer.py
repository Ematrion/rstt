from typing import List, Union, Optional
from typeguard import typechecked

import abc

from rstt.stypes import Achievement
from rstt import Player, Match

import random


class HistoryPlayer(Player):
    @typechecked
    def __init__(self, name: Optional[str]=None, level: Optional[float]=None) -> None:
        super().__init__(name=name, level=level)
        self.__achievements = []
        self.__games = []
    
    # --- getter --- #
    def achievements(self) -> List[Achievement]:
        return self.__achievements
    
    def earnings(self) -> float:
        return sum([achievement.prize for achievement in self.__achievements]) 
    
    def games(self) -> List[Match]:
        return self.__games   
    
    # --- setter --- #
    @typechecked
    def collect(self, achievement: Union[Achievement, List[Achievement]]):
        if isinstance(achievement, Achievement):
            achievements = [achievement]
        
        previous_event = [past_event.event_name for past_event in self.__achievements]
        for achievement in achievements:
            if achievement not in previous_event:
                self.__achievements.append(achievement)
            else: 
                msg=f"Can not collect {achievement}. {self} already participated in an event called {achievement.event_name}"
                raise ValueError(msg)

    def reset(self) -> None:
        self.__achievements = []
        self.__games = []
        
    # --- internal mechanism --- #
    @typechecked
    def add_game(self, match: Match) -> None:
            self.__games.append(match)
            
            
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
    
    
        
        
    
    