"""Module for 'kock-out' Competition.

Such tournament do have a strict elimination process and losing participants are quickly cut of the event.
Standing is based on 'how far' the competitors go.
"""

from typing import Callable
from typeguard import typechecked


from . import Competition
from rstt.ranking.ranking import Ranking
from rstt import BetterWin
from rstt.stypes import Solver, SPlayer

from rstt.utils import utils as uu, matching as um, competition as uc

import math


def balanced_tree(rounds):
    matches = [1, 2]
    for round in range(2, rounds+1):
        check_sum = pow(2, round)+1
        new_matches = []
        for i in matches:
            new_matches.append([i, check_sum-i])
        matches = uu.flatten(new_matches)

    return matches


class SingleEliminationBracket(Competition):
    """Single Elimination Bracket or tournament

    One of the most famous and used competition model, specialy in internationl events, 
    Participants are placed in a binary tree where the winner of a confrontation advance to the next stage and the loser is eliminated.

    More detail on the `single-elimination-bracket <https://en.wikipedia.org/wiki/Single-elimination_tournament>`_  wikipedia page.

    .. note::
        Currently the first round matching is the standard policy. for example with 8 participants:
        Seed1 versus Seed8; Seed4 versus Seed5; Seed2 versus Seed7; Seed3 versus Seed6.

        Future version will support custom first round matching.
        In the mean time, to fine tune the first round, it is possible to reorder a ranking with a permutation using the :func:`rstt.ranking.ranking.Ranking.rerank` method.
        This needs to be called on a ranking before passing it to a competition.
    """
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),
                 cashprize: dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

    # --- override --- #
    def _initialise(self):
        msg = (f'{type(self)} '
               'needs a power of two as number of participants '
               '(2,4,8,16,...)'
               f', given {len(self.participants())}')
        assert uu.power_of_two(len(self.participants())), msg

        nb_rounds = int(math.log(len(self.participants()), 2))
        self.players_left = self.seeding[[
            i-1 for i in balanced_tree(nb_rounds)]]

    def generate_games(self):
        return uc.playersToDuel(self.players_left)

    def _end_of_stage(self) -> bool:
        return True if len(self.players_left) == 1 else False

    def _update(self):
        next = [game.winner() for game in self.played_matches[-1]]
        self.players_left = next

    def _standing(self) -> dict[SPlayer, int]:
        standing = {}
        top = len(self.participants())
        for round in self.played_matches:
            for game in round:
                standing[game.loser()] = top
            top = len(self.participants()) - len(standing)

        # winner
        standing[self.played_matches[-1][0].winner()] = 1
        return standing


class DoubleEliminationBracket(Competition):
    """Double Elimination Bracket

    `Variation <https://en.wikipedia.org/wiki/Double-elimination_tournament>`_ of the Single Elimination Bracket where participants have a 2nd chance after losing before elimination.
    """
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),
                 lower_policy: Callable[[list[any]], list[any]] = lambda x: x,
                 injector_policy: Callable[[
                     list[any], list[any]], list[any]] = um.riffle_shuffle,
                 cashprize: dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

        self.upper = SingleEliminationBracket(name+'_UpperBracket',
                                              seeding, solver)
        self.lower = []  # List[Player]
        self.lower_policy = lower_policy
        self.injector_policy = injector_policy

    # --- override --- #
    def _initialise(self):
        # NOBUG: do notrun(). Not 'event' in itself -> no upper.trophies() called
        self.upper.registration(self.participants())
        self.upper.start()
        self.upper.play()

        # lower bracket
        self.lower = [[game.loser() for game in r]
                      for r in self.upper.games(by_rounds=True)]
        self.lower += [[self.upper.games(by_rounds=True)[-1][0].winner()]]

    def _update(self):
        self.lower.insert(0, [game.winner()
                          for game in self.played_matches[-1]])

    def _standing(self) -> dict[SPlayer, int]:
        standing = {}
        top = len(self.participants())
        for round in self.played_matches:
            for game in round:
                standing[game.loser()] = top
            top = len(self.participants()) - len(standing)
        # winner
        standing[self.played_matches[-1][0].winner()] = 1
        return standing

    def _end_of_stage(self) -> bool:
        return len(self.lower) == 1

    def generate_games(self):
        if len(self.lower[0]) != len(self.lower[1]):
            # lower bracket games
            games = uc.playersToDuel(self.lower_policy(self.lower.pop(0)))
        else:
            # injector games
            lower = self.lower.pop(0)
            injector = self.lower.pop(0)
            games = uc.playersToDuel(self.injector_policy(lower, injector))
        return games

    @typechecked
    def games(self, by_rounds=False, upper=False, lower=False):
        if upper and lower:
            msg = f"At most one of upper and lower can be True. Received values upper: {upper}, lower: {lower}"
            raise ValueError(msg)
        if upper:
            return self.upper.games(by_rounds)
        elif lower:
            return super().games(by_rounds)
        else:
            games = self.upper.played_matches + self.played_matches
            if by_rounds:
                return games
            else:
                return uu.flatten(games)
