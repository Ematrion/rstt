from typing import List, Dict, Any, Union, Callable, Optional

from rstt.config import PLAYER_DIST, PLAYER_DIST_ARGS

import names

class Player():
    def __init__(self, name: Optional[str]=None, level: Optional[float]=None) -> None:
        self.__name = name if name else names.get_full_name()
        self.__level = level if level else PLAYER_DIST(**PLAYER_DIST_ARGS)
        
        self.__achievements = []
    
    # --- getter --- #
    def name(self) -> str:
        return self.__name
    
    def level(self) -> float:
        return self.__level
        
    # --- magic methods --- #
    def __repr__(self) -> str:
        return f"Player - name: {self.__name}, level: {self.__level}"
    
    def __str__(self) -> str:
        return self.__name
    
    @classmethod
    def create(cls, nb: int, name_gen: Callable[..., str]=names.get_full_name,
               name_params: Dict[str, Any]={},
               level_dist: Callable[..., float]=PLAYER_DIST,
               level_params=PLAYER_DIST_ARGS):
        return [cls(name=name_gen(**name_params), level=level_dist(**level_params)) for i in range(nb)]

