from typing import Dict

from .groups import RoundRobin
from rstt.ranking.ranking import Ranking
from rstt import BetterWin
from rstt.stypes import Solver

import random

class RandomRound(RoundRobin):
    def __init__(self, name: str, seeding: Ranking, solver: Solver=BetterWin(), cashprize: Dict[int, float]={}, rounds: int=1, amount: int=1):
        super().__init__(name, seeding, solver, cashprize)
        self.nb_rounds = rounds
        self.nb_duel= amount

    def _init_future_rounds(self):
        participants = [p for p in self.participants]
        for _ in range(self.nb_rounds):
            random.shuffle(participants)
            new_round = participants[:self.nb_duel*2]
            
        self.future_rounds.append(new_round)
