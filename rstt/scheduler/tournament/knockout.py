from typing import List, Dict
from typeguard import typechecked


from rstt.scheduler.tournament.competition import Competition, playersToDuel
from rstt.ranking.ranking import Ranking
from rstt import Duel, BetterWin
from rstt.stypes import Solver

import rstt.utils.matching as um
import rstt.utils.utils as uu

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
    def __init__(self, name: str,
                seeding: Ranking,
                solver: Solver = BetterWin(),
                cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)
        self.players_left = []

    def initialise(self):
        if not uu.power_of_two(len(self.participants)):
            msg = (f'{type(self)} '
                   'needs a power of two as number of participants '
                   '(2,4,8,16,...)'
                   f', given {len(self.participants)}')
            raise ValueError(msg)

        nb_rounds = int(math.log(len(self.participants), 2))
        self.players_left = self.seeding[[i-1 for i in balanced_tree(nb_rounds)]]

    def generate_games(self):
        games = []
        for i in range(0, len(self.players_left)//2):
            p1 = self.players_left[2*i]
            p2 = self.players_left[2*i+1]
            match = Duel(p1, p2)
            games.append(match)
        return games

    def edit(self, games: List[Duel]):
        next = []
        for game in games:
            next.append(game.winner())
            self.standing[game.loser()] = len(self.players_left)
        self.players_left = next

        if len(self.players_left) == 1:
            self.standing[self.players_left[0]] = 1
            finished = True
        else:
            finished = False

        return finished


class DoubleEliminationBracket(Competition):
    def __init__(self, name: str,
                seeding: Ranking,
                solver: Solver = BetterWin,
                # TODO: add policy params
                cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)
        
        self.upper = SingleEliminationBracket(name+'_UpperBracket',
                                              seeding, solver, cashprize=None)
        self.lower = [] # List[Player]
        self.injector = [] # List[List[Player]]

        # NOTE: this is a um.riffle_shuffle for List[Player]
        #self.policy = lambda list1, list2: [e for e1, e2 in zip(list1, list2) for e in [e1, e2]]
        self.policy = um.riffle_shuffle

    def initialise(self):
        # play upper bracket as a 'SEB'
        self.upper.registration(self.participants)
        self.upper.start()
        self.upper.play()
        
        self.lower = [[game.loser() for game in r] for r in self.upper.games(by_rounds=True)]
        self.lower.append(self.upper.top(place=1))

    def generate_games(self):
        # lower bracket games
        if len(self.lower[0]) != len(self.lower[1]):
            
            games = playersToDuel(self.lower.pop(0))
        # injector games
        elif self.injector:
            lower = self.lower.pop(0)
            injector = self.lower.pop(0)
            games = playersToDuel(self.policy(lower, injector))
        return games

    def edit(self, games: List[Duel]):
        self.standing.update({
            game.loser(): len(self.participants)-len(self.standing)
            for game in games})
        self.lower.insert(0, [game.winner() for game in games])

        if not self.lower: # empty when the grand final is played
            self.standing[games[0].winner()] = 1
            self.standing[games[0].loser()] = 2
            finished = True
        else:
            finished = False
        return finished