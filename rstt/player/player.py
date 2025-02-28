from typing import List, Union, Optional
from typeguard import typechecked

from rstt.player.basicplayer import BasicPlayer
from rstt.game import Match
from rstt.stypes import Achievement




class Player(BasicPlayer):
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
        else:
            achievements = achievement
        
        previous_event = [past_event.event_name for past_event in self.__achievements]
        for achievement in achievements:
            if achievement.event_name not in previous_event:
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

