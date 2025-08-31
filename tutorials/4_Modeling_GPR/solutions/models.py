from typing import Callable, List
from rstt import Duel
from rstt.player import PlayerTVS, GaussianPlayer
from rstt.solver import ScoreProb, WIN, LOSE
from rstt.stypes import SPlayer, Score


import functools
from enum import StrEnum
from statistics import mean
import math


def logistic_elo(base, diff, constant):
    # https://wismuth.com/elo/calculator.html
    return 1.0 / (1.0 + math.pow(base, -diff/constant))


class Role(StrEnum):
    toplaner = "Toplaner"
    jungle = "Jungle"
    midlaner = "Midlaner"
    adc = "Botlaner"
    support = "Support"


class MetaData():
    def __init__(self, weights: dict[Role, float], blue: PlayerTVS, red: PlayerTVS) -> None:
        self._weights = weights
        self._blue = blue
        self._red = red

    def update(self, weights: dict[Role, float], *args, **kwargs) -> None:
        self._weights.update(weights)  # TODO: in-place no argsw
        self._blue.update_level()
        self._red.update_level()

    def weights(self) -> dict[Role, float]:
        return self._weights

    def blue(self) -> SPlayer:
        return self._blue

    def red(self) -> SPlayer:
        return self._red


class LoLTeam(PlayerTVS):
    def __init__(self, name: str, players: dict[Role, SPlayer]) -> None:
        self._players = players.values()
        self._players_by_roles = players

        super().__init__(name, level=mean(
            [player.level() for player in self._players]))

    def level(self, weights: dict[Role, float] | None = None) -> float:
        if weights:
            levels_sum = sum([self._players_by_roles[role].level(
            )*weight for role, weight in weights.items()])
            weights_sum = sum(weights.values())
            return levels_sum/weights_sum
        else:
            return mean([player.level() for player in self._players])

    def player(self, role: Role) -> SPlayer:
        return self._players_by_roles[role]

    def _update_level(self) -> None:
        for player in self._players:
            try:
                return player.update_level()
            except AttributeError:
                continue


class LoLSolver(ScoreProb):
    def __init__(self, meta: MetaData, func: Callable[[Duel], list[float]] = functools.partial(logistic_elo, base=10, constant=600)):
        self.meta = meta
        self._probability_estimator = func
        super().__init__(scores=[WIN, LOSE], func=self.probabilities)

    def _evaluate_strenght(self, duel: Duel) -> tuple[float, float]:
        # side strenght
        blue_level = self.meta.blue().level()
        red_level = self.meta.red().level()

        # team strenght
        blue_team_level = duel.player1().level(weights=self.meta.weights())
        red_team_level = duel.player2().level(weights=self.meta.weights())

        # adjustement for side
        blue_team_level += blue_level - red_level

        return [blue_team_level, red_team_level]

    def probabilities(self, duel: Duel) -> list[float]:
        level1, level2 = self._evaluate_strenght(duel)
        return [self._probability_estimator(diff=level1-level2), self._probability_estimator(diff=level2-level1)]


# alternative: 1 team versus 1 team OR 5 time 1 player versus 1 player ?

# WIN := [1.0, 0.0]

# win, lose
# Bo3 -> [2, 0], [2, 1], [1, 2], [0, 2] or [1, 0], [2/3, 1/3], [1/3, 2/3], [0, 1]
# Bo5 -> ...  or ...
