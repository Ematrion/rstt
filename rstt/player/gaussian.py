from typeguard import typechecked

from .playerTVS import PlayerTVS

import random

class GaussianPlayer(PlayerTVS):
    @typechecked
    def __init__(self, name: str, mu: float, sigma: float) -> None:
        # pass mu as level to Player, and mu/sigam as params to PlayerTVS
        super().__init__(name=name, level=mu)
        self.__sigma = sigma
        
    def update_level(self, *args, **kwars) -> None:
        self._PlayerTVS__current_level = random.gauss(self._BasicPlayer__level, self.__sigma)