""" Solver Module

Solver provide a solve(match: SMatch) method to assign a Score to the match. Typicaly a WIN/LOSE/DRAW in case of 'versus' matches
"""


from typing import List, Optional, Callable
from typeguard import typechecked

from rstt import Duel
from rstt.stypes import Score
import rstt.utils.functions as uf

import rstt.config as cfg

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
"""Default Score Value indicating a 'win' for the first memeber of a 'versus' Match"""
LOSE = [0.0, 1.0]
"""Default Score Value indicating a 'lose' for the first memeber of a 'versus' Match"""
DRAW = [0.5, 0.5]
"""Default Score Value indicating a 'draw' between the two opponents in a 'versus' Match"""


class BetterWin:
    @typechecked
    def __init__(self, with_draw: bool = False):
        """BetterWin Solver

        Implements a deterministic Score generator.
        BetterWin always assign a Win to the best (highest level) participant of a match.

        .. warning::
            Only Supports Duel at the moment.

        Parameters
        ----------
        with_draw : bool, optional
            Wether a draw should be assigned to the game in case of equals level, by default False.
            When False, there is a 'home advantage policy' meaning that in case of equals levels, the first team of the match wins.
        """
        self.with_draw = with_draw

    @typechecked
    def solve(self, duel: Duel, *args, **kwars) -> None:
        level1, level2 = duel.player1().level(), duel.player2().level()
        if level1 > level2:
            score = WIN
        elif level1 < level2:
            score = LOSE
        elif self.with_draw:
            score = DRAW
        else:
            # 'home advantage policy'
            score = WIN
        duel._Match__set_result(result=score)


class ScoreProb:
    @typechecked
    def __init__(self, scores: List[Score], func: Callable[[Duel], Score]):
        """General Purpose Solver

        A ScoreProb

        Parameters
        ----------
        scores : List[Score]
            A list of possible match outcomes.
        func : Callable[[Duel], Score]
            A function taking as input a Duel and producing Score probabilities
        """
        self.scores = scores
        self.probabilities = func

    # ??? can we simply use generic typing, is the code general enough to work for arbitrary SMatch and not just Duel
    # BUG: incompatible func typing in __init__ and .solve() usage -> write a bunch of test
    # FIXME: Should the doc match __init__ signature or the .solve usage ...

    @typechecked
    def solve(self, duel: Duel, *args, **kwars) -> None:
        score = random.choices(population=self.scores,
                               # !!! THE F* is going on here, func should return a Score
                               weights=self.probabilities(duel),
                               k=1)[0]
        duel._Match__set_result(score)


class WeightedScore(ScoreProb):
    @typechecked
    def __init__(self, scores: List[Score], weights: List[float]):
        """Weighted Score assignement

        With this Solver, A score is randomly chosed form a list of options based on weighted.

        Parameters
        ----------
        scores : List[Score]
            A list of possible match outcomes.
        weights : List[float]
            The corresponding weight associated to each Score.

        Raises
        ------
        ValueError
            An error is raised when the scores and weights length are not equal.
        """
        if len(scores) != len(weights):
            msg = f"length of scores ({len(scores)}) does not match length of weights ({len(weights)})"
            raise ValueError(msg)
        super().__init__(scores=scores, func=lambda x: weights)


class CoinFlip(WeightedScore):
    def __init__(self):
        """Random Solver

        Behave like a coin flip, a win or a lose is randomly generated with no regards to any Match details.     
        """
        super().__init__(scores=[WIN, LOSE], weights=[0.5, 0.5])


class BradleyTerry(ScoreProb):
    def __init__(self):
        """Bradley-Terry model

        Implements the famous pairwise model comparaison `probabilistic model <https://en.wikipedia.org/wiki/Bradley–Terry_model>`_.

        It is a ScoreProb Solver where the probability function that a player A with level a, beats a player B with level b, is defined as
            P(A win against B) := a/(a + b)
        """
        super().__init__(scores=[WIN, LOSE], func=self.__probabilities)

    def __probabilities(self, duel: Duel) -> List[float]:
        level1 = duel.teams()[0][0].level()
        level2 = duel.teams()[1][0].level()
        prob = uf.bradleyterry(level1, level2)
        return [prob, 1-prob]


class LogSolver(ScoreProb):
    @typechecked
    def __init__(self, base: Optional[float] = None, lc: Optional[float] = None):
        """Elo like Solver

        The LogSolver implements a standard reparametrization of the Bradley-Terry model that matches Elo rating system.
        In practice it is a ScoreProb with a probability function illustrated on `wismuth <https://wismuth.com/elo/calculator.html>`_.
        FOr a player A with level a, and a Player B with level b, it is defined by the logistic function:
        P(A wins against B) = 1/(1+base^( (b-a) / lc))

        Parameters
        ----------
        base : Optional[float], optional
            The base in the logistic function, by default 10
        lc : Optional[float], optional
            The constant in the logistic function, by default 400

        .. note::
            Default constant in the RSTT package ensure that the LogSolver probabilities matches the expected Score by :class:`rstt.ranking.inferer.Elo`.
            Which means that perfectly accurate predictions are possible when combining both in simulation.
        """
        super().__init__(scores=[WIN, LOSE], func=self.__probabilities)
        self.base = base if base is not None else cfg.LOGSOLVER_BASE
        self.lc = lc if lc is not None else cfg.LOGSOLVER_LC

    def __probabilities(self, duel: Duel) -> List[float]:
        level1 = duel.teams()[0][0].level()
        level2 = duel.teams()[1][0].level()
        prob = uf.logistic_elo(
            base=self.base, diff=level1-level2, constant=self.lc)
        return [prob, 1-prob]
