from typing import List, Any, Optional, Callable
from typeguard import typechecked

from rstt import Match
import rstt.utils.functions as uf

import random


class BradleyTerry:
    def __init__(self, scores: Optional[Any]=[[1, 0], [0, 1]], func: Optional[Callable]=None):
        self._scores = scores
        self._func = func if func else self.__probabilities
    
    def __probabilities(self, match=Match) -> List[float]:
        level1 = match.teams()[0][0].level()
        level2 = match.teams()[1][0].level()
        return [uf.bradleyterry(level1, level2), 
                uf.bradleyterry(level2, level1)]
    
    @typechecked
    def solve(self, match: Match) -> None:
        score = random.choices(population=self._scores, 
                               weights=self._func(match=match),
                               k=1)[0]
        match._Match__set_results(result=score)


