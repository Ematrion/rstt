from typing import List, Callable
from typeguard import typechecked

from rstt import Duel
from rstt.stypes import Score
import rstt.utils.functions as uf

from rstt.config import LOGSOLVER_BASE, LOGSOLVER_LC

import random



'''

    TODO:
    - Extend match to Many-Versus-Many match
    - Extend match to Free-for-all
    - LEVEL_MIXTURES: define differents ways to mix levels in a teams, sum/avg/median/ and set a parameters to tune it solvers
    - Create const value for standard score (maybe enum types) i.e Score.win := [1,0]| Score.lose := [0,1]/ Score.draw := [0.5, 0.5]
    - Work on Score type
    - Add predict() to solvers (and to the stypes.Solver Protocol ?)

'''


WIN = [1.0, 0.0]
LOSE = [0.0, 1.0]
DRAW = [0.5, 0.5]

        
class BetterWin:
    def __init__(self, with_draw: bool=False):
        self.with_draw = with_draw
        self.win = WIN
        self.lose = LOSE
        self.draw = DRAW
        
    def solve(self, duel: Duel, *args, **kwars) -> None:
        level1, level2 = duel.player1().level(), duel.player2().level()
        if level1 > level2:
            score = self.win
        elif level1 < level2:
            score = self.lose
        elif self.with_draw:
            score = self.draw
        else:
            score = self.win
        duel._Match__set_result(result=score)
                

class ScoreProb:
    @typechecked
    def __init__(self, scores: List[Score], func: Callable[[Duel], Score]):
        self.scores = scores
        self.probabilities = func
    
    def solve(self, duel: Duel, *args, **kwars) -> None:
        score = random.choices(population=self.scores, 
                               weights=self.probabilities(duel),
                               k=1)[0]
        duel._Match__set_result(score)


class WeightedScore(ScoreProb):
    def __init__(self, scores: List[Score], weights: List[float]):
        if len(scores) != len(weights):
            msg = f"length of scores ({len(scores)}) does not match length of weights ({len(weights)})"
            raise ValueError(msg)
        super().__init__(scores=scores, func= lambda x: weights)


class CoinFlip(WeightedScore):
    def __init__(self):
        super().__init__(scores=[WIN, LOSE], weights=[0.5, 0.5])
        

class BradleyTerry(ScoreProb):
    def __init__(self):
        super().__init__(scores=[WIN, LOSE], func=self.__probabilities)
    
    def __probabilities(self, duel: Duel) -> List[float]:
        level1 = duel.teams()[0][0].level()
        level2 = duel.teams()[1][0].level()
        prob = uf.bradleyterry(level1, level2)
        return [prob, 1-prob]


class LogSolver(ScoreProb):
    def __init__(self, base: float=LOGSOLVER_BASE, lc: float=LOGSOLVER_LC):
        super().__init__(scores=[WIN, LOSE], func=self.__probabilities)
        self.base = base
        self.lc = lc
    
    def __probabilities(self, duel: Duel) -> List[float]:
        level1 = duel.teams()[0][0].level()
        level2 = duel.teams()[1][0].level()
        prob = uf.logistic_elo(base=self.base, diff=level1-level2, constant=self.lc)
        return [prob, 1-prob]

