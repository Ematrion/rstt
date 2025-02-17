from typing import Union, List, Set, Dict, Optional
from typeguard import typechecked
import abc

from rstt import Player, Duel, BetterWin
from rstt.stypes import Solver, Achievement
from rstt.ranking.ranking import Ranking
import rstt.utils.utils as uu

from collections import defaultdict


def playersToDuel(players: List[Player]) -> List[Duel]:
    return [Duel(players[2*i], players[2*i+1]) for i in range(len(players)//2)]    


class Competition(metaclass=abc.ABCMeta):
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver=BetterWin(),
                 cashprize: Optional[Dict[int, float]]=None):
        # a name
        self.name = name
        
        # 'settings'
        self.participants = []
        self.seeding = seeding
        self.solver = solver
        self.cashprize = defaultdict(lambda: 0)
        if cashprize:
            self.cashprize.update(cashprize)
        
        # result related variable
        self.played_matches = []
        self.standing = {}
        
        # control variable
        self.__started = False
        self.__finished = False
        self.__closed = False

    # --- getter --- #
    def started(self):
        return self.__started
    
    def live(self):
        return self.__started and not self.__finished
    
    def over(self):
        return self.__closed
    
    def games(self, by_rounds=False):
        return self.played_matches if by_rounds else uu.flatten(self.played_matches)
    
    def top(self, place: Optional[int]=None) -> Union[Dict[int, List[Player]], List[Player]]:
        if place:
            return [key for key, value in self.standing.items() if value == place]
        else:
            return {v: [key for key, value in self.standing.items() if value == place] for v in self.standing.values()}

    @typechecked
    def registration(self, players: Union[Player, List[Player], Set[Player]]):
        if not self.__started:
            playerset = set(self.participants)
            playerset.update(players)
            self.participants = list(playerset)

    def run(self):
        if not self.__started:
            self.start()
            self.play()
            self.trophies()

    def start(self):
        if not self.__started:
            self.seeding = self.seeding.fit(self.participants)
            self.initialise()
            self.__started = True

    def play(self):
        while not self.__finished:
            current_round = self.generate_games()
            results = self.play_games(current_round)
            self.__finished = self.edit(results)

    @typechecked
    def play_games(self, games: List[Duel]):
        played = []
        for game in games:
            self.solver.solve(game)
            played.append(game)
        self.played_matches.append(played)
        return played

    def trophies(self):
        for player in self.participants:
            try: 
                result = Achievement(self.name, self.standing[player], self.cashprize[self.standing[player]])
                player.collect(result)
            except AttributeError:
                continue
        self.__closed= True

    def initialise(self):
        pass

    @abc.abstractmethod
    def generate_games(self):
        pass

    @abc.abstractmethod
    def edit(self, games: List[Duel]):
        return True
    