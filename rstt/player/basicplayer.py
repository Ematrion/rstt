from typing import Dict, Any, Callable, Optional
import rstt.config as cfg

import names

class BasicPlayer():
    def __init__(self, name: Optional[str]=None, level: Optional[float]=None) -> None:
        self.__name = name if name else names.get_full_name()
        self.__level = level if level is not None else cfg.PLAYER_DIST(**cfg.PLAYER_DIST_ARGS)
    
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
    def create(cls, nb: int,
               name_gen: Optional[Callable[..., str]]=None,
               name_params: Optional[Dict[str, Any]]=None,
               level_dist: Optional[Callable[..., float]]=None,
               level_params: Optional[Dict]=None):
        name_gen = names.get_full_name if name_gen is None else name_gen
        name_params = {} if name_params is None else name_params
        level_dist = cfg.PLAYER_DIST if level_dist is None else level_dist
        level_params = cfg.PLAYER_DIST_ARGS if level_params is None else level_params
        return [cls(name=name_gen(**name_params), level=level_dist(**level_params)) for i in range(nb)]

    @classmethod
    def seeded_players(cls, nb: int, inc: float=100, start: int=1):
        levels = [i*inc for i in range(start, nb+1)]
        names = [f"Seed_{i}" for i in range(nb, 0, -1)]
        return [cls(name=name, level=level) for name, level in zip(names, levels)]