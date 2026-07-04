from typing import Callable

import random

from rstt.player import PlayerTVS, GaussianPlayer
from rstt.stypes import SPlayer

from project.scene import Role


DEFAULT_WEIGHTS = {role: 1.0 for role in Role}
DEFAULT_DIST = {role: lambda: random.uniform(0,1) for role in Role}

class MetaData():
    def __init__(self, blue: PlayerTVS = GaussianPlayer("Blue", 1500), red: PlayerTVS = GaussianPlayer("Red", 1500),
                 weights: dict[Role, float] = DEFAULT_WEIGHTS, weights_dist: dict[Role, Callable[[], float]] = DEFAULT_DIST,
                 weights_sum: float = 1) -> None:
        # Importance of role in meta
        self._weights = weights
        self._weights_dist = weights_dist
        self._sum = weights_sum

        # Importance of side in meta
        self._blue = blue
        self._red = red
        
        self._normalize_weights()

    def update(self, weights: bool = True, blue: bool = True, red: bool = True) -> None:
        if weights:
            self._update_weights()
        if blue:
            self._update_blue()
        if red:
            self._update_red()

    def blue(self) -> SPlayer:
        return self._blue

    def red(self) -> SPlayer:
        return self._red

    def weights(self) -> dict[Role, float]:
        return self._weights

    def weight(self, role: Role) -> float:
        return self._weights[role]
    
    def set_weights(self, weights: dict[Role, float]):
        self._weights.update(weights)

    def _update_blue(self):
        self._blue.update_level()

    def _update_red(self):
        self._red.update_level()

    def _update_weights(self):
        self._weights.update({role: dist() for role, dist in self._weights_dist.items()})
        self._normalize_weights()
        
    def _normalize_weights(self):
        ratio = self._sum / sum(self._weights.values())
        self._weights = {role: weight * ratio for role, weight in self._weights.items()}
