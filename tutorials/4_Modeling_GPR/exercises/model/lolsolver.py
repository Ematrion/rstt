from rstt import Duel, ScoreProb, WIN, LOSE

from typing import Callable


class LoLSolver(ScoreProb):
    def __init__(self, func: Callable[[Duel], list[float]]):
        super().__init__(scores=[WIN, LOSE], func=func)

    def probabilities(self, duel: Duel) -> list[float]:
        ...
