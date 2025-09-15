from rstt.player import PlayerTVS, GaussianPlayer
from rstt.stypes import SPlayer

from project.scene import Role

import random


class MetaData():
    def __init__(self, weights: dict[Role, float] = {r: 1 for r in Role},
                 blue: PlayerTVS = GaussianPlayer("Blue", 1500),
                 red: PlayerTVS = GaussianPlayer("Red", 1500),
                 min_weight: float = 0.0,
                 max_weight: float = 3.0) -> None:
        # Importance of role in meta
        self._weights = weights

        # parameter for roles updates
        self._min_weight = min_weight
        self._max_weight = max_weight

        # Importance of side in meta
        self._blue = blue
        self._red = red

    def update(self, weights: dict[Role, float] | bool = True, blue: bool = True, red: bool = True) -> None:
        if weights:
            self._update_weights(weights)
        if blue:
            self._update_blue()
        if red:
            self._update_red()

    def weights(self) -> dict[Role, float]:
        return self._weights

    def weight(self, role: Role) -> float:
        return self._weights[role]

    def blue(self) -> SPlayer:
        return self._blue

    def red(self) -> SPlayer:
        return self._red

    def _update_weights(self, weights: dict[Role, float] | None = None):
        if isinstance(weights, dict):
            self._weights.update(weights)
        else:
            weights = [random.uniform(self._min_weight, self._max_weight)
                       for _ in self._weights]
            ratio = len(self._weights) / sum(weights)
            weights = [weight * ratio for weight in weights]
            self._weights = {role: weight for role,
                             weight in zip(Role, weights)}

    def _update_blue(self):
        self._blue.update_level()

    def _update_red(self):
        self._red.update_level()
