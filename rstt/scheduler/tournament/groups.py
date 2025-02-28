from typing import List, Dict
from typeguard import typechecked

from rstt import Duel, BetterWin
from . import Competition
from rstt.ranking.ranking import Ranking
from rstt.stypes import Solver
from rstt.solver.solvers import WIN, LOSE, DRAW

from rstt.utils import utils as uu, matching as um, competition as uc

import numpy as np
import math

class RoundRobin(Competition):
    def __init__(self, name: str, seeding: Ranking, solver: Solver = BetterWin,
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
            self.table[p1][p2] += game.score(p1)
            self.table[p2][p1] += game.score(p2)
 
    def _standing(self):
        groups = []
        scores = np.sum(self.table, axis=0)
        values = np.unique(scores)
        for value in values:
            index = np.where(scores == value)[0].tolist()
            groups.append(self.seeding[index])
        
        top = 0
        for group in groups:
            top += len(group)
            self.standing.update({player: top for player in group})
        
    def generate_games(self):
        return self.next_round()
        
    # --- init stuff --- #
    def _init_table(self):
        self.table = np.zeros(shape=(len(self.participants), len(self.participants)))
    
    def _init_future_rounds(self):
        self.future_rounds = um.ruban([p for p in self.seeding if p in self.participants])

    # --- round mechanisme --- #
    def next_round(self):
        # FIXME: seems unecessary -> this code in generate_games(self)
        games = uc.playersToDuel(self.future_rounds.pop(0))
        return games


class SwissRound(RoundRobin):
    def _init_future_rounds(self):
        self.future_rounds = [[player for player in self.seeding]]

    # --- Override --- #
    def _end_of_stage(self):
        return len(self.played_matches) == int(math.log(len(self.participants), 2))
    
    def _update(self):
        # !!! not how _end_of_stage() is meant to be used.
        if not self._end_of_stage():
            self.make_groups()

    def next_round(self):
        games = [uc.find_valid_draw(draws=self.draws(group)) for group in self.future_rounds]
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
    