from rstt import Duel, ScoreProb, WIN, LOSE

from . import MetaData

from typing import Callable
import functools
import math


def logistic_elo(diff, base, constant):
    # https://wismuth.com/elo/calculator.html
    return 1.0 / (1.0 + math.pow(base, -diff/constant))


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
