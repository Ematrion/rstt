from typing import List, Dict, Callable, Any
from typeguard import typechecked


from . import Competition
from rstt.ranking.ranking import Ranking
from rstt import Player, BetterWin
from rstt.stypes import Solver

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
    @typechecked
    def __init__(self, name: str,
                seeding: Ranking,
                solver: Solver = BetterWin(),
                cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

    # --- override --- #
    def _initialise(self):
        msg = (f'{type(self)} '
                'needs a power of two as number of participants '
                '(2,4,8,16,...)'
                f', given {len(self.participants)}')
        assert uu.power_of_two(len(self.participants)), msg

        nb_rounds = int(math.log(len(self.participants), 2))
        self.players_left = self.seeding[[i-1 for i in balanced_tree(nb_rounds)]]

    def generate_games(self):
        return uc.playersToDuel(self.players_left)
    
    def _end_of_stage(self) -> bool:
        return True if len(self.players_left) == 1 else False
    
    def _update(self):
        next = [game.winner() for game in self.played_matches[-1]]
        self.players_left = next
    
    def _standing(self) -> Dict[Player, int]:
        standing = {}
        top = len(self.participants)
        for round in self.played_matches:
            for game in round:
                standing[game.loser()] = top
            top = len(self.participants) - len(standing)
        
        # winner
        standing[self.played_matches[-1][0].winner()] = 1
        return standing


class DoubleEliminationBracket(Competition):
    @typechecked
    def __init__(self, name: str,
                seeding: Ranking,
                solver: Solver = BetterWin(),
                lower_policy: Callable[[List[Any]], List[Any]]=lambda x: x ,
                injector_policy: Callable[[List[Any], List[Any]], List[Any]]=um.riffle_shuffle,
                cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)
        
        self.upper = SingleEliminationBracket(name+'_UpperBracket',
                                              seeding, solver)
        self.lower = [] # List[Player]
        self.lower_policy = lower_policy
        self.injector_policy = injector_policy

    # --- override --- #
    def _initialise(self):
        # NOBUG: do notrun(). Not 'event' in itself -> no upper.trophies() called
        self.upper.registration(self.participants)
        self.upper.start()
        self.upper.play()
        
        # lower bracket
        self.lower = [[game.loser() for game in r] for r in self.upper.games(by_rounds=True)]
        self.lower += [[self.upper.games(by_rounds=True)[-1][0].winner()]]

    def _update(self):
        self.lower.insert(0, [game.winner() for game in self.played_matches[-1]])
    
    def _standing(self) -> Dict[uc.Player, int]:
        standing = {}
        top = len(self.participants)
        for round in self.played_matches:
            for game in round:
                standing[game.loser()] = top
            top = len(self.participants) - len(standing)
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
