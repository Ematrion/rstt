from typing import List, Any, Optional, Callable
from typeguard import typechecked

from rstt import Duel
import rstt.utils.functions as uf

import random



'''

    TODO:
    - Extend match to Many-Versus-Many match
    - Extend match to Free-for-all
    - LEVEL_MIXTURES: define differents ways to mix levels in a teams, sum/avg/median/ and set a parameters to tune it solvers
    - Create const value for standard score (maybe enum types) i.e Score.win := [1,0]| Score.lose := [0,1]/ Score.draw := [0.5, 0.5]

'''

WIN = [1.0, 0.0]
LOSE = [0.0, 1.0]
DRAW = [0.5, 0.5]

class BetterWin():
    def __init__(self, with_draw: bool=False):
        self.with_draw = with_draw
        self.win = WIN
        self.lose = LOSE
        self.draw = DRAW
        
    def solve(self, duel: Duel) -> None:
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
                
        
class BradleyTerry():
    # !!! Only works for Duel
    def __init__(self, scores: Optional[Any]=[WIN, LOSE], func: Optional[Callable]=None):
        self._scores = scores
        self._func = func if func else self.__probabilities
    
    def __probabilities(self, match=Duel) -> List[float]:
        level1 = match.teams()[0][0].level()
        level2 = match.teams()[1][0].level()
        return [uf.bradleyterry(level1, level2), 
                uf.bradleyterry(level2, level1)]
    
    @typechecked
    def solve(self, duel: Duel) -> None:
        score = random.choices(population=self._scores, 
                               weights=self._func(match=duel),
                               k=1)[0]
        duel._Match__set_result(result=score)


