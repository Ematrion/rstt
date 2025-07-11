"""Module for Competiton that takes the form of 'groups'

Such tournament do not have a direct elimination process, but allows participants to keep playing even after loses.
Groups usually have tables that track points to determine each participant achievements.
"""

from typing import Dict

from rstt import BetterWin
from . import Competition
from rstt.ranking.ranking import Ranking
from rstt.stypes import Solver

from rstt.utils import utils as uu, matching as um, competition as uc

import numpy as np
import math


class RoundRobin(Competition):
    """Round-Robin Tournament

    Implements the famous tournament system. The matching technique used to generate matches is
    the 'circle' algorithm illustrated `here <https://en.wikipedia.org/wiki/Round-robin_tournament#/media/File:Round-robin_tournament_10teams_en.png>`_.

    A simpl specification of the tournament reads like this:
        - a total of n x (n-1) matche is played in n-1 rounds.
        - each rounds every participants play exactly one opponent.
        - every players faces each others exactly once
        - standing is based on the player's matches scores.
    """

    def __init__(self, name: str, seeding: Ranking, solver: Solver = BetterWin(),
                 cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

        self.table = None
        self.future_rounds = []

    # --- Override --- #
    def _initialise(self):
        self._init_table()
        self._init_future_rounds()

    def _end_of_stage(self):
        return not self.future_rounds

    def _update(self):
        for game in self.played_matches[-1]:
            p1, p2 = game.player1(), game.player2()
            s1, s2 = self.seeding[[p1, p2]]
            self.table[s1][s2] += game.score(p1)
            self.table[s2][s1] += game.score(p2)

    def _standing(self):
        standing = {}
        groups = []

        scores = np.sum(self.table, axis=0)
        values = np.unique(scores)
        for value in values:
            index = np.where(scores == value)[0].tolist()
            groups.append(self.seeding[index])

        top = 0
        for group in groups:
            top += len(group)
            standing.update({player: top for player in group})

        return standing

    def generate_games(self):
        return self.next_round()

    # --- init stuff --- #
    def _init_table(self):
        self.table = np.zeros(
            shape=(len(self.participants()), len(self.participants())))

    def _init_future_rounds(self):
        self.future_rounds = um.ruban(
            [p for p in self.seeding if p in self.participants()])

    # --- round mechanisme --- #
    def next_round(self):
        # FIXME: seems unecessary -> this code in generate_games(self)
        games = uc.playersToDuel(self.future_rounds.pop(0))
        return games


class SwissRound(RoundRobin):
    """Swiss Round

    Also known as `Swiss System <https://en.wikipedia.org/wiki/Swiss-system_tournament>`_.

    It is a variation of the Round-Robin system, that fixes some issues:
        - ~ n X log2(n) matches played, which for large n (participants) is significantly faster than round-robin.
        - each rounds every participants play exactly one opponent with the same score. Which creates more interesting and balance game overall.
        - every players should face at most once other players (not always possible).

    .. warning:: 
        - Undefined behaviour when the number of registered player is not a power of 2.
        - The current matching strategy (greedy) has some issues and may lead to errors, this has been observed for number of participants above 256.

    """

    def _init_future_rounds(self):
        self.future_rounds = [[player for player in self.seeding]]

    # --- Override --- #
    def _end_of_stage(self):
        return len(self.played_matches) == int(math.log(len(self.participants()), 2))

    def _update(self):
        super()._update()
        # !!! not how _end_of_stage() is meant to be used.
        if not self._end_of_stage():
            self.make_groups()

    def next_round(self):
        games = [uc.find_valid_draw(draws=self.draws(
            group), games=self.games()) for group in self.future_rounds]
        return uu.flatten(games)

    # --- round mechanisme --- #
    def make_groups(self):
        self.future_rounds = []
        scores = np.sum(self.table, axis=1)
        values = np.unique(scores)
        for value in values:
            # build a round
            index = np.where(scores == value)[0].tolist()
            players = self.seeding[index]
            self.future_rounds.append(players)

    def draws(self, players):
        # FIXME: explore other methods / make it tunable. It could result in bug
        return [uc.playersToDuel(round) for round in um.ruban(players)]
